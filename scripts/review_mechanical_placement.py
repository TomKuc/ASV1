#!/usr/bin/env python3
"""Read-only nominal placement/courtyard audit, not a solid CAD interference test."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import pcbnew

ROOT = Path(__file__).resolve().parents[1]


def mm(x):
    return round(pcbnew.ToMM(x), 6)


def bbox(b):
    return [mm(b.GetX()), mm(b.GetY()), mm(b.GetX()+b.GetWidth()), mm(b.GetY()+b.GetHeight())]


def rectangle_gap(a, b):
    return round(math.hypot(max(a[0]-b[2], b[0]-a[2], 0),
                            max(a[1]-b[3], b[1]-a[3], 0)), 6)


def main():
    path = ROOT / 'hardware/Ankle_Sensor_V1.kicad_pcb'
    board_bytes = path.read_bytes()
    board = pcbnew.LoadBoard(str(path))
    footprints = {f.GetReference(): f for f in board.GetFootprints()}
    populated = {c['ref'] for c in json.loads((ROOT/'hardware/design.json').read_text())['components'] if c['populate']}
    shapes, data, missing_models = {}, {}, []
    for ref, f in footprints.items():
        p = f.GetPosition()
        boxes = [bbox(g.GetBoundingBox()) for g in f.GraphicalItems()
                 if g.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab) and g.GetClass() == 'PCB_SHAPE']
        fab = None if not boxes else [min(b[0] for b in boxes), min(b[1] for b in boxes),
                                     max(b[2] for b in boxes), max(b[3] for b in boxes)]
        data[ref] = {'position_mm': [mm(p.x),mm(p.y)], 'angle_deg': f.GetOrientationDegrees(),
                     'layer': f.GetLayerName(), 'fab_aabb_including_stroke_mm': fab}
        if ref in populated:
            courtyard = f.GetCourtyard(f.GetLayer())
            if courtyard.OutlineCount():
                shapes[ref] = courtyard
        for model in f.Models():
            raw = model.m_Filename
            resolved = raw.replace('${KIPRJMOD}', str(ROOT/'hardware')).replace(
                '${KICAD10_3DMODEL_DIR}', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels')
            if not Path(resolved).is_file():
                missing_models.append({'reference': ref, 'model': raw})
    overlaps = []
    for a,b in itertools.combinations(sorted(shapes),2):
        if footprints[a].GetLayer() == footprints[b].GetLayer() and shapes[a].Collide(shapes[b]):
            overlaps.append([a,b])
    distances = {}
    for ref in ('SW1','J1','J2','U1','U2'):
        a,b=data['U4'],data[ref]
        distances[ref] = {'center_distance_mm': round(math.dist(a['position_mm'],b['position_mm']),6),
            'fab_aabb_min_gap_mm': rectangle_gap(a['fab_aabb_including_stroke_mm'],b['fab_aabb_including_stroke_mm'])}
    result = {'date': '2026-10-29', 'board_sha256_at_read': hashlib.sha256(board_bytes).hexdigest(),
        'board_size_mm': [30,51.6], 'method': 'Native KiCad footprint positions and same-side courtyard polygon collision; nominal FAB AABB distances.',
        'limitations': 'No 3D solid interference test; battery, housing, screws, cables and connector plug absent.',
        'imu_distances': distances, 'same_side_populated_courtyard_overlaps': overlaps,
        'missing_linked_model_files': missing_models,
        'mandatory_rf_keepout_board_coordinates_mm': [57.8,49.8,70.2,55.0],
        'rf_note': 'Extend all-Cu antenna keepout to the actual PCB edge; native refill/DRC required after integration.',
        'footprints': data}
    out=ROOT/'reports/mechanical_placement_review.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('imu_distances','same_side_populated_courtyard_overlaps','missing_linked_model_files')}))


if __name__=='__main__':
    main()
