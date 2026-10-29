#!/usr/bin/env python3
"""Native KiCad router regression checks using synthetic boards only.

Run with the Python 3.9 bundled with KiCad. Never opens the project PCB.
"""
from __future__ import annotations

import contextlib
import io
import unittest

import pcbnew

from route_pcb import Router, Settings, plane_candidate_offsets


def point(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def board_with_outline():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    for a, b in (((0, 0), (12, 0)), ((12, 0), (12, 8)),
                 ((12, 8), (0, 8)), ((0, 8), (0, 0))):
        edge = pcbnew.PCB_SHAPE()
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(point(*a))
        edge.SetEnd(point(*b))
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetWidth(pcbnew.FromMM(0.05))
        board.Add(edge)
    return board


def add_pad(board, ref, pos, size, net=None):
    footprint = pcbnew.FOOTPRINT(board)
    footprint.SetReference(ref)
    board.Add(footprint)
    pad = pcbnew.PAD(footprint)
    pad.SetNumber("1")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(point(*size))
    pad.SetPosition(point(*pos))
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    pad.SetLayerSet(layers)
    if net is not None:
        pad.SetNet(net)
    footprint.Add(pad)
    return pad


def add_track(board, a, b, net):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(*a))
    track.SetEnd(point(*b))
    track.SetLayer(pcbnew.F_Cu)
    track.SetWidth(pcbnew.FromMM(0.15))
    track.SetNet(net)
    board.Add(track)
    return track


def add_via(board, pos, net):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(*pos))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetWidth(pcbnew.FromMM(0.50))
    via.SetDrill(pcbnew.FromMM(0.25))
    via.SetNet(net)
    board.Add(via)
    return via


