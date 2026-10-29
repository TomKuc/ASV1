#!/usr/bin/env python3
"""Conservative grid router for KiCad 10 SWIG Python 3.9.

Creates actual tracks/vias, never claims production completeness. In1.Cu is
reserved for GND; only F.Cu, B.Cu and In2.Cu are used for signal tracks.
Run with the Python bundled with KiCad, not the system Python.
"""
from __future__ import annotations

import argparse
import collections
import functools
import heapq
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@functools.lru_cache(maxsize=16)
def plane_candidate_offsets(radius):
    """Cached order is identical to sorting legal (d2, absolute_x, absolute_y)."""
    return tuple(sorted((dx * dx + dy * dy, dx, dy)
                        for dx in range(-radius, radius + 1)
                        for dy in range(-radius, radius + 1)
                        if dx * dx + dy * dy <= radius * radius))


@dataclass
class Settings:
    grid: float = 0.10
    clearance: float = 0.15
    width: float = 0.15
    via_diameter: float = 0.50
    via_drill: float = 0.25
    hole_clearance: float = 0.25
    edge_clearance: float = 0.30
    via_cost: float = 2.0
    max_expansions: int = 180000
    max_seconds: float = 600.0


class Search:
    """Eight-direction A*, with conservative corner checks and through vias."""

    STEPS = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
             (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)),
             (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2)))

    def __init__(self, world, settings):
        self.world = world
        self.settings = settings

    def find(self, starts, goals, net, deadline, layers=None, max_expansions=None):
        allowed = tuple(layers or self.world.layers)
        goals = set(goals)
        starts = [s for s in starts if s[2] in allowed and not self.world.blocked(*s, net)]
        goals = {s for s in goals if s[2] in allowed and not self.world.blocked(*s, net)}
        if not starts or not goals:
            return None, {"reason": "pad_escape_blocked", "expanded": 0}
        gx = [s[0] for s in goals]
        gy = [s[1] for s in goals]
        goal_layers = {s[2] for s in goals}
        bounds = min(gx), max(gx), min(gy), max(gy)

        def heuristic(node):
            dx = max(bounds[0] - node[0], node[0] - bounds[1], 0)
            dy = max(bounds[2] - node[1], node[1] - bounds[3], 0)
            diagonal = min(dx, dy)
            return max(dx, dy) + (math.sqrt(2) - 1) * diagonal + (
                0 if node[2] in goal_layers else self.settings.via_cost / self.settings.grid)

        queue, costs, parents = [], {}, {}
        serial = 0
        for node in starts:
            costs[node] = 0.0
            heapq.heappush(queue, (heuristic(node), serial, 0.0, node))
            serial += 1
        expanded = 0
        limit = max_expansions or self.settings.max_expansions
        while queue:
            _, _, cost, node = heapq.heappop(queue)
            if cost != costs.get(node):
                continue
            if node in goals:
                path = [node]
                while node in parents:
                    node = parents[node]
                    path.append(node)
                return list(reversed(path)), {"reason": "path_found", "expanded": expanded}
            expanded += 1
            if expanded > limit:
                return None, {"reason": "search_expansion_limit", "expanded": expanded}
            if expanded % 256 == 0 and time.monotonic() >= deadline:
                return None, {"reason": "time_limit", "expanded": expanded}
            x, y, layer = node
            neighbors = []
            for dx, dy, step in self.STEPS:
                nx, ny = x + dx, y + dy
                if self.world.blocked(nx, ny, layer, net):
                    continue
                if dx and dy and (self.world.blocked(x + dx, y, layer, net)
                                  or self.world.blocked(x, y + dy, layer, net)):
                    continue
                neighbors.append(((nx, ny, layer), step))
            if len(allowed) > 1 and self.world.via_allowed(x, y, net):
                for other in allowed:
                    if other != layer and not self.world.blocked(x, y, other, net):
                        neighbors.append(((x, y, other), self.settings.via_cost / self.settings.grid))
            for nxt, increment in neighbors:
                new_cost = cost + increment
                if new_cost + 1e-9 < costs.get(nxt, math.inf):
                    costs[nxt] = new_cost
                    parents[nxt] = node
                    heapq.heappush(queue, (new_cost + heuristic(nxt), serial, new_cost, nxt))
                    serial += 1
        return None, {"reason": "no_path", "expanded": expanded}


