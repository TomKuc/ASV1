#!/usr/bin/env python3
"""Apply bounded local A1 audit repairs to a separate PCB, preserving routing.

Requires KiCad Python. Never overwrites its input. DRC is mandatory afterwards.
"""
from pathlib import Path
import argparse,hashlib,json,math
import pcbnew as pcb


def xy(v):
    return [round(pcb.ToMM(v.x),6),round(pcb.ToMM(v.y),6)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--findings',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args();src=a.input.resolve();out=a.output.resolve()
    assert src!=out,'Separate output required'
    source_hash=hashlib.sha256(src.read_bytes()).hexdigest()
    b=pcb.LoadBoard(str(src));items={t.m_Uuid.AsString():t for t in b.GetTracks()}
    changes=[]
    findings=json.loads(a.findings.read_text())
    for finding in findings['violations']:
        if finding['type']!='track_not_centered_on_via':continue
        t,v=[items[i['uuid']] for i in finding['items']]
        if t.GetClass()=='PCB_VIA':t,v=v,t
        assert t.GetClass()=='PCB_TRACK' and v.GetClass()=='PCB_VIA'
        assert t.GetNetCode()==v.GetNetCode()
        center=v.GetPosition();ends=[t.GetStart(),t.GetEnd()]
        distance=[math.hypot(q.x-center.x,q.y-center.y) for q in ends]
        index=min(range(2),key=lambda i:distance[i])
        assert 0<distance[index]<=pcb.FromMM(.10)
        changes.append({'kind':'center_track_endpoint','uuid':t.m_Uuid.AsString(),
            'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),
            'from_mm':xy(ends[index]),'to_mm':xy(center),'delta_mm':distance[index]/1e6})
        (t.SetStart if index==0 else t.SetEnd)(center)
    for net,old,new in [('QSPI_IO3',(71.85,73.9),(71.85,73.76)),
                        ('VBUS',(66.45,94.0),(66.45,93.93))]:
        before=pcb.VECTOR2I(pcb.FromMM(old[0]),pcb.FromMM(old[1]))
        after=pcb.VECTOR2I(pcb.FromMM(new[0]),pcb.FromMM(new[1]))
        candidates=[v for v in b.GetTracks() if v.GetClass()=='PCB_VIA'
                    and v.GetNetname()==net and v.GetPosition()==before]
        assert len(candidates)==1,(net,candidates)
        v=candidates[0]
        touched=[]
        for t in b.GetTracks():
            if t.GetClass()!='PCB_TRACK' or t.GetNetCode()!=v.GetNetCode():continue
            for getter,setter in ((t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)):
                if getter()==before:
                    setter(after);touched.append(t.m_Uuid.AsString())
        assert len(touched)==2,(net,touched)
        v.SetPosition(after)
        changes.append({'kind':'move_via_and_connected_endpoints','uuid':v.m_Uuid.AsString(),
                        'net':net,'from_mm':list(old),'to_mm':list(new),
                        'connected_tracks':touched,'diameter_mm':pcb.ToMM(v.GetWidth(pcb.F_Cu)),
                        'drill_mm':pcb.ToMM(v.GetDrill())})
    pcb.SaveBoard(str(out),b)
    assert hashlib.sha256(src.read_bytes()).hexdigest()==source_hash
    a.report.write_text(json.dumps({'status':'LOCAL_REPAIR_REQUIRES_NATIVE_DRC_AND_FAB_REVIEW',
        'source_sha256':source_hash,'source_unchanged':True,'changes':changes,
        'footprints_moved':0,'vias_added_or_removed':0,'tracks_added_or_removed':0,
        'routing_strategy':'Only bounded endpoint adjustments and two existing via positions; no autorouter'},indent=2)+'\n')
    print('Centered',len(changes)-2,'endpoints; moved2existingvias. Input preserved.')


if __name__=='__main__':main()
