#!/usr/bin/env python3
"""Read-only native KiCad signal-geometry survey for Ankle Sensor V1.

Run with the Python/pcbnew shipped with KiCad. The script never refills zones,
edits the board or calls SaveBoard. It writes only its requested JSON/Markdown
reports, checking the board hash before publishing either result.

Lengths are sums of trace objects, including branches and overlap with pads.
They are not point-to-point electrical lengths or timing/impedance simulations.
"""

import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

import pcbnew as pcb

import verify_design as sexpr


ROOT = Path(__file__).resolve().parents[1]
METHOD_VERSION = 2
DEFAULT_STEP_MM = 0.05
HOLE_CLASSIFICATION_RADIUS_MM = 0.6
SOURCES = {
    "Nordic_QSPI": "https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/qspi.html",
    "Nordic_CLOCK": "https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/clock.html",
    "ST_IMU": "https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf",
    "Winbond_flash": "https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf",
    "TI_return_paths": "https://www.ti.com/lit/an/scaa082a/scaa082a.pdf",
    "Abracon_ABS07": "https://abracon.com/Resonators/ABS07.pdf",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def mm(value):
    return float(pcb.ToMM(value))


def xy(point):
    return [round(mm(point.x), 6), round(mm(point.y), 6)]


def uid(item):
    return str(item.m_Uuid.AsString())


def file_label(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def bbox_near(box, point, radius=0):
    return (box.GetLeft() - radius <= point.x <= box.GetRight() + radius
            and box.GetTop() - radius <= point.y <= box.GetBottom() + radius)


def is_via(item):
    return item.Type() == pcb.PCB_VIA_T


def connected_pad_component(connectivity, pads):
    """Traverse native connectivity, instead of assuming one-hop adjacency."""
    if not pads:
        return None
    seen, todo = set(), [pads[0]]
    while todo:
        item = todo.pop()
        key = uid(item)
        if key in seen:
            continue
        seen.add(key)
        todo.extend(other for other in connectivity.GetConnectedItems(item)
                    if uid(other) not in seen)
    return all(uid(pad) in seen for pad in pads)


def geometry_fingerprint(traces, vias, pads):
    """Hash geometry, not UUIDs or the serialization order of the PCB file."""
    records = []
    for trace in traces:
        ends = sorted([xy(trace.GetStart()), xy(trace.GetEnd())])
        record = {"kind": trace.GetClass(), "ends_mm": ends,
                  "layer": int(trace.GetLayer()), "width_mm": mm(trace.GetWidth())}
        if trace.Type() != pcb.PCB_TRACE_T:
            arc = pcb.Cast_to_PCB_ARC(trace)
            record["mid_mm"] = xy(arc.GetMid())
        records.append(record)
    for item in vias:
        via = pcb.Cast_to_PCB_VIA(item)
        records.append({"kind": "via", "xy_mm": xy(via.GetPosition()),
                        "diameter_mm": mm(via.GetWidth(pcb.F_Cu)),
                        "drill_mm": mm(via.GetDrillValue()),
                        "via_type": int(via.GetViaType()),
                        "layers": [int(via.TopLayer()), int(via.BottomLayer())]})
    for pad in pads:
        records.append({"kind": "pad", "ref": pad.GetParentFootprint().GetReference(),
                        "number": pad.GetNumber(), "xy_mm": xy(pad.GetPosition()),
                        "size_mm": xy(pad.GetSize()), "shape": int(pad.GetShape()),
                        "rotation_deg": pad.GetOrientation().AsDegrees(),
                        "layers": sorted(int(layer) for layer in pad.GetLayerSet().Seq())})
    canonical = sorted(json.dumps(record, sort_keys=True, separators=(",", ":"))
                       for record in records)
    return sha256("\n".join(canonical).encode())


class ReferenceGeometry:
    """Stored native zone fills and actual pad/via copper, with holes removed."""

    def __init__(self, board, items, pads):
        self.ground_zones = [z for z in board.Zones() if not z.GetIsRuleArea()
                             and z.GetNetname() == "GND" and z.IsOnLayer(pcb.In1_Cu)]
        self.power_zones = [z for z in board.Zones() if not z.GetIsRuleArea()
                            and z.GetNetname() == "+3V0" and z.IsOnLayer(pcb.In2_Cu)]
        self.ground_polys = [z.GetFilledPolysList(pcb.In1_Cu) for z in self.ground_zones]
        self.power_polys = [z.GetFilledPolysList(pcb.In2_Cu) for z in self.power_zones]
        if not any(poly.OutlineCount() for poly in self.ground_polys):
            raise ValueError("Stored In1.Cu GND fill is missing; refill separately before review")
        if not any(poly.OutlineCount() for poly in self.power_polys):
            raise ValueError("Stored In2.Cu +3V0 fill is missing; refill separately before review")
        self.ground_shapes = self.copper_shapes(items + pads, "GND", pcb.In1_Cu)
        self.power_shapes = self.copper_shapes(items + pads, "+3V0", pcb.In2_Cu)
        self.ground_vias = [item for item in items if is_via(item)
                            and item.GetNetname() == "GND"]
        self.holes = []
        for item in items + pads:
            drilled_pad = (isinstance(item, pcb.PAD) and item.GetDrillSize().x > 0
                           and item.GetDrillSize().y > 0)
            if is_via(item) or drilled_pad:
                shape = item.GetEffectiveHoleShape()
                self.holes.append((shape, shape.BBox()))

    @staticmethod
    def copper_shapes(items, net, layer):
        return [(item.GetEffectiveShape(layer), item.GetBoundingBox()) for item in items
                if item.GetNetname() == net and item.IsOnLayer(layer)]

    def hole_collides(self, point, radius=0):
        return any(bbox_near(box, point, radius) and shape.Collide(point, radius)
                   for shape, box in self.holes)

    def contains(self, point, ground=True):
        # Effective copper shapes may cover drill centres; those are voids.
        if self.hole_collides(point):
            return False
        polys = self.ground_polys if ground else self.power_polys
        shapes = self.ground_shapes if ground else self.power_shapes
        return (any(poly.Contains(point) for poly in polys)
                or any(bbox_near(box, point) and shape.Collide(point, 0)
                       for shape, box in shapes))

    def nearest_ground_via(self, point):
        if not self.ground_vias:
            return None
        via = min(self.ground_vias, key=lambda v: (v.GetPosition().x - point.x)**2
                  + (v.GetPosition().y - point.y)**2)
        position = via.GetPosition()
        return {"distance_mm": round(math.hypot(position.x - point.x,
                                                position.y - point.y) / 1e6, 6),
                "position_mm": xy(position), "uuid": uid(via)}


def projection_survey(board, traces, reference, step_mm):
    rows, examples = {}, []
    for trace in traces:
        layer = board.GetLayerName(trace.GetLayer())
        length = mm(trace.GetLength())
        row = rows.setdefault(layer, {
            "sample_count": 0, "total_mm": 0.0, "In1_GND_uncovered_mm": 0.0,
            "uncovered_near_hole_mm": 0.0, "uncovered_away_from_hole_mm": 0.0,
            "max_uncovered_run_one_segment_mm": 0.0,
            "In2_power_uncovered_mm_for_bottom": 0.0})
        if trace.Type() != pcb.PCB_TRACE_T:
            row["unsupported_arc_projection"] = True
            continue
        if length <= 0:
            continue
        count = max(1, math.ceil(length / step_mm))
        piece, start, end, run = length / count, trace.GetStart(), trace.GetEnd(), 0.0
        for index in range(count):
            fraction = (index + 0.5) / count
            point = pcb.VECTOR2I(round(start.x + (end.x - start.x) * fraction),
                                round(start.y + (end.y - start.y) * fraction))
            row["sample_count"] += 1
            row["total_mm"] += piece
            if not reference.contains(point):
                row["In1_GND_uncovered_mm"] += piece
                run += piece
                near = reference.hole_collides(point, pcb.FromMM(HOLE_CLASSIFICATION_RADIUS_MM))
                row["uncovered_near_hole_mm" if near else "uncovered_away_from_hole_mm"] += piece
                if len(examples) < 8 or (not near and len(examples) < 20):
                    examples.append({"xy_mm": xy(point), "layer": layer,
                                     "within_0p6mm_of_hole": near, "track_uuid": uid(trace)})
            else:
                run = 0.0
            row["max_uncovered_run_one_segment_mm"] = max(
                row["max_uncovered_run_one_segment_mm"], run)
            if trace.GetLayer() == pcb.B_Cu and not reference.contains(point, ground=False):
                row["In2_power_uncovered_mm_for_bottom"] += piece
    for row in rows.values():
        row["In1_GND_projected_copper_coverage_percent"] = (
            100 * (1 - row["In1_GND_uncovered_mm"] / row["total_mm"])
            if row["total_mm"] else None)
        for key, value in list(row.items()):
            if isinstance(value, float):
                row[key] = round(value, 6)
    return rows, examples


def survey_net(board, connectivity, name, items, pads, reference, step_mm):
    net_items = [item for item in items if item.GetNetname() == name]
    traces = [item for item in net_items if not is_via(item)]
    vias = [item for item in net_items if is_via(item)]
    net_pads = sorted([pad for pad in pads if pad.GetNetname() == name],
                      key=lambda p: (p.GetParentFootprint().GetReference(), p.GetNumber()))
    by_layer = collections.defaultdict(float)
    for trace in traces:
        by_layer[board.GetLayerName(trace.GetLayer())] += mm(trace.GetLength())
    projection, examples = projection_survey(board, traces, reference, step_mm)
    return {
        "net": name, "geometry_sha256": geometry_fingerprint(traces, vias, net_pads),
        "total_trace_copper_mm": round(sum(by_layer.values()), 6),
        "trace_mm_by_layer": {key: round(value, 6) for key, value in sorted(by_layer.items())},
        "trace_segment_count": len(traces), "via_count": len(vias),
        "widths_mm": sorted({round(mm(t.GetWidth()), 6) for t in traces}),
        "pads": [{"reference": p.GetParentFootprint().GetReference(), "number": p.GetNumber(),
                  "xy_mm": xy(p.GetPosition())} for p in net_pads],
        "all_pads_one_native_component": connected_pad_component(connectivity, net_pads),
        "vias": [{"uuid": uid(v), "xy_mm": xy(v.GetPosition()),
                  "diameter_mm": mm(pcb.Cast_to_PCB_VIA(v).GetWidth(pcb.F_Cu)),
                  "drill_mm": mm(pcb.Cast_to_PCB_VIA(v).GetDrillValue()),
                  "nearest_GND_via": reference.nearest_ground_via(v.GetPosition())}
                 for v in sorted(vias, key=uid)],
        "projection_sampling": projection, "projection_uncovered_examples": examples}


def lfxo_geometry(pads, reference):
    lookup = {(p.GetParentFootprint().GetReference(), p.GetNumber()): p for p in pads}
    rows = []
    def distance(a, b):
        return round(math.hypot(a.x - b.x, a.y - b.y) / 1e6, 6)
    for name, pin, crystal_pin, cap in [("LF_XL1", "17", "1", "C7"),
                                       ("LF_XL2", "18", "2", "C8")]:
        mcu, crystal = lookup["U3", pin], lookup["Y1", crystal_pin]
        capacitor, ground = lookup[cap, "1"], lookup[cap, "2"]
        rows.append({"net": name,
                     "MCU_to_Y1_pad_straight_distance_mm": distance(mcu.GetPosition(), crystal.GetPosition()),
                     "Y1_to_cap_pad_straight_distance_mm": distance(crystal.GetPosition(), capacitor.GetPosition()),
                     "cap_GND_pad_nearest_GND_via": reference.nearest_ground_via(ground.GetPosition())})
    return rows


def drc_summary(path):
    if path is None:
        return {"file": None, "status": "NOT_PROVIDED_NOT_RUN_BY_THIS_SCRIPT"}
    raw = path.read_bytes()
    report = json.loads(raw)
    return {"file": file_label(path), "sha256": sha256(raw), "date": report.get("date"),
            "violations": len(report["violations"]),
            "unconnected": len(report["unconnected_items"]),
            "schematic_parity": len(report["schematic_parity"]),
            "ignored_checks": [item["key"] for item in report.get("ignored_checks", [])],
            "generated_by_this_script": False,
            "board_hash_binding": "NOT_INDEPENDENTLY_PROVEN_BY_DRC_JSON",
            "limitation": "Caller must provide the DRC produced from this exact saved board/project."}


def compare_baseline(report, baseline_path, baseline_report=None):
    if baseline_path is None:
        return None
    previous = baseline_report if baseline_report is not None else json.loads(baseline_path.read_bytes())
    before = {row["net"]: row for row in previous["nets"]}
    after = {row["net"]: row for row in report["nets"]}
    keys = ("total_trace_copper_mm", "trace_mm_by_layer", "trace_segment_count",
            "via_count", "widths_mm", "all_pads_one_native_component")
    changes = {}
    fingerprints = {}
    for name in sorted(before.keys() | after.keys()):
        old, new = before.get(name, {}), after.get(name, {})
        changed = {key: {"before": old.get(key), "after": new.get(key)}
                   for key in keys if old.get(key) != new.get(key)}
        pad_key = lambda p: (p["reference"], p["number"], p["xy_mm"])
        old_pads = sorted(old.get("pads", []), key=pad_key)
        new_pads = sorted(new.get("pads", []), key=pad_key)
        if old_pads != new_pads:
            changed["pads"] = {"before": old_pads, "after": new_pads}
        old_vias = [{k: v[k] for k in ("xy_mm", "diameter_mm", "drill_mm")}
                    for v in old.get("vias", [])]
        new_vias = [{k: v[k] for k in ("xy_mm", "diameter_mm", "drill_mm")}
                    for v in new.get("vias", [])]
        if sorted(old_vias, key=str) != sorted(new_vias, key=str):
            changed["via_geometry"] = {"before": old_vias, "after": new_vias}
        if changed:
            changes[name] = changed
        fingerprints[name] = (old["geometry_sha256"] == new["geometry_sha256"]
                              if old.get("geometry_sha256") and new.get("geometry_sha256") else None)
    return {"file": file_label(baseline_path), "file_sha256": sha256(baseline_path.read_bytes()),
            "source_kind": "native_board_read" if baseline_report is not None else "previous_json_report",
            "board_sha256": previous["board_sha256"], "net_metric_changes": changes,
            "geometry_identical_per_net": fingerprints,
            "all_signal_geometry_identical": (all(fingerprints.values())
                                               if all(v is not None for v in fingerprints.values()) else None),
            "limitation": "Legacy reports lack full fingerprints; equal listed metrics do not prove identical routes. Projection differences can also reflect fill or method changes."}


def build_report(path, drc_path=None, step_mm=DEFAULT_STEP_MM, as_of=None):
    data = path.read_bytes()
    board = pcb.LoadBoard(str(path))
    board.BuildConnectivity()
    tree = sexpr.parse_sexpr(data.decode())
    items, pads = list(board.Tracks()), list(board.GetPads())
    reference = ReferenceGeometry(board, items, pads)
    names = sorted({item.GetNetname() for item in items + pads
                    if item.GetNetname().startswith(("QSPI", "IMU_", "LF_"))
                    or item.GetNetname() == "FLASH_CS_N"})
    nets = [survey_net(board, board.GetConnectivity(), name, items, pads, reference, step_mm)
            for name in names]
    lookup = {row["net"]: row for row in nets}
    clock, flash_clock = lookup["QSPI_SCK"], lookup["QSPI_CLK_FLASH"]
    return {
        "status": "GEOMETRY_REVIEW_ONLY_PHYSICAL_SI_AND_LFXO_QUALIFICATION_REQUIRED",
        "as_of_utc": as_of or datetime.now(timezone.utc).isoformat(),
        "board_file": file_label(path), "board_sha256": sha256(data), "board_bytes": len(data),
        "board_unchanged_after_read": None, "kicad_version": pcb.GetBuildVersion(),
        "auditor": {"script": file_label(Path(__file__)), "script_sha256": sha256(Path(__file__).read_bytes()),
                    "method_version": METHOD_VERSION},
        "method": {
            "length": "Sum native GetLength of every trace by net/layer, including branches and trace portions overlapping pads. Pad copper is not added separately. Package/module routes and via barrel length excluded. Not electrical path-delay/skew.",
            "reference_projection": "Straight-track midpoint sampling of stored In1 GND fill plus GND pad/via copper; actual drilled-hole interiors excluded. In2 +3V projection for B.Cu reported separately. No refill or field simulation.",
            "max_sample_step_mm": step_mm,
            "near_hole_classification_radius_mm": HOLE_CLASSIFICATION_RADIUS_MM,
            "projection_arcs": "Not sampled; flagged if present. Native length and geometry fingerprint still include arcs.",
            "method_change_from_legacy_v1": "Drill interiors explicitly removed from effective pad/via copper shapes; full per-net geometry hashes and transitive connectivity added.",
            "geometry_fingerprint": "Sorted native trace/via/pad geometries; UUID and serialization order excluded. At KiCad coordinate precision; pad rotation/size/shape/layers included. Not a complete filled-copper hash.",
            "no_board_mutation": True},
        "nominal_board_thickness_mm": float(sexpr.atom(sexpr.child(tree, "general"), "thickness")),
        "copper_layers_top_to_bottom": [board.GetLayerName(layer) for layer in board.GetEnabledLayers().CuStack()],
        "explicit_dielectric_stackup_present_in_PCB": sexpr.child(sexpr.child(tree, "setup"), "stackup") is not None,
        "stackup_not_fabricator_qualified": True, "drc": drc_summary(drc_path),
        "GND_reference": {"In1_GND_zone_count": len(reference.ground_zones),
                          "filled_polygon_count": sum(p.OutlineCount() for p in reference.ground_polys),
                          "filled_area_mm2": sum(p.Area() / 1e12 for p in reference.ground_polys),
                          "non_via_tracks_on_In1": sum(not is_via(t) and t.GetLayer() == pcb.In1_Cu for t in items),
                          "GND_through_via_count": sum(pcb.Cast_to_PCB_VIA(v).GetViaType() == pcb.VIATYPE_THROUGH for v in reference.ground_vias)},
        "nets": nets,
        "signal_geometry_sha256": sha256(json.dumps({n: lookup[n]["geometry_sha256"] for n in names}, sort_keys=True).encode()),
        "clock_path": {"module_to_R11_QSPI_SCK_total_trace_mm": clock["total_trace_copper_mm"],
                       "module_to_R11_vias": clock["via_count"],
                       "R11_to_flash_total_trace_mm": flash_clock["total_trace_copper_mm"],
                       "R11_to_flash_vias": flash_clock["via_count"],
                       "combined_clock_trace_mm": round(clock["total_trace_copper_mm"] + flash_clock["total_trace_copper_mm"], 6),
                       "R11_nominal_ohm": 22, "termination_not_measured": True},
        "LFXO_geometry": lfxo_geometry(pads, reference),
        "physical_qualification": {"QSPI_32MHz": "NOT_QUALIFIED", "IMU_SPI_8MHz": "NOT_QUALIFIED",
                                   "LSM6DSV32X_manufacturer_SPI_limit_MHz": 10,
                                   "NRF52840_manufacturer_QSPI_limit_MHz": 32,
                                   "LFXO_load_ESR_startup_drive_temperature": "NOT_QUALIFIED",
                                   "max_board_supported_frequency_from_geometry": None},
        "sources": SOURCES}


def markdown(report):
    nets = {row["net"]: row for row in report["nets"]}
    lines = ["# Przegląd geometrii QSPI, SPI, LFXO i odniesienia GND", "",
             "Stan odczytu: **{}**, KiCad {}. Plik: `{}`, SHA256:".format(
                 report["as_of_utc"], report["kicad_version"], report["board_file"]), "",
             "`{}`".format(report["board_sha256"]), "",
             "Raport przeliczono z rzeczywistych obiektów i zapisanych wypełnień PCB, bez zmiany pliku ani ponownego fill. **QSPI 32 MHz, SPI IMU 8 MHz i LFXO wymagają fizycznej kwalifikacji.** Z geometrii ani DRC nie wyznaczono maksymalnej działającej częstotliwości.", "",
             "Audytor: [review_signal_geometry.py](../scripts/review_signal_geometry.py), metoda v{}, SHA256 `{}`. Szczegóły i fingerprints: [JSON](../reports/signal_geometry_review.json).".format(
                 report["auditor"]["method_version"], report["auditor"]["script_sha256"]), "",
             "## Długości i przelotki", "",
             "Długości są sumami natywnego `GetLength()` wszystkich ścieżek sieci, z gałęziami i częściami nachodzącymi na pady. Geometria padów nie dodaje osobnej długości. Pominięto połączenia wewnątrz modułów/pakietów i beczki przelotek. To nie pomiar drogi MCU–układ ani obliczenie skew.", "",
             "| Sieć | Razem [mm] | F.Cu | B.Cu | In2.Cu | Przelotki | Pady w jednym komponencie |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for row in report["nets"]:
        lengths = ["{:.3f}".format(row["trace_mm_by_layer"][layer]) if layer in row["trace_mm_by_layer"] else "—"
                   for layer in ("F.Cu", "B.Cu", "In2.Cu")]
        lines.append("| {} | {:.3f} | {} | {} | {} | {} | {} |".format(
            row["net"], row["total_trace_copper_mm"], *lengths, row["via_count"],
            {True: "tak", False: "NIE", None: "brak padów"}[row["all_pads_one_native_component"]]))
    clock, ground = report["clock_path"], report["GND_reference"]
    lines += ["", "## QSPI i SPI", "",
              "Zegar QSPI ma łącznie **{:.3f} mm**: moduł→R11 {:.3f} mm / {} przelotek; R11→Flash {:.3f} mm / {} przelotek. R11=22 Ω pozostaje wartością do strojenia, bez pomiaru skuteczności. Trasa wewnętrzna modułu nie jest znana z PCB.".format(
                  clock["combined_clock_trace_mm"], clock["module_to_R11_QSPI_SCK_total_trace_mm"],
                  clock["module_to_R11_vias"], clock["R11_to_flash_total_trace_mm"], clock["R11_to_flash_vias"]), "",
              "Zmiany warstw, gałęzie i obciążenia wymagają oceny odbić oraz marginesów czasowych. Różnice sum długości sieci nie są obliczonym skew. Brakuje kwalifikowanego stosu dielektryków i pełnego budżetu czasowego pakiet–PCB–odbiornik. Nordic dopuszcza do 32 MHz i wymaga właściwej konfiguracji pinów/high-drive; nie kwalifikuje to automatycznie tej płytki. [Nordic QSPI]({}), [Winbond W25Q01JV Rev E]({}).".format(SOURCES["Nordic_QSPI"], SOURCES["Winbond_flash"]), "",
              "IMU_SCK: **{:.3f} mm / {} przelotek**; MISO {:.3f} mm, MOSI {:.3f} mm. Planowane 8 MHz wymaga prób CS, duty cycle, setup/hold i integralności odczytów pod obciążeniem. Użyty limit katalogowy IMU: 10 MHz. [ST LSM6DSV32X, tabela SPI]({}).".format(
                  nets["IMU_SCK"]["total_trace_copper_mm"], nets["IMU_SCK"]["via_count"],
                  nets["IMU_MISO"]["total_trace_copper_mm"], nets["IMU_MOSI"]["total_trace_copper_mm"], SOURCES["ST_IMU"]), "",
              "## GND i drogi powrotne", "",
              "In1.Cu: {} stref GND, {} zapisanych obrysów fill, pole **{:.3f} mm²**, {} ścieżek na In1 i **{} przelotek przelotowych GND**. Liczba obrysów/pole nie opisują impedancji drogi powrotnej.".format(
                  ground["In1_GND_zone_count"], ground["filled_polygon_count"], ground["filled_area_mm2"],
                  ground["non_via_tracks_on_In1"], ground["GND_through_via_count"]), "",
              "Próbkowano środki prostych ścieżek co najwyżej {:.3f} mm. Sprawdzono zapisany fill In1 i miedź GND padów/przelotek z wyłączeniem wnętrz otworów. Odległość ≤{:.1f} mm od otworu jest tylko klasyfikacją pomocniczą. Arc projection jest jawnie pomijane/flagowane, jeśli występuje. To kontrola rzutu, bez symulacji pól/prądu powrotnego.".format(
                  report["method"]["max_sample_step_mm"], HOLE_CLASSIFICATION_RADIUS_MM), "",
              "| Sieć | Brak In1 w rzucie [mm] | Z tego dalej od otworów [mm] | Najdłuższy ciąg w jednym odcinku [mm] | Brak In2 +3V pod B.Cu [mm] |",
              "|---|---:|---:|---:|---:|"]
    for row in report["nets"]:
        samples = list(row["projection_sampling"].values())
        lines.append("| {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} |".format(
            row["net"], sum(r["In1_GND_uncovered_mm"] for r in samples),
            sum(r["uncovered_away_from_hole_mm"] for r in samples),
            max([r["max_uncovered_run_one_segment_mm"] for r in samples] or [0]),
            sum(r["In2_power_uncovered_mm_for_bottom"] for r in samples)))
    via_distances = [(v["nearest_GND_via"]["distance_mm"], row["net"])
                     for row in report["nets"] if row["net"].startswith("QSPI")
                     for v in row["vias"] if v["nearest_GND_via"]]
    if via_distances:
        distance, name = max(via_distances)
        lines += ["", "Największa odległość od przelotki QSPI do najbliższej przelotki GND: **{:.3f} mm ({})**. Nie jest to samodzielne kryterium zaliczenia drogi powrotnej.".format(distance, name)]
    lines += ["", "B.Cu sąsiaduje z mieszaną In2 (+3V0 i sygnały); In1 GND leży dalej. Pokrycie rzutu In1 nie dowodzi ciągłego najbliższego odniesienia na In2. Należy ocenić połączenia odniesienia przy przejściach warstw i wpływ antypadów według rzeczywistego stosu. [TI SCAA082A]({}).".format(SOURCES["TI_return_paths"]), "",
              "Nominalna grubość PCB: {:.3f} mm. Szczegółowy blok dielektryków w pliku: **{}**. Parametry fabryczne, Er i impedancje nie zostały zakwalifikowane; skrypt nie wyznacza impedancji ze stałych domyślnych KiCad.".format(
                  report["nominal_board_thickness_mm"], "jest" if report["explicit_dielectric_stackup_present_in_PCB"] else "brak"), "",
              "## LFXO", ""]
    for row in report["LFXO_geometry"]:
        signal = nets[row["net"]]
        via = row["cap_GND_pad_nearest_GND_via"]
        lines.append("{}: **{:.3f} mm / {} przelotek**, warstwy {}; odległość prosta MCU→Y1 {:.3f} mm, Y1→C {:.3f} mm; najbliższa przelotka GND od pada kondensatora: {} mm.".format(
            row["net"], signal["total_trace_copper_mm"], signal["via_count"],
            ", ".join(signal["trace_mm_by_layer"]), row["MCU_to_Y1_pad_straight_distance_mm"],
            row["Y1_to_cap_pad_straight_distance_mm"], "{:.3f}".format(via["distance_mm"]) if via else "brak"))
        lines.append("")
    lines += ["C7/C8=10 pF to wartości początkowe. Kryształ ABS07 w wybranej opcji ma CL=7 pF; pojemności pinów/PCB, ESR, drive, start i temperaturę należy ocenić fizycznie. Nie obciążać węzłów kwarcu zwykłą sondą podczas oceny częstotliwości; użyć buforowanego sygnału LFCLK. [Nordic CLOCK]({}), [Abracon ABS07]({}).".format(SOURCES["Nordic_CLOCK"], SOURCES["Abracon_ABS07"]), ""]
    baseline = report.get("baseline_comparison")
    if baseline:
        changed = ", ".join(baseline["net_metric_changes"]) or "brak zmian dostępnych metryk"
        lines += ["## Porównanie z bazą", "",
                  "Bazowy PCB SHA256: `{}`. Zmienione metryki sieci: **{}**. Wszystkie wartości bieżące przeliczono ponownie; nie podmieniono jedynie hasha.".format(baseline["board_sha256"], changed), "",
                  "Pełna identyczność geometrii według fingerprints: **{}**.".format(
                      "tak" if baseline["all_signal_geometry_identical"] is True else "nie" if baseline["all_signal_geometry_identical"] is False else "nie można rozstrzygnąć dla starszego formatu"), ""]
        if baseline["all_signal_geometry_identical"] is None:
            lines += ["Starszy raport bez fingerprints pozwala porównać długości/warstwy/pady/przelotki, ale nie dowodzi identycznej polilinii.", ""]
        elif baseline.get("source_kind") == "native_board_read":
            lines += ["Bazową PCB i bieżącą PCB odczytano natywnie tym samym audytorem; porównano geometrie wszystkich badanych ścieżek, przelotek i padów. Nie korzystano wyłącznie z historycznych sum długości.", ""]
        lines += ["Metoda v2 dodatkowo usuwa wnętrza otworów z kształtów miedzi padów/przelotek; może to zmienić wyniki projekcji względem historycznej metody v1.", ""]
    drc = report["drc"]
    lines += ["## Kontrole i kwalifikacja", ""]
    if drc.get("file"):
        lines += ["Dostarczony [DRC]({}) (`{}`): **{} naruszeń / {} niepołączonych / {} parity**, {} ignorowanych kontroli. Skrypt nie uruchamia DRC i nie potwierdza niezależnie związania tego JSON z hashem PCB; źródło DRC musi wskazać prowadzący audyt.".format(
            "../" + drc["file"] if not Path(drc["file"]).is_absolute() else drc["file"],
            drc["sha256"], drc["violations"], drc["unconnected"], drc["schematic_parity"], len(drc["ignored_checks"])), ""]
    else:
        lines += ["Nie dostarczono DRC do tego uruchomienia; skrypt nie uruchamia ERC/DRC.", ""]
    lines += ["Wymagane pozostają pomiary QSPI/SPI, strojenie zboczy i R11, testy CRC pełnych 128 MiB i obu dies po resetach/zanikach oraz kwalifikacja LFXO. [Plan prób Flash A1](flash_firmware_test_plan_A1.md). Poprawny DRC i długości ścieżek nie są certyfikacją SI ani dokładności/synchronizacji zegarów.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=ROOT / "hardware/Ankle_Sensor_V1.kicad_pcb")
    parser.add_argument("--json", type=Path, default=ROOT / "reports/signal_geometry_review.json")
    parser.add_argument("--markdown", type=Path, default=ROOT / "docs/signal_geometry_review.md")
    parser.add_argument("--drc", type=Path, help="Native DRC JSON from the same saved PCB; never run by this script")
    parser.add_argument("--expected-sha256", help="Fail without writing reports if the saved PCB differs")
    baseline_group = parser.add_mutually_exclusive_group()
    baseline_group.add_argument("--baseline", type=Path, help="Previous signal JSON, loaded before outputs are replaced")
    baseline_group.add_argument("--baseline-board", type=Path, help="Saved baseline PCB; survey it afresh without writing an intermediate report")
    parser.add_argument("--step-mm", type=float, default=DEFAULT_STEP_MM)
    parser.add_argument("--as-of-utc", help="Explicit ISO timestamp for reproducible report rendering")
    args = parser.parse_args()
    if not 0 < args.step_mm <= 0.05:
        parser.error("--step-mm must be >0 and <=0.05 mm")
    input_paths = {args.board.resolve()}
    if args.drc:
        input_paths.add(args.drc.resolve())
    if args.baseline_board:
        input_paths.add(args.baseline_board.resolve())
    if args.json.resolve() in input_paths or args.markdown.resolve() in input_paths:
        parser.error("Report output must not overwrite a board or DRC input")
    if args.json.resolve() == args.markdown.resolve():
        parser.error("JSON and Markdown outputs must be distinct")
    before = sha256(args.board.read_bytes())
    if args.expected_sha256 and before != args.expected_sha256.lower():
        parser.error("PCB SHA256 differs from --expected-sha256")
    report = build_report(args.board, args.drc, args.step_mm, args.as_of_utc)
    if args.baseline_board:
        baseline_before = sha256(args.baseline_board.read_bytes())
        baseline_report = build_report(args.baseline_board, step_mm=args.step_mm, as_of=args.as_of_utc)
        if (sha256(args.baseline_board.read_bytes()) != baseline_before
                or baseline_report["board_sha256"] != baseline_before):
            raise RuntimeError("Baseline PCB changed during read; no reports written")
        report["baseline_comparison"] = compare_baseline(report, args.baseline_board, baseline_report)
    else:
        report["baseline_comparison"] = compare_baseline(report, args.baseline)
    if sha256(args.board.read_bytes()) != before or report["board_sha256"] != before:
        raise RuntimeError("PCB changed during read; no reports written")
    report["board_unchanged_after_read"] = True
    json_text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    md_text = markdown(report)
    for path, content in [(args.json, json_text), (args.markdown, md_text)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print(json.dumps({"board_sha256": before, "signal_geometry_sha256": report["signal_geometry_sha256"],
                      "nets": {row["net"]: {"trace_mm": row["total_trace_copper_mm"],
                                               "via_count": row["via_count"]} for row in report["nets"]},
                      "json": file_label(args.json), "markdown": file_label(args.markdown)}, indent=2))


if __name__ == "__main__":
    main()