class World:
    """Native pad/track geometry rasterized with grid-cell safety allowance."""

    def __init__(self, pcbnew, board, settings):
        self.pcbnew, self.board, self.s = pcbnew, board, settings
        self.layers = (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu)
        enabled = board.GetEnabledLayers()
        self.layers = tuple(layer for layer in self.layers if enabled.Contains(layer))
        self.all_copper = tuple(layer for layer in (pcbnew.F_Cu, pcbnew.In1_Cu,
                                                    pcbnew.In2_Cu, pcbnew.B_Cu)
                                if enabled.Contains(layer))
        if board.GetCopperLayerCount() != 4:
            raise ValueError("This router requires exactly four copper layers")
        self.grid = pcbnew.FromMM(settings.grid)
        box = board.GetBoardEdgesBoundingBox()
        self.x0 = math.floor(box.GetLeft() / self.grid) * self.grid
        self.y0 = math.floor(box.GetTop() / self.grid) * self.grid
        self.nx = int(math.ceil((box.GetRight() - self.x0) / self.grid)) + 1
        self.ny = int(math.ceil((box.GetBottom() - self.y0) / self.grid)) + 1
        if self.nx * self.ny > 4000000:
            raise ValueError("Grid exceeds four million cells; check units/outline")
        self.copper = {layer: {} for layer in self.layers}
        self.vias = {}
        self.holes = {}
        self.hole_reuse = {}
        self._hole_count = 0
        self.hole_clearance = max(settings.hole_clearance,
                                  pcbnew.ToMM(board.GetDesignSettings().m_HoleToHoleMin))
        self.hole_copper_clearance = pcbnew.ToMM(board.GetDesignSettings().m_HoleClearance)
        self.pad_via_exclusion = set()
        self.geometry = {layer: [] for layer in self.all_copper}
        self.drill_geometry = {layer: [] for layer in self.all_copper}
        self.rules = {layer: [] for layer in self.layers}
        self.via_rules = []
        self._owners = []  # Keep SWIG native geometry owners alive.
        self._wide_edge_shapes = {}
        self._connectivity_dirty = True
        self._pad_anchor_cache = {}
        self._build_outline()
        self._build_obstacles()

    def point(self, x, y):
        return self.pcbnew.VECTOR2I(int(self.x0 + x * self.grid), int(self.y0 + y * self.grid))

    def cell(self, point):
        return round((point.x - self.x0) / self.grid), round((point.y - self.y0) / self.grid)

    def key(self, x, y):
        return y * self.nx + x

    def _build_outline(self):
        pcbnew = self.pcbnew
        outline = pcbnew.SHAPE_POLY_SET()
        if not self.board.GetBoardPolygonOutlines(outline, False):
            raise ValueError("KiCad cannot construct a closed board outline; routing aborted")
        self._owners.append(outline)
        self.outline = outline
        self.track_inside = bytearray(self.nx * self.ny)
        self.via_inside = bytearray(self.nx * self.ny)
        half_diagonal = self.s.grid / math.sqrt(2)
        for target, radius in ((self.track_inside, self.s.width / 2),
                               (self.via_inside, self.s.via_diameter / 2)):
            inset = pcbnew.SHAPE_POLY_SET(outline)
            inset.Inflate(-pcbnew.FromMM(self.s.edge_clearance + radius + half_diagonal),
                          pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.005))
            for y in range(self.ny):
                for x in range(self.nx):
                    target[self.key(x, y)] = int(inset.Contains(self.point(x, y)))

    def _raster(self, shape, box, margin, target, net, grid_guard=True):
        # Tracks span cell edges; a via/hole is placed exactly at a cell centre
        # and therefore does not need the additional cell-diagonal allowance.
        margin = self.pcbnew.FromMM(margin + (self.s.grid / math.sqrt(2) if grid_guard else 0))
        if not grid_guard:
            margin = max(0, margin - 1)  # An exact minimum gap is permitted.
        xlo = max(0, int(math.floor((box.GetLeft() - margin - self.x0) / self.grid)))
        xhi = min(self.nx - 1, int(math.ceil((box.GetRight() + margin - self.x0) / self.grid)))
        ylo = max(0, int(math.floor((box.GetTop() - margin - self.y0) / self.grid)))
        yhi = min(self.ny - 1, int(math.ceil((box.GetBottom() + margin - self.y0) / self.grid)))
        bit = 1 << max(0, net)
        for y in range(ylo, yhi + 1):
            for x in range(xlo, xhi + 1):
                if shape.Collide(self.point(x, y), margin):
                    k = self.key(x, y)
                    if isinstance(target, set):
                        target.add(k)
                    else:
                        target[k] = target.get(k, 0) | bit

    def add_copper_item(self, item, pad=False):
        self._connectivity_dirty = True
        net = int(item.GetNetCode())
        layers = [layer for layer in self.all_copper if item.IsOnLayer(layer)]
        # Non-plated holes are mechanical obstacles on every copper layer.
        if pad and item.GetAttribute() == self.pcbnew.PAD_ATTRIB_NPTH:
            layers = list(self.all_copper)
            net = 0
        for layer in layers:
            shape = item.GetEffectiveShape(layer)
            box = item.GetBoundingBox(layer) if pad else item.GetBoundingBox()
            self._owners.extend((item, shape))
            self.geometry[layer].append((shape, box, net))
            if layer in self.copper:
                self._raster(shape, box, self.s.clearance + self.s.width / 2,
                             self.copper[layer], net)
            via_margin = max(self.s.clearance + self.s.via_diameter / 2,
                             self.hole_copper_clearance + self.s.via_drill / 2)
            self._raster(shape, box, via_margin, self.vias, net)
            if pad:
                # No open via-in-pad, including same-net pads, in this workflow.
                self._raster(shape, box, 0.05 + self.s.via_diameter / 2,
                             self.pad_via_exclusion, 0)
        is_via = item.Type() == self.pcbnew.PCB_VIA_T
        if is_via or (pad and item.GetDrillSize().x > 0 and item.GetDrillSize().y > 0):
            hole = item.GetEffectiveHoleShape()
            box = hole.BBox()
            self._owners.append(hole)
            self._hole_count += 1
            self._raster(hole, box, self.s.via_drill / 2 + self.hole_clearance,
                         self.holes, self._hole_count, grid_guard=False)
            # Hole-to-copper and copper-to-copper are independent rules.
            # An NPTH has no annulus: a 0.15 mm net-clearance raster alone
            # cannot enforce the loaded 0.25 mm drill-edge clearance.
            for layer in self.all_copper:
                if layer not in layers:
                    continue
                self.drill_geometry[layer].append((hole, box, net))
                if layer in self.copper:
                    self._raster(hole, box, self.hole_copper_clearance + self.s.width / 2,
                                 self.copper[layer], net)
            self._raster(hole, box, self.hole_copper_clearance + self.s.via_diameter / 2,
                         self.vias, net)
            if is_via:
                point = item.GetPosition()
                key = (point.x, point.y, item.GetNetCode())
                self.hole_reuse[key] = self.hole_reuse.get(key, 0) | (1 << self._hole_count)

    def _build_obstacles(self):
        for pad in self.board.GetPads():
            self.add_copper_item(pad, pad=True)
        for track in self.board.Tracks():
            self.add_copper_item(track)
        zones = list(self.board.Zones())
        for footprint in self.board.Footprints():
            zones.extend(footprint.Zones())
        for zone in zones:
            shape = zone.Outline()
            box = shape.BBox()
            self._owners.extend((zone, shape))
            if zone.GetIsRuleArea():
                if zone.GetDoNotAllowVias() and any(zone.IsOnLayer(l) for l in self.all_copper):
                    self._raster(shape, box, self.s.via_diameter / 2, self.vias, 0)
                    self.via_rules.append((shape, box))
                if zone.GetDoNotAllowTracks():
                    for layer in self.layers:
                        if zone.IsOnLayer(layer):
                            self._raster(shape, box, self.s.width / 2, self.copper[layer], 0)
                            self.rules[layer].append((shape, box, 0))
            else:
                # In2.Cu is a mixed power/signal layer: ordinary pours yield
                # antipads during native refill. Preserve every keepout and
                # all real pads/tracks/vias; only ignore the pour polygon here.
                # Existing ordinary pours on F/B remain routing obstacles.
                for layer in self.layers:
                    if layer != self.pcbnew.In2_Cu and zone.IsOnLayer(layer):
                        net = int(zone.GetNetCode())
                        self._raster(shape, box, self.s.clearance + self.s.width / 2,
                                     self.copper[layer], net)
                        self.rules[layer].append((shape, box, net))

    def blocked(self, x, y, layer, net):
        if x < 0 or y < 0 or x >= self.nx or y >= self.ny or layer not in self.copper:
            return True
        k = self.key(x, y)
        return not self.track_inside[k] or bool(self.copper[layer].get(k, 0) & ~(1 << net))

    def via_allowed(self, x, y, net):
        if x < 0 or y < 0 or x >= self.nx or y >= self.ny:
            return False
        k = self.key(x, y)
        point = self.point(x, y)
        reusable_hole = self.hole_reuse.get((point.x, point.y, net), 0)
        return bool(self.via_inside[k] and k not in self.pad_via_exclusion
                    and not (self.vias.get(k, 0) & ~(1 << net))
                    and not (self.holes.get(k, 0) & ~reusable_hole))

    def via_group_allowed(self, positions, net):
        """Also check new through holes against other vias in the same route."""
        positions = list(positions)
        if not all(self.via_allowed(x, y, net) for x, y in positions):
            return False
        minimum = self.s.via_drill + self.hole_clearance
        for i, first in enumerate(positions):
            for second in positions[i + 1:]:
                distance = math.hypot(first[0] - second[0], first[1] - second[1]) * self.s.grid
                if distance < minimum - 1e-9:
                    return False
        return True

    @staticmethod
    def _boxes_overlap(box, a, b, margin):
        return not (max(a.x, b.x) + margin < box.GetLeft()
                    or min(a.x, b.x) - margin > box.GetRight()
                    or max(a.y, b.y) + margin < box.GetTop()
                    or min(a.y, b.y) - margin > box.GetBottom())

    def segment_clear(self, a, b, layer, net, width=None):
        seg = self.pcbnew.SEG(a, b)
        width = self.s.width if width is None else width
        margin = self.pcbnew.FromMM(self.s.clearance + width / 2)
        for shape, box, other in self.geometry[layer] + self.rules.get(layer, []):
            if other != net and self._boxes_overlap(box, a, b, margin):
                if shape.Collide(seg, margin):
                    return False
        hole_margin = self.pcbnew.FromMM(self.hole_copper_clearance + width / 2)
        for hole, box, other in self.drill_geometry[layer]:
            if other != net and self._boxes_overlap(box, a, b, hole_margin):
                if hole.Collide(seg, hole_margin):
                    return False
        if width > self.s.width + 1e-9:
            # Widening must retain copper-edge clearance too. Dense samples and
            # an extra sample-step inset conservatively cover rounded corners.
            step = self.s.grid / 2
            if width not in self._wide_edge_shapes:
                inset = self.pcbnew.SHAPE_POLY_SET(self.outline)
                inset.Inflate(-self.pcbnew.FromMM(self.s.edge_clearance + width / 2 + step),
                              self.pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS,
                              self.pcbnew.FromMM(0.005))
                self._wide_edge_shapes[width] = inset
            inset = self._wide_edge_shapes[width]
            length = self.pcbnew.ToMM(round(math.hypot(b.x - a.x, b.y - a.y)))
            count = max(1, int(math.ceil(length / step)))
            for i in range(count + 1):
                point = self.pcbnew.VECTOR2I(round(a.x + (b.x - a.x) * i / count),
                                            round(a.y + (b.y - a.y) * i / count))
                if not inset.Contains(point):
                    return False
        return True

    def refresh_connectivity(self):
        if self._connectivity_dirty:
            self.board.BuildConnectivity()
            self._connectivity_dirty = False
            self._pad_anchor_cache.clear()

    def connected_items(self, pad):
        self.refresh_connectivity()
        return self.board.GetConnectivity().GetConnectedItems(pad)

    def pad_anchors(self, pad):
        """Map grid nodes to actual pads or natively connected fanout vias.

        A via anchor is already connected to the pad by real copper. No new
        pad-centre-to-via shortcut may be inferred from that relationship.
        """
        self.refresh_connectivity()
        key = str(pad.m_Uuid.AsString())
        if key in self._pad_anchor_cache:
            return self._pad_anchor_cache[key]
        x, y = self.cell(pad.GetPosition())
        anchors = {}
        # A nearby grid node must still lie in the actual pad, avoiding an
        # unverified diagonal "escape" from the centre of a narrow pad.
        for layer in self.layers:
            if not pad.IsOnLayer(layer):
                continue
            shape = pad.GetEffectiveShape(layer)
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                point = self.point(x + dx, y + dy)
                if shape.Collide(point, 0) and self.segment_clear(pad.GetPosition(), point,
                                                                layer, pad.GetNetCode()):
                    anchors[(x + dx, y + dy, layer)] = {"kind": "pad"}
        for item in self.connected_items(pad):
            if item.Type() != self.pcbnew.PCB_VIA_T or item.GetNetCode() != pad.GetNetCode():
                continue
            via = self.pcbnew.Cast_to_PCB_VIA(item)
            vx, vy = self.cell(via.GetPosition())
            for layer in self.layers:
                if not via.IsOnLayer(layer):
                    continue
                shape = via.GetEffectiveShape(layer)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        node = (vx + dx, vy + dy, layer)
                        if shape.Collide(self.point(*node[:2]), 0):
                            anchors[node] = {"kind": "connected_via",
                                             "via_uuid": str(via.m_Uuid.AsString()),
                                             "via_xy_nm": [via.GetPosition().x, via.GetPosition().y]}
        self._pad_anchor_cache[key] = anchors
        return anchors

    def pad_nodes(self, pad):
        return list(self.pad_anchors(pad))


