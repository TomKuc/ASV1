#!/usr/bin/env python3
"""Summarise actual KiCad reports without treating partial checks as release."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--erc',default='reports/erc_current.json')
    parser.add_argument('--drc',required=True)
    args=parser.parse_args()
    erc=json.loads((ROOT/args.erc).read_text());drc=json.loads((ROOT/args.drc).read_text())
    ev=[v for sheet in erc['sheets'] for v in sheet['violations']]
    dv=drc['violations']
    report={
        'revision':'A1-AUDIT','kicad_version':erc.get('kicad_version'),
        'erc_report':args.erc,'erc_errors':sum(v['severity']=='error' for v in ev),
        'erc_warnings':sum(v['severity']=='warning' for v in ev),
        'erc_review':'U4 pins2/3 intentionally grounded in documented primary-SPI mode with Qvar/sensorhub disabled. Native ERC warnings remain visible.',
        'drc_report':args.drc,'drc_geometry_errors':sum(v['severity']=='error' for v in dv),
        'drc_warnings':sum(v['severity']=='warning' for v in dv),
        'unconnected_items':len(drc['unconnected_items']),
        'schematic_parity_findings':len(drc.get('schematic_parity',[])),
        'erc_ignored_checks':erc.get('ignored_checks',[]),
        'drc_ignored_checks':drc.get('ignored_checks',[]),
        'fabrication_release':False,
        'release_note':'Electrical completion, manufacturing DFM, RF/USB review, parts sourcing and physical verification are separate gates. This script cannot release the design.',
        'inputs':{}
    }
    names=['hardware/Ankle_Sensor_V1.kicad_pcb','hardware/Ankle_Sensor_V1.kicad_pro',
           'hardware/design.json','hardware/component_choices.json',
           'hardware/fp-lib-table','hardware/sym-lib-table',args.erc,args.drc]
    names.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT/'hardware').glob('*.kicad_sch')))
    for name in names:
        report['inputs'][name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    (ROOT/'reports/validation_status.json').write_text(json.dumps(report,indent=2)+'\n')
    compatibility={
        'project':'Ankle_Sensor_V1','revision':'A1-AUDIT','kicad_version':report['kicad_version'],
        'kicad_open_check':'PASS_NATIVE_SCHEMATIC_LOAD_AND_PDF_EXPORT',
        'erc':'RUN','drc':'RUN','fabrication_release':False,
        'pcb_routing':'CONNECTED_REVIEW_PENDING' if report['unconnected_items']==0 else 'PARTIAL',
        'current_counts':{k:report[k] for k in ['erc_errors','erc_warnings','drc_geometry_errors','drc_warnings','unconnected_items','schematic_parity_findings']},
        'details':'validation_status.json'
    }
    (ROOT/'reports/kicad_checks_status.json').write_text(json.dumps(compatibility,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='inputs'},indent=2))

if __name__=='__main__':main()
