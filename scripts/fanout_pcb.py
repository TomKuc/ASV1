#!/usr/bin/env python3
"""Explicit first-layer fanouts and local power loops before trunk routing.

Uses exact native pad coordinates. Run on an unrouted placement checkpoint,
then perform native DRC. These are reviewable tracks, not a DRC exemption.
"""
from pathlib import Path
import argparse
import json
import pcbnew as pcb

ROOT=Path(__file__).resolve().parents[1]

def v(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('input');parser.add_argument('output')
    args=parser.parse_args();board=pcb.LoadBoard(args.input)
    fps={f.GetReference():f for f in board.GetFootprints()}
    records=[]
    def pad(ref,pin):return next(p for p in fps[ref].Pads() if p.GetNumber()==str(pin))
    def xy(p):return (pcb.ToMM(p.GetPosition().x),pcb.ToMM(p.GetPosition().y))
    def track(p,points,width=.15):
        for a,b in zip(points,points[1:]):
            if a==b:continue
            t=pcb.PCB_TRACK(board);t.SetStart(v(*a));t.SetEnd(v(*b));t.SetLayer(pcb.F_Cu)
            t.SetWidth(pcb.FromMM(width));t.SetNet(p.GetNet());board.Add(t)
        records.append({'net':p.GetNetname(),'points_mm':points,'width_mm':width})
    def via(p,point):
        t=pcb.PCB_VIA(board);t.SetPosition(v(*point));t.SetWidth(pcb.FromMM(.5));t.SetDrill(pcb.FromMM(.25))
        t.SetLayerPair(pcb.F_Cu,pcb.B_Cu);t.SetViaType(pcb.VIATYPE_THROUGH);t.SetNet(p.GetNet())
        t.SetFrontTentingMode(pcb.TENTING_MODE_TENTED);t.SetBackTentingMode(pcb.TENTING_MODE_TENTED)
        board.Add(t)
    # Inner and outer module pin columns need different escape directions.
    # Put their layer transitions down before another net can fence them in.
    for pin in [4,6,11,36,38,40,53]:
        p=pad('U3',pin);x,y=xy(p);cx=pcb.ToMM(fps['U3'].GetPosition().x)
        relative=x-cx;sign=1 if relative>0 else -1
        dx=.85*sign*(1 if abs(relative)>4.2 else -1)
        endpoint=(round(x+dx,5),y)
        track(p,[(x,y),endpoint]);via(p,endpoint)
    for pin in [12,14]:
        p=pad('U4',pin);x,y=xy(p);endpoint=(x,74.5)
        track(p,[(x,y),endpoint]);via(p,endpoint)
    # BQ25185 power path: controlled short connections to local bypass caps.
    p=pad('U1',1);end=xy(pad('C2',1))
    track(p,[xy(p),(61.3,91.4)])
    track(p,[(61.3,91.4),(61.3,end[1]+.3),end],.3)
    p=pad('U1',2);end=xy(pad('C3',1))
    track(p,[xy(p),(60.825,91.8)])
    track(p,[(60.825,91.8),end],.3)
    p=pad('U1',10);end=xy(pad('C1',1))
    track(p,[xy(p),(xy(p)[0],end[1])])
    track(p,[(xy(p)[0],end[1]),end],.3)
    # STAT1 and STAT2 escape on opposite sides of the fine-pitch package.
    p=pad('U1',9);endpoint=(64.8,91.65)
    track(p,[xy(p),(64.65,91.8),endpoint]);via(p,endpoint)
    p=pad('U1',3);endpoint=(61.1,93.1)
    track(p,[xy(p),(61.35,92.2),(61.35,92.85),endpoint]);via(p,endpoint)
    p=pad('U1',8);track(p,[xy(p),xy(pad('R2',1))])
    p=pad('U1',7);track(p,[xy(p),(64.7,92.6),(65.3,93.2),xy(pad('R1',1))])
    # Connect the separate charger ground pin into its thermal return.
    p=pad('U1',5);track(p,[xy(p),(62.4,93),(62.8,93.4),(63,93.4)],.2)
    # LDO input/output capacitors sit directly ahead of the respective pins.
    for pin,cap in [(1,'C4'),(5,'C5')]:
        p=pad('U2',pin);track(p,[xy(p),xy(pad(cap,1))],.3)
        ground=pad(cap,2);start=xy(ground);endpoint=(start[0],78.3)
        track(ground,[start,endpoint],.2);via(ground,endpoint)
    p=pad('U2',1)
    track(p,[xy(p),(67.95,xy(p)[1]),(67.95,xy(pad('U2',3))[1]),xy(pad('U2',3))],.3)
    p=pad('U2',2);endpoint=(70.3,83)
    track(p,[xy(p),endpoint],.2);via(p,endpoint)
    board.BuildConnectivity();pcb.SaveBoard(args.output,board)
    (ROOT/'reports/explicit_fanout.json').write_text(json.dumps({'status':'REQUIRES_NATIVE_DRC','connections':records},indent=2)+'\n')
    print('Explicit fanouts and local loops:',len(records),'connections. Run KiCad DRC before trunk routing.')

if __name__=='__main__':main()
