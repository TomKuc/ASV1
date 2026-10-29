#!/usr/bin/env python3
"""Read-only check of stored native copper fill, not only keepout declarations."""
from pathlib import Path
import hashlib
import json
import pcbnew

ROOT=Path(__file__).resolve().parents[1]


def rectangle(x0,y0,x1,y1):
    p=pcbnew.SHAPE_POLY_SET()
    p.NewOutline()
    for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):
        p.Append(pcbnew.FromMM(x),pcbnew.FromMM(y))
    return p


def intersection_area(a,b):
    p=pcbnew.SHAPE_POLY_SET()
    p.BooleanIntersection(a,b)
    return round(p.Area()/1e12,9)


def main():
    path=ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb'
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    board=pcbnew.LoadBoard(str(path))
    full=rectangle(57.8,49.8,70.2,55.0)
    front=rectangle(57.8,50.0,70.2,51.25)
    control=rectangle(50.5,50.5,56.5,54.5)
    expected_layers={pcbnew.F_Cu,pcbnew.B_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu}
    keepouts=[]
    results=[]
    checked=set()
    for z in board.Zones():
        layers=set(z.GetLayerSet().Seq())
        if z.GetIsRuleArea():
            area=intersection_area(z.Outline(),full)
            if area>64.479:
                keepouts.append({'layers':[board.GetLayerName(l) for l in sorted(layers)],
                    'coverage_area_mm2':area,'tracks_forbidden':z.GetDoNotAllowTracks(),
                    'vias_forbidden':z.GetDoNotAllowVias(),'pads_forbidden':z.GetDoNotAllowPads(),
                    'zone_fills_forbidden':z.GetDoNotAllowZoneFills()})
                assert expected_layers <= layers
                assert z.GetDoNotAllowTracks() and z.GetDoNotAllowVias()
                assert z.GetDoNotAllowPads() and z.GetDoNotAllowZoneFills()
            continue
        for layer in sorted(layers & {pcbnew.In1_Cu,pcbnew.In2_Cu}):
            fill=z.GetFilledPolysList(layer)
            assert z.IsFilled() and fill.OutlineCount()>0
            front_area=intersection_area(fill,front)
            full_area=intersection_area(fill,full)
            outside_control=intersection_area(fill,control)
            assert front_area==0 and full_area==0
            assert outside_control>0
            hits=[]
            # Independent point checks strictly inside the antenna-front strip.
            for x in (58.0,60.0,62.0,64.0,66.0,68.0,70.0):
                for y in (50.1,50.4,50.7,51.0,51.2):
                    point=pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
                    if fill.Contains(point):
                        hits.append([x,y])
            assert not hits
            results.append({'layer':board.GetLayerName(layer),'net':z.GetNetname(),
                'stored_fill_outline_count':fill.OutlineCount(),
                'stored_fill_area_mm2':round(fill.Area()/1e12,6),
                'full_keepout_copper_intersection_mm2':full_area,
                'antenna_front_strip_copper_intersection_mm2':front_area,
                'positive_control_copper_area_mm2':outside_control,
                'front_strip_samples':35,'sample_copper_hits':hits})
            checked.add(layer)
    assert keepouts and checked=={pcbnew.In1_Cu,pcbnew.In2_Cu}
    result={'date':'2026-10-28','board_sha256_at_read':digest,
        'native_kicad_version':pcbnew.GetBuildVersion(),
        'method':'Native SHAPE_POLY_SET BooleanIntersection of stored fill including holes; independent Contains samples.',
        'status':'PASS_FOR_CURRENT_STORED_FILL_NOT_RF_QUALIFICATION_OR_FABRICATION_RELEASE',
        'keepout_rectangle_mm':[57.8,49.8,70.2,55.0],
        'front_strip_rectangle_mm':[57.8,50.0,70.2,51.25],
        'keepouts':keepouts,'filled_layers':results}
    (ROOT/'reports/rf_filled_copper_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
