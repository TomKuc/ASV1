#!/usr/bin/env python3
"""Compare exported coordinates with native PCB; not an independent CAM DRC.

Run with the KiCad-bundled Python. Intentionally supports only this project's
decimal Excellon/G85 and straight rectangular profile export, failing closed
if the geometry or format changes.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'manufacturing/review'


def xy(v):
    return (round(pcb.ToMM(v.x), 6), round(pcb.ToMM(v.y), 6))


def drill(path):
    tools = {}; active = None; holes = []; slots = []
    text = path.read_text()
    assert 'METRIC' in text and 'G90' in text and 'M30' in text
    number = r'(-?\d+(?:\.\d*)?)'
    for line in text.splitlines():
        m = re.fullmatch(r'T(\d+)C'+number, line)
        if m:
            tools[m[1]] = float(m[2]); continue
        m = re.fullmatch(r'T(\d+)', line)
        if m:
            active = m[1]; continue
        if not line.startswith('X'):
            continue
        m = re.fullmatch('X'+number+'Y'+number+'G85X'+number+'Y'+number, line)
        if m:
            x1,y1,x2,y2 = map(float,m.groups())
            slots.append((round((x1+x2)/2,6), round((y1+y2)/2,6), tools[active],
                          round(abs(x2-x1)+tools[active],6), round(abs(y2-y1)+tools[active],6)))
            continue
        m = re.fullmatch('X'+number+'Y'+number, line)
        assert m, 'Unsupported Excellon coordinate: '+line
        holes.append((*map(float,m.groups()), tools[active]))
    return sorted(holes),sorted(slots)


def compare_drills(actual, expected):
    # Decimal Excellon coordinates are rounded to 1 um by this exporter.
    # This is a file-format tolerance, not a manufacturing tolerance.
    remaining=list(expected);maximum=0.0
    assert len(actual)==len(expected)
    for row in actual:
        matches=[r for r in remaining if len(r)==len(row) and
                 all(abs(a-b)<=0.00051 for a,b in zip(row,r))]
        assert len(matches)==1, ('Unmatched/ambiguous drill',row,matches)
        match=matches[0];remaining.remove(match)
        maximum=max(maximum,max(abs(a-b) for a,b in zip(row,match)))
    assert not remaining
    return maximum


def main():
    path = ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb'
    board = pcb.LoadBoard(str(path))
    origin = xy(board.GetDesignSettings().GetAuxOrigin())
    assert origin == (50.0,101.6)
    def plot(v):
        x,y = xy(v)
        return round(x-origin[0],6),round(origin[1]-y,6)
    footprints = {f.GetReference():f for f in board.GetFootprints()}
    manifest = json.loads((OUT/'export_manifest.json').read_text())
    board_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    assert manifest['board_sha256'] == board_hash
    parts = {c['ref'] for c in json.loads((ROOT/'hardware/design.json').read_text())['components'] if c['populate']}
    positions = list(csv.DictReader((OUT/'assembly/CPL_REVIEW_ROTATIONS_UNCONFIRMED.csv').open()))
    assert {r['Designator'] for r in positions} == parts
    for row in positions:
        f = footprints[row['Designator']]
        assert plot(f.GetPosition()) == (float(row['Mid X']),float(row['Mid Y']))
        assert f.GetLayer()==pcb.F_Cu and row['Layer']=='Top'
        assert abs(f.GetOrientationDegrees()-float(row['Rotation']))<1e-6
    vias = sorted((*plot(t.GetPosition()),round(pcb.ToMM(t.GetDrillValue()),6))
                  for t in board.GetTracks() if t.GetClass()=='PCB_VIA')
    pth,slots = drill(OUT/'drill/Ankle_Sensor_V1-PTH.drl')
    npth,np_slots = drill(OUT/'drill/Ankle_Sensor_V1-NPTH.drl')
    via_error=compare_drills(pth,vias)
    assert not np_slots
    expected_npth=[];expected_slots=[]
    for f in board.GetFootprints():
        for p in f.Pads():
            dx,dy=xy(p.GetDrillSize())
            if not dx and not dy:
                continue
            center=plot(p.GetPosition())
            if p.GetAttribute()==pcb.PAD_ATTRIB_NPTH:
                assert dx==dy
                expected_npth.append((*center,dx))
            else:
                assert f.GetReference()=='J1' and p.GetNumber()=='SH'
                assert p.GetOrientationDegrees()%180==0
                expected_slots.append((*center,min(dx,dy),dx,dy))
    npth_error=compare_drills(npth,expected_npth)
    slot_error=compare_drills(slots,expected_slots)
    profile=OUT/'gerbers/Ankle_Sensor_V1-Edge_Cuts.gbr'
    content=profile.read_text()
    assert '%FSLAX46Y46*%' in content and '%MOMM*%' in content
    previous=None;segments=[]
    for line in content.splitlines():
        m=re.fullmatch(r'X(-?\d+)Y(-?\d+)D0([12])\*',line)
        if m:
            point=(int(m[1])/1e6,int(m[2])/1e6)
            if m[3]=='1':
                assert previous is not None
                segments.append(tuple(sorted((previous,point))))
            previous=point
    a,b,c,d=(0.,0.),(30.,0.),(30.,51.6),(0.,51.6)
    assert set(segments)=={tuple(sorted(pair)) for pair in ((a,b),(b,c),(c,d),(d,a))}
    result={'status':'PASS_COORDINATE_AND_DRILL_COMPARISON_NOT_CAM_RELEASE',
        'native_kicad_version':pcb.GetBuildVersion(),'board_sha256':board_hash,
        'origin_native_mm':origin,'profile_centerline_mm':[30,51.6],
        'placement_matches_native_parts':len(positions),'via_drills_match_native':len(vias),
        'plated_slots_match_native':len(slots),'npth_match_native':len(npth),
        'excellon_numeric_comparison_tolerance_mm':0.00051,
        'maximum_drill_coordinate_or_size_error_mm':max(via_error,npth_error,slot_error),
        'limitations':'Native footprint anchors/angles are compared, not JLC placement translations. Copper/mask/paste Gerbers need independent CAM and DFM review.'}
    (ROOT/'reports/manufacturing_geometry_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