class Router:
    def __init__(self, pcbnew, board, settings, plane_nets, net_filter,
                 preferred_widths=None, neckdown_length=0.50):
        self.pcbnew, self.board, self.s = pcbnew, board, settings
        self.world = World(pcbnew, board, settings)
        self.search = Search(self.world, settings)
        self.plane_nets = set(plane_nets)
        self.net_filter = set(net_filter)
        self.preferred_widths = preferred_widths or {"VBUS": 0.30, "VSYS": 0.30, "VBAT": 0.30}
        self.neckdown_length = neckdown_length
        self.deadline = time.monotonic() + settings.max_seconds
        self.existing_vias = {(track.GetPosition().x, track.GetPosition().y, track.GetNetCode())
                              for track in board.Tracks() if track.Type() == pcbnew.PCB_VIA_T}
        self.stats = {"status": "PARTIAL_REQUIRES_KICAD_DRC_AND_REVIEW",
                      "kicad_version": pcbnew.GetBuildVersion(),
                      "settings_mm": dict(vars(settings)),
                      "routing_layers": [board.GetLayerName(l) for l in self.world.layers],
                      "reserved_plane_layer": board.GetLayerName(pcbnew.In1_Cu),
                      "tracks_added": 0, "vias_added": 0, "connections": [],
                      "preferred_widths_mm": self.preferred_widths,
                      "connected_via_anchor_uses": [],
                      "new_via_tenting": "front_and_back",
                      "neckdown_length_mm": neckdown_length,
                      "power_width_fallbacks": [], "track_length_by_net_and_width_mm": {},
                      "plane_stubs": [], "warnings": [
                          "No impedance, differential-pair, RF, timing or mechanical qualification.",
                          "GND/other plane stubs require real zones and zone fill before connectivity/DRC.",
                          "Grid router is conservative and incomplete; use KiCad DRC as authority."]}
        design = board.GetDesignSettings()
        constraints = {"track_width": int(design.m_TrackMinWidth),
                       "via_diameter": int(design.m_ViasMinSize),
                       "via_drill": int(design.m_MinThroughDrill),
                       "clearance": int(design.m_MinClearance),
                       "edge_clearance": int(design.m_CopperEdgeClearance)}
        self.stats["board_minimums_mm"] = {key: pcbnew.ToMM(value)
                                            for key, value in constraints.items()}
        actual = {"track_width": settings.width, "via_diameter": settings.via_diameter,
                  "via_drill": settings.via_drill, "clearance": settings.clearance,
                  "edge_clearance": settings.edge_clearance}
        for key, value in actual.items():
            if pcbnew.FromMM(value) < constraints[key]:
                self.stats["warnings"].append("Requested " + key + " is below the loaded board minimum; DRC will fail")
        self.stats["net_filter"] = sorted(self.net_filter)
        self.stats["effective_hole_to_hole_mm"] = self.world.hole_clearance
        self.stats["loaded_hole_to_copper_mm"] = self.world.hole_copper_clearance

    def _add_track(self, a, b, layer, net, width=None):
        if a == b:
            return
        width = self.s.width if width is None else width
        track = self.pcbnew.PCB_TRACK(self.board)
        track.SetStart(a)
        track.SetEnd(b)
        track.SetLayer(layer)
        track.SetWidth(self.pcbnew.FromMM(width))
        track.SetNetCode(net)
        self.board.Add(track)
        self.world.add_copper_item(track)
        self.stats["tracks_added"] += 1
        name = self.board.FindNet(net).GetNetname()
        widths = self.stats["track_length_by_net_and_width_mm"].setdefault(name, {})
        width_key = format(width, ".3f")
        widths[width_key] = widths.get(width_key, 0) + math.hypot(b.x - a.x, b.y - a.y) / 1000000

    def _add_via(self, x, y, net):
        point = self.world.point(x, y)
        key = (point.x, point.y, net)
        if key in self.existing_vias:
            return
        if not self.world.via_allowed(x, y, net):
            raise ValueError("Refusing via placement violating geometry or drill-to-drill spacing")
        via = self.pcbnew.PCB_VIA(self.board)
        via.SetPosition(point)
        via.SetViaType(self.pcbnew.VIATYPE_THROUGH)
        via.SetLayerPair(self.pcbnew.F_Cu, self.pcbnew.B_Cu)
        via.SetWidth(self.pcbnew.FromMM(self.s.via_diameter))
        via.SetDrill(self.pcbnew.FromMM(self.s.via_drill))
        via.SetNetCode(net)
        via.SetFrontTentingMode(self.pcbnew.TENTING_MODE_TENTED)
        via.SetBackTentingMode(self.pcbnew.TENTING_MODE_TENTED)
        self.board.Add(via)
        self.world.add_copper_item(via)
        self.existing_vias.add(key)
        self.stats["vias_added"] += 1

    @staticmethod
    def pad_id(pad):
        return pad.GetParentFootprint().GetReference() + "." + pad.GetNumber()

    @staticmethod
    def _compact(path):
        if len(path) < 3:
            return path
        result = [path[0]]
        last_delta = tuple(b - a for a, b in zip(path[0], path[1]))
        for i in range(1, len(path) - 1):
            delta = tuple(b - a for a, b in zip(path[i], path[i + 1]))
            if delta != last_delta:
                result.append(path[i])
            last_delta = delta
        result.append(path[-1])
        return result

    def commit(self, path, net, first_pad, last_pad=None):
        path = self._compact(path)
        segments = []
        first_anchor = self.world.pad_anchors(first_pad).get(path[0])
        last_anchor = self.world.pad_anchors(last_pad).get(path[-1]) if last_pad is not None else None
        if first_anchor is None or (last_pad is not None and last_anchor is None):
            return False
        first = self.world.point(*path[0][:2])
        if first_anchor["kind"] == "pad":
            segments.append((first_pad.GetPosition(), first, path[0][2]))
        for a, b in zip(path, path[1:]):
            if a[2] == b[2]:
                segments.append((self.world.point(*a[:2]), self.world.point(*b[:2]), a[2]))
        if last_pad is not None and last_anchor["kind"] == "pad":
            segments.append((self.world.point(*path[-1][:2]), last_pad.GetPosition(), path[-1][2]))
        if not all(self.world.segment_clear(a, b, layer, net) for a, b, layer in segments):
            return False
        transitions = {a[:2] for a, b in zip(path, path[1:]) if a[2] != b[2]}
        if not self.world.via_group_allowed(transitions, net):
            return False
        for a, b, layer, width in self._preferred_segments(
                segments, net, first_pad, last_pad,
                first_is_pad=first_anchor["kind"] == "pad",
                last_is_pad=last_anchor is not None and last_anchor["kind"] == "pad"):
            self._add_track(a, b, layer, net, width)
        for x, y in transitions:
            self._add_via(x, y, net)
        for pad, node, anchor in ((first_pad, path[0], first_anchor),
                                  (last_pad, path[-1], last_anchor)):
            if anchor is not None and anchor["kind"] == "connected_via":
                self.stats["connected_via_anchor_uses"].append({
                    "pad": self.pad_id(pad), "layer": self.board.GetLayerName(node[2]),
                    "grid_node": list(node), **anchor})
        return True

    def _preferred_segments(self, segments, net, first_pad, last_pad,
                            first_is_pad=True, last_is_pad=True):
        """Prefer wider power traces, retaining explicit fine-pad neckdowns."""
        name = self.board.FindNet(net).GetNetname()
        preferred = max(self.s.width, self.preferred_widths.get(name, self.s.width))
        if preferred <= self.s.width + 1e-9:
            return [(a, b, layer, self.s.width) for a, b, layer in segments]
        segments = [(a, b, layer) for a, b, layer in segments if a != b]
        if not segments:
            return []
        distances = [math.hypot(b.x - a.x, b.y - a.y) / 1000000 for a, b, _ in segments]
        total = sum(distances)
        first_size = first_pad.GetSize(segments[0][2])
        start_neck = self.neckdown_length if first_is_pad and min(first_size.x, first_size.y) < self.pcbnew.FromMM(preferred) else 0
        end_neck = 0
        if last_pad is not None and last_is_pad:
            last_size = last_pad.GetSize(segments[-1][2])
            if min(last_size.x, last_size.y) < self.pcbnew.FromMM(preferred):
                end_neck = self.neckdown_length
        boundaries = sorted({max(0, min(total, value)) for value in (start_neck, total - end_neck)})
        result, travelled = [], 0.0
        for (a, b, layer), length in zip(segments, distances):
            cuts = [travelled] + [cut for cut in boundaries if travelled + 1e-9 < cut < travelled + length - 1e-9] + [travelled + length]
            for begin, end in zip(cuts, cuts[1:]):
                pa = self.pcbnew.VECTOR2I(round(a.x + (b.x - a.x) * (begin - travelled) / length),
                                         round(a.y + (b.y - a.y) * (begin - travelled) / length))
                pb = self.pcbnew.VECTOR2I(round(a.x + (b.x - a.x) * (end - travelled) / length),
                                         round(a.y + (b.y - a.y) * (end - travelled) / length))
                middle = (begin + end) / 2
                width = self.s.width if middle < start_neck or middle > total - end_neck else preferred
                if width > self.s.width and not self.world.segment_clear(pa, pb, layer, net, width):
                    self.stats["power_width_fallbacks"].append({
                        "net": name, "layer": self.board.GetLayerName(layer),
                        "length_mm": end - begin, "preferred_width_mm": preferred,
                        "actual_width_mm": self.s.width,
                        "reason": "widening_geometry_or_edge_clearance_blocked"})
                    width = self.s.width
                result.append((pa, pb, layer, width))
            travelled += length
        return result

    def route_plane_pad(self, pad):
        net, name = int(pad.GetNetCode()), pad.GetNetname()
        record = {"net": name, "pad": self.pad_id(pad), "plane_fill_required": True}
        if pad.GetAttribute() == self.pcbnew.PAD_ATTRIB_PTH:
            record["result"] = "plated_pad_can_contact_plane"
            return record
        connected = self.world.connected_items(pad)
        if any(item.Type() == self.pcbnew.PCB_VIA_T for item in connected):
            record["result"] = "existing_connected_via_can_contact_plane"
            return record
        if time.monotonic() >= self.deadline:
            record.update(result="UNROUTED_plane_stub", reason="time_limit")
            return record
        starts = self.world.pad_nodes(pad)
        x, y = self.world.cell(pad.GetPosition())
        candidates = []
        radius = int(math.ceil(3.0 / self.s.grid))
        for d2, dx, dy in plane_candidate_offsets(radius):
            if self.world.via_allowed(x + dx, y + dy, net):
                candidates.append((d2, x + dx, y + dy))
                if len(candidates) == 24:
                    break
        for _, gx, gy in candidates:
            for layer in sorted({node[2] for node in starts}):
                path, search = self.search.find(starts, [(gx, gy, layer)], net, self.deadline,
                                                layers=(layer,), max_expansions=10000)
                if path and self.commit(path, net, pad):
                    self._add_via(gx, gy, net)
                    record.update(result="stub_and_via_added", via_xy_mm=[
                        self.pcbnew.ToMM(self.world.point(gx, gy).x),
                        self.pcbnew.ToMM(self.world.point(gx, gy).y)])
                    return record
                if time.monotonic() >= self.deadline:
                    break
            if time.monotonic() >= self.deadline:
                break
        record["result"] = "UNROUTED_plane_stub"
        return record

    def _pad_components(self, pads):
        """Use KiCad connectivity, preserving connected groups on reruns."""
        self.world.refresh_connectivity()
        conn = self.board.GetConnectivity()
        groups = []
        remaining = {str(p.m_Uuid.AsString()): p for p in pads}
        while remaining:
            key, seed = remaining.popitem()
            group = [seed]
            linked = {str(item.m_Uuid.AsString()) for item in conn.GetConnectedItems(seed)}
            for other in list(remaining):
                if other in linked:
                    group.append(remaining.pop(other))
            groups.append(group)
        return groups

    def route_net(self, pads):
        groups = self._pad_components(pads)
        net, name = int(pads[0].GetNetCode()), pads[0].GetNetname()
        failed = set()
        while len(groups) > 1:
            choices = []
            for i, first in enumerate(groups):
                for j in range(i + 1, len(groups)):
                    for a in first:
                        for b in groups[j]:
                            pair = tuple(sorted((self.pad_id(a), self.pad_id(b))))
                            if pair not in failed:
                                pa, pb = a.GetPosition(), b.GetPosition()
                                choices.append(((pa.x - pb.x) ** 2 + (pa.y - pb.y) ** 2,
                                                i, j, a, b, pair))
            if not choices:
                break
            _, i, j, a, b, pair = min(choices, key=lambda value: value[0])
            if time.monotonic() >= self.deadline:
                path, info = None, {"reason": "time_limit", "expanded": 0}
            else:
                path, info = self.search.find(self.world.pad_nodes(a), self.world.pad_nodes(b),
                                              net, self.deadline)
            success = bool(path and self.commit(path, net, a, b))
            record = {"net": name, "from": self.pad_id(a), "to": self.pad_id(b), **info,
                      "result": "tracks_added" if success else "UNROUTED"}
            if path and not success:
                record["reason"] = "native_geometry_validation_failed"
            self.stats["connections"].append(record)
            if success:
                groups[i].extend(groups[j])
                del groups[j]
            else:
                failed.add(pair)
            print(name + " " + record["from"] + " -> " + record["to"] + ": " + record["result"],
                  file=sys.stderr, flush=True)
            if record["reason"] == "time_limit":
                break
        return [[self.pad_id(p) for p in group] for group in groups]

    def run(self):
        nets = collections.defaultdict(list)
        for pad in self.board.GetPads():
            if pad.GetNetCode() > 0 and pad.GetNumber():
                if not self.net_filter or pad.GetNetname() in self.net_filter:
                    nets[pad.GetNetname()].append(pad)
        self.world.refresh_connectivity()
        self.stats["native_unconnected_before"] = self.board.GetConnectivity().GetUnconnectedCount(False)
        # Route critical fine-pitch signals before adding plane stubs, then all others.
        def priority(item):
            name, pads = item
            critical = 0 if name.startswith("USB_D") else 1 if name.startswith(("QSPI", "FLASH", "IMU")) else 2
            return critical, len(pads), name

        remaining = {}
        for name, pads in sorted(nets.items(), key=priority):
            if name not in self.plane_nets and len(pads) > 1:
                remaining[name] = self.route_net(pads)
        for name in sorted(self.plane_nets):
            for pad in nets.get(name, []):
                self.stats["plane_stubs"].append(self.route_plane_pad(pad))
        self.world.refresh_connectivity()
        self.stats["native_unconnected_after_before_zone_refill"] = self.board.GetConnectivity().GetUnconnectedCount(False)
        self.stats["remaining_signal_components"] = {name: groups for name, groups in remaining.items()
                                                       if len(groups) > 1}
        self.stats["unrouted_plane_pads"] = [r for r in self.stats["plane_stubs"]
                                               if r["result"].startswith("UNROUTED")]
        self.stats["plane_zone_presence"] = {name: any(z.GetNetname() == name and not z.GetIsRuleArea()
                                                       for z in self.board.Zones()) for name in self.plane_nets}
        return self.stats


