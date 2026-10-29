#!/usr/bin/env python3
"""Merge native PCB item blocks by UUID, relative to a frozen input file.

Preserves KiCad-written copper/footprint blocks byte-for-byte. This avoids
cross-board SWIG lifetime problems. Net tables must match; conflicting edits
fail closed. Native KiCad DRC remains mandatory after merging.
"""
from pathlib import Path
import argparse
from decimal import Decimal, InvalidOperation
import json
from verify_design import parse_sexpr, child, children

COPPER={'segment','via','arc'}

def norm(value):
    if isinstance(value,list):return tuple(norm(x) for x in value)
    try:return Decimal(value)
    except InvalidOperation:return value

def root_blocks(text):
    depth=0;quoted=False;escaped=False;start=None;blocks=[]
    for i,char in enumerate(text):
        if quoted:
            if escaped:escaped=False
            elif char=='\\':escaped=True
            elif char=='"':quoted=False
            continue
        if char=='"':quoted=True
        elif char=='(':
            if depth==1:start=i
            depth+=1
        elif char==')':
            depth-=1
            if depth==1 and start is not None:
                raw=text[start:i+1];node=parse_sexpr(raw)
                blocks.append((start,i+1,raw,node));start=None
    if depth or quoted:raise ValueError('Malformed PCB expressions')
    return blocks

def load(path):
    text=Path(path).read_text();blocks=root_blocks(text)
    copper={};footprints={};nets={}
    for _,_,raw,node in blocks:
        if node[0] in COPPER:
            uid=child(node,'uuid')[1]
            if uid in copper:raise ValueError('Duplicate copper UUID '+uid)
            copper[uid]=(raw,norm(node))
        elif node[0]=='footprint':
            props={p[1]:p[2] for p in children(node,'property')}
            ref=props.get('Reference')
            if not ref:raise ValueError('Footprint missing reference')
            footprints[ref]=(raw,(norm(child(node,'at')),norm(child(node,'layer'))))
        elif node[0]=='net':nets[node[1]]=node[2]
    return {'text':text,'blocks':blocks,'copper':copper,'footprints':footprints,'nets':nets}

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',required=True)
    p.add_argument('--repair',action='append',required=True)
    p.add_argument('--output',required=True);p.add_argument('--report',required=True)
    args=p.parse_args();base=load(args.base)
    copper=dict(base['copper']);fps=dict(base['footprints']);audit=[]
    for path in args.repair:
        repair=load(path)
        if repair['nets']!=base['nets']:raise ValueError('Changed net table: '+path)
        removed=set(base['copper'])-set(repair['copper'])
        modified={u for u in set(base['copper'])&set(repair['copper']) if base['copper'][u][1]!=repair['copper'][u][1]}
        added=set(repair['copper'])-set(base['copper'])
        for uid in removed|modified:
            desired=repair['copper'].get(uid);current=copper.get(uid)
            if current is None:
                if desired is None:continue
                raise ValueError('Deleted/modified conflict '+uid)
            if current[1]!=base['copper'][uid][1]:
                if desired is not None and current[1]==desired[1]:continue
                raise ValueError('Geometry conflict '+uid)
            copper.pop(uid)
            if desired is not None:copper[uid]=desired
        for uid in added:
            if uid in copper and copper[uid][1]!=repair['copper'][uid][1]:raise ValueError('New UUID conflict '+uid)
            copper[uid]=repair['copper'][uid]
        moved={}
        for ref,item in repair['footprints'].items():
            original=base['footprints'][ref]
            if item[1]==original[1]:continue
            if fps[ref][1]!=original[1] and fps[ref][1]!=item[1]:raise ValueError('Placement conflict '+ref)
            fps[ref]=item
            node=parse_sexpr(item[0]);at=child(node,'at')
            moved[ref]=[float(x) for x in at[1:]]
        audit.append({'repair':path,'removed':len(removed),'modified':len(modified),'added':len(added),'moved_footprints':moved})
    first=base['blocks'][0][0];last=base['blocks'][-1][1]
    out=[base['text'][:first]];written=set()
    for _,_,raw,node in base['blocks']:
        if node[0] in COPPER:
            uid=child(node,'uuid')[1]
            if uid in copper:out.append(copper[uid][0]);written.add(uid)
        elif node[0]=='footprint':
            ref=next(p[2] for p in children(node,'property') if p[1]=='Reference')
            out.append(fps[ref][0])
        else:out.append(raw)
    out.extend(copper[u][0] for u in sorted(set(copper)-written))
    out.append(base['text'][last:])
    merged='\n'.join(out);parse_sexpr(merged)
    Path(args.output).write_text(merged)
    Path(args.report).write_text(json.dumps({'status':'MERGED_REQUIRES_NATIVE_DRC','repairs':audit},indent=2)+'\n')
    print(json.dumps(audit,indent=2))

if __name__=='__main__':main()
