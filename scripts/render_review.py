#!/usr/bin/env python3
"""Simple SVG view of generated schematics, NOT a KiCad plot or parser check."""
from pathlib import Path
from html import escape
from verify_design import parse_sexpr, child, children, atom

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'/'schematic_review'
OUT.mkdir(parents=True,exist_ok=True)

def txt(x,y,text,size=1,anchor='start',color='#222'):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{escape(text)}</text>'

def line(x1,y1,x2,y2,color='#156a4a',width=.18):
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="{width}" fill="none"/>'

def render(path):
    tree=parse_sexpr(path.read_text())
    lib={s[1]:s for s in children(child(tree,'lib_symbols'), 'symbol')}
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1188" viewBox="0 0 420 297">','<rect width="420" height="297" fill="white"/>','<g font-family="Arial, sans-serif">']
    svg.append(txt(10,10,'A0 REVIEW / custom SVG renderer / NOT a KiCad export / NOT FOR FABRICATION',1.5,color='#a32121'))
    for t in children(tree,'text'):
        at=child(t,'at');svg.append(txt(float(at[1]),float(at[2]),t[1],1.05))
    for wire in children(tree,'wire'):
        pts=children(child(wire,'pts'),'xy');svg.append(line(*map(float,pts[0][1:3]),*map(float,pts[1][1:3])))
    for inst in children(tree,'symbol'):
        sym=lib[atom(inst,'lib_id')];at=child(inst,'at');x,y=map(float,at[1:3])
        for sub in children(sym,'symbol'):
            for rect in children(sub,'rectangle'):
                a=child(rect,'start');b=child(rect,'end');x1,x2=sorted([x+float(a[1]),x+float(b[1])]);y1,y2=sorted([y-float(a[2]),y-float(b[2])])
                svg.append(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="#fff9dd" stroke="#8b1919" stroke-width=".18"/>')
            for poly in children(sub,'polyline'):
                pts=children(child(poly,'pts'),'xy')
                coords=[(x+float(p[1]),y-float(p[2])) for p in pts]
                for a,b in zip(coords,coords[1:]):svg.append(line(*a,*b,'#8b1919'))
            for pin in children(sub,'pin'):
                pa=child(pin,'at');px=x+float(pa[1]);py=y-float(pa[2]);isleft=float(pa[3])==0;d=2.54 if isleft else -2.54
                svg.append(line(px,py,px+d,py,'#8b1919'))
                svg.append(txt(px+d+(0.5 if isleft else -.5),py+.25,atom(pin,'name',''),.8,'start' if isleft else 'end','#2b6b69'))
                svg.append(txt(px+d/2,py-.3,atom(pin,'number',''),.75,'middle','#8b1919'))
        for p in children(inst,'property'):
            if p[1] not in ('Reference','Value'):continue
            a=child(p,'at');svg.append(txt(float(a[1]),float(a[2]),p[2],.95,'middle'))
    for label in children(tree,'global_label'):
        a=child(label,'at');x,y,angle=map(float,a[1:4]);svg.append(txt(x,y-.35,label[1],.9,'end' if angle==0 else 'start','#13663a'))
    for nc in children(tree,'no_connect'):
        a=child(nc,'at');x,y=map(float,a[1:3]);svg.append(line(x-.4,y-.4,x+.4,y+.4,'#1a4b9b'));svg.append(line(x-.4,y+.4,x+.4,y-.4,'#1a4b9b'))
    svg.append(txt(10,295,path.name+' / coordinates and pin labels read from .kicad_sch / review only',1.1))
    svg.append('</g></svg>')
    target=OUT/(path.stem+'.svg');target.write_text('\n'.join(svg));return target

paths=[ROOT/'hardware'/f'{name}.kicad_sch' for name in ['power','mcu','sensors','io','temperature']]
for p in paths:print(render(p).relative_to(ROOT))
index='<!doctype html><html lang="pl"><meta charset="utf-8"><title>Ankle Sensor - review schematu</title><style>body{font:16px system-ui;background:#eee;margin:24px}img{width:100%;background:white;border:1px solid #ccc}h2{margin-top:40px}</style><h1>Ankle Sensor V1 — przegląd schematu A0</h1><p>Własny renderer SVG, to nie eksport ani walidacja KiCad. NOT FOR FABRICATION.</p>'
for p in paths:index+=f'<h2>{p.stem}</h2><a href="{p.stem}.svg"><img src="{p.stem}.svg" alt="{p.stem}"></a>'
(OUT/'index.html').write_text(index)