def self_test():
    """Pure routing tests: barrier, layer transition, diagonal clearance, timeout."""
    class FakeWorld:
        layers = (0, 2, 6)

        def __init__(self, block=None, via=True):
            self.block = block or set()
            self.via = via

        def blocked(self, x, y, layer, net):
            return x < 0 or y < 0 or x >= 12 or y >= 12 or (x, y, layer) in self.block

        def via_allowed(self, x, y, net):
            return self.via and 1 <= x <= 10 and 1 <= y <= 10

    settings = Settings()
    deadline = time.monotonic() + 5
    wall = {(5, y, 0) for y in range(12)}
    path, _ = Search(FakeWorld(wall), settings).find([(1, 1, 0)], [(10, 10, 0)], 1, deadline)
    assert path and any(p[2] != 0 for p in path)
    path, _ = Search(FakeWorld(wall, via=False), settings).find([(1, 1, 0)], [(10, 10, 0)], 1, deadline)
    assert path is None
    obstacles = {(1, 0, 0), (0, 1, 0)}
    path, _ = Search(FakeWorld(obstacles, via=False), settings).find([(0, 0, 0)], [(1, 1, 0)], 1, deadline)
    assert path is None
    path, _ = Search(FakeWorld(), settings).find([(1, 1, 0)], [(10, 10, 0)], 1, deadline,
                                                max_expansions=1)
    assert path is None
    compact = Router._compact([(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 0, 2), (2, 1, 2)])
    assert compact == [(0, 0, 0), (2, 0, 0), (2, 0, 2), (2, 1, 2)]
    fake = FakeWorld()
    fake.s, fake.hole_clearance = settings, 0.25
    assert not World.via_group_allowed(fake, [(1, 1), (4, 1)], 1)
    assert World.via_group_allowed(fake, [(1, 1), (6, 1)], 1)
    print("6 routing self-tests passed; no PCB modified; no DRC performed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--stats", type=Path, help="JSON report; default OUTPUT.route.json")
    parser.add_argument("--plane-net", action="append", default=None,
                        help="Add pad-to-plane vias instead of routing a net; default GND")
    parser.add_argument("--net", action="append", default=[], help="Limit changes to named nets")
    parser.add_argument("--grid", type=float, default=0.10)
    parser.add_argument("--clearance", type=float, default=0.15)
    parser.add_argument("--width", type=float, default=0.15)
    parser.add_argument("--via-diameter", type=float, default=0.50)
    parser.add_argument("--via-drill", type=float, default=0.25)
    parser.add_argument("--hole-clearance", type=float, default=0.25,
                        help="Minimum drill-edge to drill-edge gap, including same-net holes")
    parser.add_argument("--preferred-width", action="append", default=[], metavar="NET=MM",
                        help="Override preferred width; defaults VBUS/VSYS/VBAT=0.30 mm")
    parser.add_argument("--neckdown-length", type=float, default=0.50,
                        help="Base-width distance from fine pads before preferred widening")
    parser.add_argument("--edge-clearance", type=float, default=0.30)
    parser.add_argument("--max-seconds", type=float, default=600)
    parser.add_argument("--max-expansions", type=int, default=180000)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.input or not args.output:
        parser.error("input and output paths are required")
    if args.input.resolve() == args.output.resolve():
        parser.error("use a separate output file to preserve the placed input board")
    if not args.input.is_file():
        parser.error("input PCB does not exist")
    if min(args.grid, args.clearance, args.width, args.via_drill,
           args.hole_clearance, args.edge_clearance) <= 0:
        parser.error("geometry values must be positive")
    if args.max_seconds <= 0 or args.max_expansions <= 0:
        parser.error("search limits must be positive")
    if args.neckdown_length < 0:
        parser.error("neckdown length must not be negative")
    preferred_widths = {"VBUS": 0.30, "VSYS": 0.30, "VBAT": 0.30}
    for entry in args.preferred_width:
        try:
            name, value = entry.rsplit("=", 1)
            width = float(value)
            if not name or width < args.width:
                raise ValueError()
            preferred_widths[name] = width
        except ValueError:
            parser.error("preferred width must be NET=MM and at least the base width")
    if args.via_diameter < args.via_drill + 0.20:
        parser.error("via diameter must provide at least 0.10 mm annular ring")
    try:
        import pcbnew
    except ImportError:
        parser.error("run with /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3")
    settings = Settings(grid=args.grid, clearance=args.clearance, width=args.width,
                        via_diameter=args.via_diameter, via_drill=args.via_drill,
                        hole_clearance=args.hole_clearance,
                        edge_clearance=args.edge_clearance, max_seconds=args.max_seconds,
                        max_expansions=args.max_expansions)
    board = pcbnew.LoadBoard(str(args.input.resolve()))
    started = time.monotonic()
    router = Router(pcbnew, board, settings, args.plane_net or ["GND"], args.net,
                    preferred_widths, args.neckdown_length)
    stats = router.run()
    stats.update(input=str(args.input.resolve()), output=str(args.output.resolve()),
                 elapsed_seconds=round(time.monotonic() - started, 3))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not pcbnew.SaveBoard(str(args.output.resolve()), board):
        raise RuntimeError("KiCad failed to save output PCB")
    report = args.stats or args.output.with_suffix(".route.json")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps({key: stats[key] for key in ("status", "tracks_added", "vias_added",
                                                   "native_unconnected_after_before_zone_refill",
                                                   "elapsed_seconds")}))
    print("Report: " + str(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