class NativeRouterTests(unittest.TestCase):
    def test_connected_dogleg_via_is_anchor_without_pad_shortcut(self):
        board = board_with_outline()
        net = pcbnew.NETINFO_ITEM(board, "TEST")
        board.Add(net)
        source = add_pad(board, "SOURCE", (2.025, 2.025), (0.2, 0.2), net)
        target = add_pad(board, "TARGET", (10, 2), (0.7, 0.7), net)
        # Fine adjacent pads suppress conservative grid escape from SOURCE.
        add_pad(board, "ABOVE", (2.025, 1.625), (0.2, 0.2))
        add_pad(board, "BELOW", (2.025, 2.425), (0.2, 0.2))
        # A direct centre-to-via shortcut would cross this other copper.
        add_pad(board, "DIAGONAL_BLOCK", (3.1, 3), (0.6, 0.6))
        # The only useful route through this wall is on another copper layer.
        add_pad(board, "FRONT_WALL", (6, 4), (0.5, 7.0))
        fanout = [add_track(board, a, b, net) for a, b in (
            ((2.025, 2.025), (2.4, 2.025)), ((2.4, 2.025), (2.4, 4)),
            ((2.4, 4), (4, 4)))]
        original_via = add_via(board, (4, 4), net)
        before = {str(item.m_Uuid.AsString()) for item in board.Tracks()}
        router = Router(pcbnew, board, Settings(max_seconds=10, max_expansions=60000), [], [])
        anchors = router.world.pad_anchors(source)
        free_pad_nodes = [node for node, anchor in anchors.items()
                          if anchor["kind"] == "pad"
                          and not router.world.blocked(*node, net.GetNetCode())]
        self.assertEqual(free_pad_nodes, [])
        self.assertTrue(any(anchor["kind"] == "connected_via" for anchor in anchors.values()))
        self.assertFalse(router.world.segment_clear(source.GetPosition(),
                                                    original_via.GetPosition(),
                                                    pcbnew.F_Cu, net.GetNetCode()))
        with contextlib.redirect_stderr(io.StringIO()):
            stats = router.run()
        self.assertEqual(stats["remaining_signal_components"], {})
        self.assertEqual(stats["native_unconnected_after_before_zone_refill"], 0)
        self.assertTrue(any(use["pad"] == "SOURCE.1" for use in stats["connected_via_anchor_uses"]))
        new_items = [item for item in board.Tracks() if str(item.m_Uuid.AsString()) not in before]
        new_tracks = [item for item in new_items if item.Type() == pcbnew.PCB_TRACE_T]
        self.assertTrue(new_tracks)
        # No new track may go back to the source-pad centre. The actual dogleg
        # remains the only connection from that pad to its existing via.
        for track in new_tracks:
            self.assertNotEqual(track.GetStart(), source.GetPosition())
            self.assertNotEqual(track.GetEnd(), source.GetPosition())
            self.assertNotEqual(track.GetLayer(), pcbnew.In1_Cu)
        new_vias = [pcbnew.Cast_to_PCB_VIA(item) for item in new_items
                    if item.Type() == pcbnew.PCB_VIA_T]
        self.assertTrue(new_vias)
        for via in new_vias:
            self.assertEqual(via.GetFrontTentingMode(), pcbnew.TENTING_MODE_TENTED)
            self.assertEqual(via.GetBackTentingMode(), pcbnew.TENTING_MODE_TENTED)
        self.assertTrue(all(str(item.m_Uuid.AsString()) in before for item in fanout))

    def test_plain_pad_routing_still_connects(self):
        board = board_with_outline()
        net = pcbnew.NETINFO_ITEM(board, "TEST")
        board.Add(net)
        source = add_pad(board, "SOURCE", (2, 2), (0.6, 0.6), net)
        add_pad(board, "TARGET", (8, 5), (0.6, 0.6), net)
        router = Router(pcbnew, board, Settings(max_seconds=5), [], [])
        self.assertTrue(all(anchor["kind"] == "pad"
                            for anchor in router.world.pad_anchors(source).values()))
        with contextlib.redirect_stderr(io.StringIO()):
            stats = router.run()
        self.assertEqual(stats["native_unconnected_after_before_zone_refill"], 0)
        self.assertGreater(stats["tracks_added"], 0)
        self.assertEqual(stats["connected_via_anchor_uses"], [])

    def test_unconnected_same_net_via_is_not_an_anchor(self):
        board = board_with_outline()
        net = pcbnew.NETINFO_ITEM(board, "TEST")
        board.Add(net)
        source = add_pad(board, "SOURCE", (2, 2), (0.6, 0.6), net)
        add_via(board, (8, 5), net)
        router = Router(pcbnew, board, Settings(max_seconds=5), [], [])
        anchors = router.world.pad_anchors(source)
        self.assertTrue(anchors)
        self.assertTrue(all(anchor["kind"] == "pad" for anchor in anchors.values()))

    def test_cached_plane_offsets_preserve_original_candidate_order(self):
        for radius in (2, 7, 30):
            x, y = 19, 31
            legal = lambda dx, dy: (dx * 3 + dy * 5) % 7 not in (0, 1)
            old = sorted((dx * dx + dy * dy, x + dx, y + dy)
                         for dx in range(-radius, radius + 1)
                         for dy in range(-radius, radius + 1)
                         if dx * dx + dy * dy <= radius * radius and legal(dx, dy))[:24]
            new = []
            for d2, dx, dy in plane_candidate_offsets(radius):
                if legal(dx, dy):
                    new.append((d2, x + dx, y + dy))
                    if len(new) == 24:
                        break
            self.assertEqual(old, new)

    def test_npth_uses_loaded_hole_to_copper_clearance(self):
        board = board_with_outline()
        board.GetDesignSettings().m_HoleClearance = pcbnew.FromMM(0.25)
        net = pcbnew.NETINFO_ITEM(board, "TEST")
        board.Add(net)
        add_pad(board, "SOURCE", (2, 4.8), (0.5, 0.5), net)
        add_pad(board, "TARGET", (8, 4.8), (0.5, 0.5), net)
        hole = add_pad(board, "NPTH", (5, 4), (1, 1))
        hole.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        hole.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        hole.SetDrillSize(point(1, 1))
        layers = pcbnew.LSET()
        for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            layers.AddLayer(layer)
        hole.SetLayerSet(layers)
        router = Router(pcbnew, board, Settings(grid=.05, max_seconds=5), [], [])
        world = router.world
        self.assertAlmostEqual(world.hole_copper_clearance, .25)
        # Hole edge y=4.5; 0.15 mm trace at y=4.8 leaves only 0.225 mm.
        self.assertFalse(world.segment_clear(point(2, 4.8), point(8, 4.8),
                                              pcbnew.F_Cu, net.GetNetCode()))
        self.assertFalse(world.segment_clear(point(2, 4.8), point(8, 4.8),
                                              pcbnew.In2_Cu, net.GetNetCode()))
        # y=4.85 leaves 0.275 mm copper-to-hole and is physically legal.
        self.assertTrue(world.segment_clear(point(2, 4.85), point(8, 4.85),
                                             pcbnew.F_Cu, net.GetNetCode()))
        with contextlib.redirect_stderr(io.StringIO()):
            stats = router.run()
        self.assertEqual(stats["native_unconnected_after_before_zone_refill"], 0)
        native_hole = hole.GetEffectiveHoleShape()
        for track in board.Tracks():
            if track.Type() == pcbnew.PCB_TRACE_T:
                self.assertFalse(native_hole.Collide(track.GetEffectiveShape(track.GetLayer()),
                                                     pcbnew.FromMM(.25) - 1))

    def test_in2_ordinary_power_pour_yields_but_keepout_does_not(self):
        board = board_with_outline()
        net = pcbnew.NETINFO_ITEM(board, "TEST")
        power = pcbnew.NETINFO_ITEM(board, "+3V0")
        board.Add(net)
        board.Add(power)
        add_pad(board, "SOURCE", (2, 2), (.5, .5), net)
        add_pad(board, "TARGET", (8, 5), (.5, .5), net)

        def zone(corners, keepout=False):
            item = pcbnew.ZONE(board)
            item.SetLayer(pcbnew.In2_Cu)
            item.SetNet(power)
            item.SetIsRuleArea(keepout)
            if keepout:
                item.SetDoNotAllowTracks(True)
                item.SetDoNotAllowVias(True)
            outline = item.Outline()
            outline.NewOutline()
            for x, y in corners:
                outline.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
            board.Add(item)

        zone(((1, 1), (11, 1), (11, 7), (1, 7)))
        router = Router(pcbnew, board, Settings(max_seconds=5), [], [])
        x, y = router.world.cell(point(6, 4))
        self.assertFalse(router.world.blocked(x, y, pcbnew.In2_Cu, net.GetNetCode()))
        zone(((5, 3), (7, 3), (7, 5), (5, 5)), keepout=True)
        router = Router(pcbnew, board, Settings(max_seconds=5), [], [])
        self.assertTrue(router.world.blocked(x, y, pcbnew.In2_Cu, net.GetNetCode()))
        self.assertFalse(router.world.via_allowed(x, y, net.GetNetCode()))


if __name__ == "__main__":
    unittest.main()
