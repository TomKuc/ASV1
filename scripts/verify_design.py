#!/usr/bin/env python3
"""Limited independent schematic/manifest audit, using only Python stdlib.

This is NOT KiCad ERC, DRC, a KiCad parser-validity check or a fabrication release.
Supported scope: flat sheets or a tree of sheet containers, embedded pin
definitions, simple wires, labels and explicit no_connect markers.
Sheet pins, buses and reused sheet files are outside verified scope.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


class ParseError(ValueError):
    pass


def parse_sexpr(source):
    """Parse strings and atoms without eval; reject unclosed/trailing input."""
    stack, roots = [], []
    i = 0
    while i < len(source):
        char = source[i]
        if char.isspace():
            i += 1
            continue
        if char == ";":
            end = source.find("\n", i)
            i = len(source) if end < 0 else end + 1
            continue
        if char == "(":
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
            i += 1
            continue
        if char == ")":
            if not stack:
                raise ParseError(f"Unexpected ')' at character {i}")
            stack.pop()
            i += 1
            continue
        if not stack:
            raise ParseError(f"Atom outside root expression at character {i}")
        if char == '"':
            i += 1
            token = []
            while i < len(source) and source[i] != '"':
                if source[i] == "\\":
                    i += 1
                    if i == len(source):
                        raise ParseError("Unclosed string escape")
                    token.append({"n": "\n", "r": "\r", "t": "\t"}.get(source[i], source[i]))
                else:
                    token.append(source[i])
                i += 1
            if i == len(source):
                raise ParseError("Unclosed string")
            stack[-1].append("".join(token))
            i += 1
        else:
            start = i
            while i < len(source) and not source[i].isspace() and source[i] not in "();":
                i += 1
            stack[-1].append(source[start:i])
    if stack:
        raise ParseError("Unclosed expression")
    if len(roots) != 1 or not roots[0]:
        raise ParseError("Expected one nonempty root expression")
    return roots[0]


def children(node, name):
    return [item for item in node[1:] if isinstance(item, list) and item and item[0] == name]


def child(node, name, default=None):
    found = children(node, name)
    if len(found) > 1:
        raise ParseError(f"Multiple {name} entries where one was expected")
    return found[0] if found else default


def atom(node, name, default=None):
    found = child(node, name)
    return found[1] if found and len(found) > 1 else default


def walk(node, skip=()):
    yield node
    for item in node[1:]:
        if isinstance(item, list) and item and item[0] not in skip:
            yield from walk(item, skip)


def point(x, y):
    return (round(float(x), 6), round(float(y), 6))


def at_point(node):
    at = child(node, "at")
    if not at or len(at) < 3:
        raise ParseError(f"Missing position on {node[0]}")
    return point(at[1], at[2])


def on_segment(p, a, b):
    cross = (p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])
    return abs(cross) < 1e-6 and min(a[0], b[0]) - 1e-6 <= p[0] <= max(a[0], b[0]) + 1e-6 and min(a[1], b[1]) - 1e-6 <= p[1] <= max(a[1], b[1]) + 1e-6


def world_pin(instance, pin):
    """Library y points up, sheet y points down; rotation is in CAD degrees."""
    sx, sy = at_point(instance)
    px, py = at_point(pin)
    at = child(instance, "at")
    angle = float(at[3]) if len(at) > 3 else 0
    mirror = atom(instance, "mirror")
    # Reject mirroring rather than silently use an unverified transform.
    if mirror:
        raise ParseError("Mirrored instances are outside this audit's verified scope")
    if angle % 90:
        raise ParseError("Nonorthogonal symbol rotation is outside verified scope")
    radians = math.radians(angle)
    return point(sx + px * math.cos(radians) - py * math.sin(radians), sy - px * math.sin(radians) - py * math.cos(radians))


def library_pins(library, unit=1, convert=1):
    pins = {}
    for sub in children(library, "symbol"):
        match = re.search(r"_(\d+)_(\d+)$", sub[1])
        if not match:
            raise ParseError(f"Cannot interpret embedded symbol unit {sub[1]}")
        if int(match[1]) not in (0, unit) or int(match[2]) not in (0, convert):
            continue
        for pin in children(sub, "pin"):
            number = atom(pin, "number")
            if number is None:
                raise ParseError("Library pin without number")
            if number in pins:
                raise ParseError(f"Duplicate library pin number {number}")
            pins[number] = pin
    if not pins:
        raise ParseError(f"No pins found for {library[1]}, unit {unit}")
    return pins


def normalize_design(design):
    if isinstance(design, list):
        return {"components": design}
    if not isinstance(design, dict) or not isinstance(design.get("components"), list):
        raise ParseError("Manifest must be a components list or an object with components list")
    return design


def verify(design, schematic, *, check_singletons=True, allow_sheet_containers=False):
    design = normalize_design(design)
    issues = []
    def issue(code, message, severity="error"):
        issues.append({"severity": severity, "code": code, "message": message})

    if schematic[0] != "kicad_sch":
        raise ParseError("Not a kicad_sch document")
    unsupported_kinds = ["bus", "bus_entry", "hierarchical_label", "symbol_instances"]
    if not allow_sheet_containers:
        unsupported_kinds.append("sheet")
    for unsupported in unsupported_kinds:
        if children(schematic, unsupported):
            issue("unsupported_construct", f"Top-level {unsupported} requires KiCad verification")
    expected = {}
    for component in design["components"]:
        if not isinstance(component, dict) or not component.get("ref") or not isinstance(component.get("pins"), dict):
            raise ParseError("Each component needs ref and pins dictionary")
        ref = str(component["ref"])
        if ref in expected:
            issue("duplicate_manifest_reference", ref)
        expected[ref] = component
        for number, net in component["pins"].items():
            if not isinstance(number, str) or not number or (net is not None and (not isinstance(net, str) or not net)):
                raise ParseError(f"Invalid pin/net entry for {ref}.{number}")

    uuids = collections.Counter(node[1] for node in walk(schematic, ("lib_symbols",)) if node[0] == "uuid" and len(node) == 2)
    for uid, count in uuids.items():
        if count > 1:
            issue("duplicate_uuid", f"{uid} occurs {count} times outside lib_symbols")
    libs_node = child(schematic, "lib_symbols", ["lib_symbols"])
    libraries = {}
    for lib in children(libs_node, "symbol"):
        if lib[1] in libraries:
            issue("duplicate_library_id", lib[1])
        libraries[lib[1]] = lib

    pins_world = {}
    instances = {}
    for instance in children(schematic, "symbol"):
        properties = {prop[1]: prop[2] for prop in children(instance, "property") if len(prop) >= 3}
        ref = properties.get("Reference")
        if not ref:
            issue("missing_reference", str(atom(instance, "uuid")))
            continue
        if ref in instances:
            issue("duplicate_schematic_reference", ref)
        instances[ref] = instance
        if ref not in expected:
            issue("unexpected_component", ref)
            continue
        component = expected[ref]
        lib_id = atom(instance, "lib_id")
        requested_symbol = component.get("symbol")
        if requested_symbol and requested_symbol not in (lib_id, str(lib_id).split(":")[-1]):
            issue("symbol_mismatch", f"{ref}: manifest={requested_symbol}, schematic={lib_id}")
        if component.get("footprint") and properties.get("Footprint") != component["footprint"]:
            issue("footprint_mismatch", f"{ref}: {properties.get('Footprint')} != {component['footprint']}")
        for manifest_key, names in (("mpn", ("MPN", "Manufacturer Part Number")), ("jlcpcb", ("JLCPCB", "LCSC", "LCSC Part #", "LCSC Part"))):
            existing = next((properties[name] for name in names if name in properties), None)
            if existing is not None and component.get(manifest_key) and existing != str(component[manifest_key]):
                issue("property_mismatch", f"{ref}: {manifest_key} field differs from manifest")
        if lib_id not in libraries:
            issue("missing_embedded_symbol", f"{ref}: {lib_id}")
            continue
        if atom(libraries[lib_id], "extends"):
            issue("unsupported_inheritance", f"{ref}: inherited symbol needs KiCad resolution")
            continue
        pin_defs = library_pins(libraries[lib_id], int(atom(instance, "unit", 1)), int(atom(instance, "convert", 1)))
        actual_numbers = set(pin_defs)
        expected_numbers = set(component["pins"])
        if actual_numbers != expected_numbers:
            issue("pin_set_mismatch", f"{ref}: library-only={sorted(actual_numbers - expected_numbers)}, manifest-only={sorted(expected_numbers - actual_numbers)}")
        pin_records = [pin[1] for pin in children(instance, "pin")]
        if set(pin_records) != actual_numbers or len(pin_records) != len(set(pin_records)):
            issue("instance_pin_records", f"{ref}: pin instance records differ from library pin set")
        for number, pin in pin_defs.items():
            pins_world[(ref, number)] = world_pin(instance, pin)
    for ref in set(expected) - set(instances):
        issue("missing_component", ref)

    labels = []
    for kind in ("label", "global_label"):
        for label in children(schematic, kind):
            labels.append((at_point(label), label[1]))
    no_connects = [at_point(nc) for nc in children(schematic, "no_connect")]
    nc_counter = collections.Counter(no_connects)
    for p, count in nc_counter.items():
        if count > 1:
            issue("duplicate_nc", str(p))
    segments = []
    for wire in children(schematic, "wire"):
        pts = child(wire, "pts", ["pts"])
        xy = children(pts, "xy")
        if len(xy) != 2:
            issue("unsupported_wire", "Wire does not have two endpoints")
            continue
        a, b = (point(p[1], p[2]) for p in xy)
        if a == b:
            issue("zero_length_wire", str(a))
        segments.append((a, b))
    points = set(pins_world.values()) | {p for p, _ in labels} | set(no_connects)
    points |= {at_point(junction) for junction in children(schematic, "junction")}
    for a, b in segments:
        points.update((a, b))
    # Interior crossings connect only if an endpoint, label, pin or junction is present.
    graph = collections.defaultdict(set)
    wire_points = set()
    for a, b in segments:
        along = sorted(p for p in points if on_segment(p, a, b))
        wire_points.update(along)
        for p, q in zip(along, along[1:]):
            graph[p].add(q)
            graph[q].add(p)
    components_of_points = {}
    graph_groups = []
    for p in points:
        if p in components_of_points:
            continue
        group_id = len(graph_groups)
        group, todo = set(), [p]
        while todo:
            current = todo.pop()
            if current in group:
                continue
            group.add(current)
            components_of_points[current] = group_id
            todo.extend(graph[current] - group)
        graph_groups.append(group)
    group_names = collections.defaultdict(set)
    for p, name in labels:
        group_names[components_of_points[p]].add(name)
    group_global_names = collections.defaultdict(set)
    for label in children(schematic, "global_label"):
        group_global_names[components_of_points[at_point(label)]].add(label[1])
    for group_id, names in group_names.items():
        if len(names) > 1:
            issue("shorted_net_labels", f"Physically connected labels: {sorted(names)}")

    expected_nc_points = set()
    net_pins = collections.defaultdict(list)
    checked_connected = checked_nc = 0
    global_label_pins = []
    for ref, component in expected.items():
        for number, net in component["pins"].items():
            key = (ref, number)
            if net is not None:
                net_pins[net].append(key)
            if key not in pins_world:
                continue
            p = pins_world[key]
            names = group_names.get(components_of_points[p], set())
            if net is None:
                checked_nc += 1
                expected_nc_points.add(p)
                if p not in nc_counter:
                    issue("missing_no_connect", f"{ref}.{number} at {p}")
                if p in wire_points or names:
                    issue("nc_pin_connected", f"{ref}.{number} at {p}")
            else:
                checked_connected += 1
                if p not in wire_points:
                    issue("pin_without_wire", f"{ref}.{number} expected {net} at {p}")
                if names != {net}:
                    issue("pin_net_mismatch", f"{ref}.{number}: expected {net}, physical labels {sorted(names)}")
                if net in group_global_names.get(components_of_points[p], set()):
                    global_label_pins.append([ref, number, net])
                if p in nc_counter:
                    issue("connected_pin_marked_nc", f"{ref}.{number}: {net}")
    for p in set(no_connects) - expected_nc_points:
        issue("unexpected_no_connect", str(p))
    for p, name in labels:
        if name not in net_pins:
            issue("unexpected_net_label", f"{name} at {p}")
    allowed_single = set(design.get("open_nets", [])) | set(design.get("test_nets", [])) | set(design.get("allow_single_pin_nets", []))
    for net, refs in net_pins.items():
        if check_singletons and len(refs) == 1 and net not in allowed_single:
            ref = refs[0][0]
            is_test = ref.upper().startswith("TP") or "testpoint" in str(expected[ref].get("symbol", "")).lower()
            if not is_test:
                issue("single_pin_net", f"{net}: {refs[0][0]}.{refs[0][1]}; declare an intentional open/test net explicitly")
    return {
        "check_type": "independent_static_schematic_manifest_audit",
        "status": "STATIC_CHECKS_FAILED" if any(i["severity"] == "error" for i in issues) else "STATIC_CHECKS_PASS",
        "kicad_erc": "NOT_RUN",
        "kicad_drc": "NOT_RUN",
        "fabrication_release": False,
        "scope": "One flat schematic; embedded pin positions, wire/label connectivity, NC, references, UUIDs and manifest consistency",
        "limitations": ["This does not validate KiCad syntax or its electrical pin rules", "Does not validate datasheet correctness, footprint geometry, PCB routing, RF or charging safety", "Unsupported hierarchy, inheritance, buses and mirrors are errors"],
        "counts": {"manifest_components": len(expected), "schematic_components": len(instances), "connected_pins_checked": checked_connected, "nc_pins_checked": checked_nc, "nets": len(net_pins), "wires": len(segments), "labels": len(labels), "uuids": len(uuids), "errors": sum(i["severity"] == "error" for i in issues)},
        "pins_with_global_labels": global_label_pins,
        "issues": issues,
    }


def verify_project(design, root_path):
    """Audit separate sheet geometries; join only actual global labels by name.

    Manifest sheet fields select a sheet by filename stem. Container hierarchy
    and instance UUID paths are inspected; sheet pins and reused files fail.
    """
    design = normalize_design(design)
    root_path = root_path.resolve()
    files, sources, trees, paths = {}, {}, {}, {}
    issues = []
    def visit(path, hierarchy_path):
        path = path.resolve()
        if path in trees:
            raise ParseError(f"Reused/cyclic sheet file outside verified scope: {path}")
        if path.parent != root_path.parent:
            raise ParseError(f"Sheet outside project directory: {path}")
        contents = path.read_bytes()
        tree = parse_sexpr(contents.decode("utf-8"))
        if tree[0] != "kicad_sch":
            raise ParseError(f"Not a schematic: {path}")
        trees[path] = tree
        paths[path] = hierarchy_path or f"/{atom(tree, 'uuid')}"
        sources[str(path)] = hashlib.sha256(contents).hexdigest()
        if path.stem in files:
            raise ParseError(f"Duplicate sheet stem: {path.stem}")
        files[path.stem] = path
        for sheet in children(tree, "sheet"):
            if children(sheet, "pin"):
                raise ParseError(f"Sheet pins outside verified scope: {path}")
            props = {prop[1]: prop[2] for prop in children(sheet, "property") if len(prop) >= 3}
            filename = props.get("Sheetfile") or props.get("Sheet file")
            uid = atom(sheet, "uuid")
            if not filename or not uid:
                raise ParseError(f"Sheet lacks filename/UUID: {path}")
            child_path = path.parent / filename
            visit(child_path, f"{paths[path]}/{uid}")
    visit(root_path, None)
    if len(trees) == 1 and not any(component.get("sheet") for component in design["components"]):
        result = verify(design, trees[root_path])
        result["schematic_sources_sha256"] = sources
        return result

    seen_uuids, seen_refs = collections.defaultdict(list), collections.defaultdict(list)
    reports = {}
    pin_global = set()
    for path, tree in trees.items():
        subset = dict(design)
        subset["components"] = [component for component in design["components"] if component.get("sheet") == path.stem]
        result = verify(subset, tree, check_singletons=False, allow_sheet_containers=True)
        reports[path.stem] = result
        issues.extend(dict(item, sheet=path.stem) for item in result["issues"])
        pin_global.update(tuple(record) for record in result["pins_with_global_labels"])
        for node in walk(tree, ("lib_symbols",)):
            if node[0] == "uuid" and len(node) == 2:
                seen_uuids[node[1]].append(path.stem)
        for instance in children(tree, "symbol"):
            props = {prop[1]: prop[2] for prop in children(instance, "property") if len(prop) >= 3}
            ref = props.get("Reference")
            if ref:
                seen_refs[ref].append(path.stem)
            records = [node for node in walk(instance) if node[0] == "path" and len(node) >= 2]
            if len(records) != 1 or records[0][1] != paths[path]:
                issues.append({"severity": "error", "code": "instance_hierarchy_path", "sheet": path.stem, "message": f"{ref}: expected exactly one instance path {paths[path]}"})
            elif atom(records[0], "reference") != ref:
                issues.append({"severity": "error", "code": "instance_hierarchy_reference", "sheet": path.stem, "message": f"{ref}: hierarchy reference differs from field"})
    for uid, sheets in seen_uuids.items():
        if len(set(sheets)) > 1:
            issues.append({"severity": "error", "code": "duplicate_project_uuid", "message": f"{uid}: {sheets}"})
    for ref, sheets in seen_refs.items():
        if len(sheets) > 1:
            issues.append({"severity": "error", "code": "duplicate_project_reference", "message": f"{ref}: {sheets}"})
    expected_refs = collections.Counter(str(component["ref"]) for component in design["components"])
    net_pins = collections.defaultdict(list)
    for component in design["components"]:
        ref = str(component["ref"])
        if component.get("sheet") not in files:
            issues.append({"severity": "error", "code": "unknown_manifest_sheet", "message": f"{ref}: {component.get('sheet')}"})
        if expected_refs[ref] > 1:
            issues.append({"severity": "error", "code": "duplicate_manifest_reference", "message": ref})
        for pin, net in component["pins"].items():
            if net is not None:
                net_pins[net].append((ref, pin, component.get("sheet")))
    allowed_single = set(design.get("open_nets", [])) | set(design.get("test_nets", [])) | set(design.get("allow_single_pin_nets", []))
    for net, pins in net_pins.items():
        if len({record[2] for record in pins}) > 1:
            for ref, pin, sheet in pins:
                if (ref, pin, net) not in pin_global:
                    issues.append({"severity": "error", "code": "cross_sheet_net_without_global_label", "sheet": sheet, "message": f"{ref}.{pin}: {net}"})
        if len(pins) == 1 and net not in allowed_single:
            ref, pin, sheet = pins[0]
            component = next(component for component in design["components"] if str(component["ref"]) == ref)
            if not ref.upper().startswith("TP") and "testpoint" not in str(component.get("symbol", "")).lower():
                issues.append({"severity": "error", "code": "single_pin_net", "sheet": sheet, "message": f"{net}: {ref}.{pin}; declare intentional open/test net explicitly"})
    counts = {key: sum(result["counts"].get(key, 0) for result in reports.values()) for key in ("schematic_components", "connected_pins_checked", "nc_pins_checked", "wires", "labels")}
    counts.update({"manifest_components": len(design["components"]), "sheets": len(trees), "nets": len(net_pins), "uuids": len(seen_uuids), "errors": sum(issue["severity"] == "error" for issue in issues)})
    return {
        "check_type": "independent_static_schematic_manifest_audit",
        "status": "STATIC_CHECKS_FAILED" if counts["errors"] else "STATIC_CHECKS_PASS",
        "kicad_erc": "NOT_RUN", "kicad_drc": "NOT_RUN", "fabrication_release": False,
        "scope": "Separate sheet geometry; global labels by name; sheet paths, embedded pins, wire/label connectivity, NC, references, UUIDs and manifest consistency",
        "limitations": ["This does not validate KiCad syntax or its electrical pin rules", "Does not validate datasheets, footprint geometry, PCB routing, RF or charging safety", "Sheet pins, reused sheet files, buses, inherited and mirrored symbols are outside scope"],
        "counts": counts, "schematic_sources_sha256": sources,
        "sheet_counts": {name: result["counts"] for name, result in reports.items()}, "issues": issues,
    }


def write_bom(design, path):
    """Manifest-derived audit BOM. No claimed PCBA availability or rotation data."""
    groups = collections.defaultdict(list)
    for component in normalize_design(design)["components"]:
        if component.get("populate") is False or component.get("in_bom") is False:
            continue
        key = tuple(str(component.get(name) or "") for name in ("value", "mpn", "footprint", "jlcpcb"))
        groups[key].append(str(component["ref"]))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("Comment", "Designator", "Footprint", "LCSC Part #", "MPN", "Quantity", "Audit status"))
        for (value, mpn, footprint, jlcpcb), refs in sorted(groups.items(), key=lambda item: sorted(item[1])[0]):
            writer.writerow((value or mpn, ",".join(sorted(refs)), footprint, jlcpcb, mpn, len(refs), "MANIFEST ONLY; NOT ORDER RELEASE" if jlcpcb else "MISSING JLCPCB ID; NOT ORDER RELEASE"))


def self_test():
    library = '(symbol "Local:Two" (symbol "Two_1_1" (pin passive line (at -5 0 0) (number "1")) (pin passive line (at 5 0 180) (number "2"))))'
    instance = '(symbol (lib_id "Local:Two") (at 100 100 0) (unit 1) (uuid "instance") (property "Reference" "U1") (property "Footprint" "Local:Two") (pin "1" (uuid "pin1")) (pin "2" (uuid "pin2")))'
    good = f'(kicad_sch (uuid "root") (lib_symbols {library}) {instance} (wire (pts (xy 95 100) (xy 90 100)) (uuid "wire")) (label "N" (at 90 100 0) (uuid "label")) (no_connect (at 105 100) (uuid "nc")))'
    design = {"components": [{"ref": "U1", "symbol": "Local:Two", "footprint": "Local:Two", "pins": {"1": "N", "2": None}}], "open_nets": ["N"]}
    tests = 0
    assert verify(design, parse_sexpr(good))["counts"]["errors"] == 0
    tests += 1
    for old, new, expected_code in [
        ('(at 90 100 0)', '(at 89 100 0)', 'pin_net_mismatch'),
        ('(no_connect (at 105 100) (uuid "nc"))', '', 'missing_no_connect'),
        ('(uuid "pin2")', '(uuid "pin1")', 'duplicate_uuid'),
        ('(property "Reference" "U1")', '(property "Reference" "U2")', 'missing_component'),
        ('(label "N"', '(label "WRONG"', 'pin_net_mismatch'),
    ]:
        report = verify(design, parse_sexpr(good.replace(old, new)))
        assert expected_code in {issue["code"] for issue in report["issues"]}, (expected_code, report)
        tests += 1
    shorted = good[:-1] + '(label "OTHER" (at 95 100 0) (uuid "other")))'
    assert 'shorted_net_labels' in {issue['code'] for issue in verify(design, parse_sexpr(shorted))['issues']}
    tests += 1
    assert parse_sexpr('(x "a\\\"b" "")') == ['x', 'a"b', '']
    tests += 1
    for invalid in ('(x', '(x))', '(x "unclosed)', '(x)(y)'):
        try:
            parse_sexpr(invalid)
        except ParseError:
            tests += 1
        else:
            raise AssertionError(f"Malformed expression accepted: {invalid}")
    top_pin = parse_sexpr('(pin (at 0 5 0))')
    assert world_pin(parse_sexpr('(symbol (at 100 100 90))'), top_pin) == (95.0, 100.0)
    tests += 1
    # Independent sheet fixtures verify coordinates are not merged across sheets
    # and local labels cannot impersonate a global connection.
    with tempfile.TemporaryDirectory(prefix="ankle-static-verifier-") as directory:
        directory = Path(directory)
        root = directory / "root.kicad_sch"
        root.write_text('(kicad_sch (uuid "root") (lib_symbols) (sheet (uuid "a") (property "Sheetfile" "a.kicad_sch")) (sheet (uuid "b") (property "Sheetfile" "b.kicad_sch")))', encoding="utf-8")
        project_design = {"components": []}
        child_sources = {}
        for sheet_name, ref in (("a", "U1"), ("b", "U2")):
            placed = instance.replace('"U1"', f'"{ref}"')
            placed = placed[:-1] + f'(instances (project "test" (path "/root/{sheet_name}" (reference "{ref}") (unit 1)))))'
            sheet_source = f'(kicad_sch (uuid "page") (lib_symbols {library}) {placed} (wire (pts (xy 95 100) (xy 90 100)) (uuid "wire")) (global_label "N" (at 90 100 0) (uuid "label")) (no_connect (at 105 100) (uuid "nc")))'
            sheet_source = re.sub(r'\(uuid "([^"]+)"\)', lambda match: f'(uuid "{sheet_name}-{match[1]}")', sheet_source)
            child_sources[sheet_name] = sheet_source
            (directory / f"{sheet_name}.kicad_sch").write_text(sheet_source, encoding="utf-8")
            project_design["components"].append({"ref": ref, "sheet": sheet_name, "symbol": "Local:Two", "footprint": "Local:Two", "pins": {"1": "N", "2": None}})
        assert verify_project(project_design, root)["counts"]["errors"] == 0
        tests += 1
        child_b = directory / "b.kicad_sch"
        child_b.write_text(child_sources["b"].replace("(global_label", "(label"), encoding="utf-8")
        assert "cross_sheet_net_without_global_label" in {issue["code"] for issue in verify_project(project_design, root)["issues"]}
        tests += 1
        child_b.write_text(child_sources["b"].replace('"b-page"', '"a-page"'), encoding="utf-8")
        assert "duplicate_project_uuid" in {issue["code"] for issue in verify_project(project_design, root)["issues"]}
        tests += 1
        child_b.write_text(child_sources["b"].replace('"/root/b"', '"/root/wrong"'), encoding="utf-8")
        assert "instance_hierarchy_path" in {issue["code"] for issue in verify_project(project_design, root)["issues"]}
        tests += 1
    print(f"Static verifier self-tests passed: {tests}; this script does not execute KiCad ERC/DRC")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, default=Path("hardware/design.json"))
    parser.add_argument("--schematic", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("reports"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    schematic_path = args.schematic
    if schematic_path is None:
        preferred = args.design.parent / "Ankle_Sensor_V1.kicad_sch"
        candidates = [preferred] if preferred.exists() else sorted(args.design.parent.glob("*.kicad_sch"))
        if len(candidates) != 1:
            parser.error("Provide --schematic (there must otherwise be exactly one schematic beside design.json)")
        schematic_path = candidates[0]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    try:
        design_bytes, schematic_bytes = args.design.read_bytes(), schematic_path.read_bytes()
        design = json.loads(design_bytes)
        report = verify_project(design, schematic_path)
        report["inputs"] = {"design": str(args.design), "design_sha256": hashlib.sha256(design_bytes).hexdigest(), "schematic": str(schematic_path), "schematic_sha256": hashlib.sha256(schematic_bytes).hexdigest()}
        write_bom(design, args.out_dir / "bom_from_design.csv")
    except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
        report = {"status": "STATIC_CHECKS_FAILED", "fabrication_release": False, "kicad_erc": "NOT_RUN", "kicad_drc": "NOT_RUN", "issues": [{"severity": "error", "code": "input_or_parser_failure", "message": str(error)}]}
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    (args.out_dir / "static_design_verification.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Statyczna kontrola schematu i manifestu", "", f"Status: **{report['status']}**", "", "**To nie jest ERC ani DRC KiCad. Nie stanowi zwolnienia do produkcji.**", "", "Sprawdzono jedynie zgodność parsowanego schematu z manifestem oraz ograniczony model połączeń.", "", "Ten skrypt nie uruchamia ERC/DRC. Rzeczywiste raporty KiCad są zapisane osobno w katalogu reports.", ""]
    for key, value in report.get("counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Wykryte problemy", ""])
    lines.extend(f"- {item['severity']}: `{item['code']}` — {item['message']}" for item in report["issues"])
    if not report["issues"]:
        lines.append("Brak rozbieżności w objętym zakresem modelu statycznym. Wymagane otwarcie i ERC w KiCad.")
    lines.extend(["", "BOM `bom_from_design.csv` pochodzi wyłącznie z manifestu. Nie potwierdza dostępności części ani montażu PCBA.", ""])
    (args.out_dir / "static_design_verification.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{report['status']}: {len(report['issues'])} finding(s). This script does not execute KiCad ERC/DRC.")
    return 1 if report["status"] == "STATIC_CHECKS_FAILED" else 0


if __name__ == "__main__":
    sys.exit(main())
