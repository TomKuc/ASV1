#!/usr/bin/env python3
"""Create explicitly labelled mechanical clearance envelopes using KiCad OCCT.

These are rectangular solids, not manufacturer component models. No project
schematic or PCB is edited. Run with KiCad's bundled Python.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
TMP = Path('/private/tmp/ankle_model_envelopes')
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    model_dir = ROOT / 'hardware/3dmodels'
    model_dir.mkdir(parents=True, exist_ok=True)
    width, depth, height = 8.10, 6.10, 0.80
    board = pcbnew.BOARD()
    # This temporary construction uses the exported dielectric solid only.
    # KiCad10's default 2L stack subtracts 0.09mm for external Cu/mask.
    # Compensate here, then assert the actual exported solid is exactly0.80mm.
    construction_board_thickness = height + .09
    board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(construction_board_thickness))
    corners = [(-width/2, -depth/2), (width/2, -depth/2),
               (width/2, depth/2), (-width/2, depth/2)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1])))
        edge.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(b[0]), pcbnew.FromMM(b[1])))
        edge.SetWidth(pcbnew.FromMM(.05))
        board.Add(edge)
    source = TMP / 'W25Q01JVZEIQ_ENVELOPE_MAX.kicad_pcb'
    model = model_dir / 'W25Q01JVZEIQ_ENVELOPE_MAX.step'
    pcbnew.SaveBoard(str(source), board)
    env = dict(os.environ)
    env['KICAD_CONFIG_HOME'] = str(TMP / 'kicad_config')
    run = subprocess.run([CLI, 'pcb', 'export', 'step', '--force', '--board-only',
                          '--user-origin', '0x0mm', '--output', str(model), str(source)],
                         env=env, capture_output=True, text=True, check=True)
    text = model.read_text()
    points = [tuple(map(float, values.split(','))) for values in re.findall(
        r'CARTESIAN_POINT\([^,]*,\(([^)]+)\)\)', text)]
    points = [point for point in points if len(point) == 3]
    bounds = [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]
    for axis, expected in enumerate((width, depth, height)):
        assert abs((bounds[axis][1] - bounds[axis][0]) - expected) < 1e-6, (bounds, expected)
    assert abs(bounds[0][0] + bounds[0][1]) < 1e-6
    assert abs(bounds[1][0] + bounds[1][1]) < 1e-6
    z_offset = -bounds[2][0]
    assert abs(bounds[2][1] + z_offset - height) < 1e-6
    assert 'MANIFOLD_SOLID_BREP' in text
    relative = '${KIPRJMOD}/3dmodels/' + model.name
    entry = f'''(model "{relative}"
  (offset (xyz 0 0 {z_offset:.6f}))
  (scale (xyz 1 1 1))
  (rotate (xyz 0 0 0))
)'''
    manifest = {
        'date': '2026-10-28', 'reference': 'U5', 'mpn': 'W25Q01JVZEIQ',
        'kind': 'RECTANGULAR_MAXIMUM_PACKAGE_ENVELOPE_NOT_VENDOR_CAD',
        'dimensions_mm': [width, depth, height],
        'source': 'Winbond W25Q01JV Rev E, 2024-03-04, package ZE, printed page81',
        'source_url': 'https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf',
        'model_path': str(model.relative_to(ROOT)),
        'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
        'native_exporter': pcbnew.GetBuildVersion(),
        'construction_board_thickness_mm': construction_board_thickness,
        'native_bounds_mm': bounds,
        'recommended_offset_mm': [0, 0, z_offset],
        'resulting_bounds_above_pcb_top_mm': [0, height],
        'model_entry': entry,
        'limitations': [
            'Rectangular maximum package envelope only; no leads, exposed pad, chamfer or manufacturer geometry.',
            'Component placement and solder joint standoff require separate enclosure allowance.',
            'The main project PCB and its footprint model associations were not modified.',
        ],
        'usb_model': {'reference': 'J1', 'status': 'MISSING_EXACT_MODEL',
            'reason': 'Manufacturer page gives nominal8.94x7.35x3.16mm, but maximum dimensions, tolerances and mounting datum were not verified.'},
    }
    out = ROOT / 'hardware/geometry_sources/model_envelopes.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'reports/model_envelope_entry.sexpr').write_text(entry + '\n')
    (ROOT / 'reports/model_envelope_export.log').write_text(run.stdout + run.stderr)
    print(json.dumps({'model': str(model.relative_to(ROOT)), 'bounds_mm': bounds,
                      'offset_z_mm': z_offset, 'solid_brep': True}))


if __name__ == '__main__':
    main()
