#!/usr/bin/env python3
"""Vendor only used KiCad footprints and available models into the project."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import os

ROOT=Path(__file__).resolve().parents[1]
HW=ROOT/'hardware'
APP=Path(os.environ.get('ANKLE_KICAD_APP','/Applications/KiCad/KiCad.app'))
LIBS=APP/'Contents/SharedSupport/footprints'
MODELS=APP/'Contents/SharedSupport/3dmodels'
DEST=HW/'footprints/AnkleSensor.pretty'
THREED=HW/'3dmodels'

def main():
    DEST.mkdir(parents=True,exist_ok=True);THREED.mkdir(exist_ok=True)
    design=json.loads((HW/'design.json').read_text())
    choices=json.loads((HW/'component_choices.json').read_text())
    audit=[]
    for c in design['components']:
        if c['ref'].startswith('#'):continue
        footprint=c['footprint']
        if not footprint:raise ValueError('Missing footprint for '+c['ref'])
        lib,name=footprint.split(':',1)
        source=DEST/(name+'.kicad_mod') if lib=='AnkleSensor' else LIBS/(lib+'.pretty')/(name+'.kicad_mod')
        target=DEST/(name+'.kicad_mod')
        content=source.read_text()
        item={'ref':c['ref'],'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target':str(target.relative_to(ROOT)),'models':[]}
        for match in list(re.finditer(r'\(model "([^"]+)"',content)):
            old=match.group(1)
            if old.startswith('${KIPRJMOD}/'):
                model=HW/old[len('${KIPRJMOD}/'):]
                item['models'].append({'path':old,'available':model.is_file()});continue
            if not old.startswith('${KICAD10_3DMODEL_DIR}/'):continue
            rel=old[len('${KICAD10_3DMODEL_DIR}/'):]
            model=MODELS/rel
            # The installed bundle can contain .step rather than .stp or vice versa.
            if not model.exists():
                alt=model.with_suffix('.step' if model.suffix=='.stp' else '.stp')
                if alt.exists():model=alt
            if model.exists():
                local=THREED/(Path(rel).parent.name+'_'+model.name)
                if not local.exists():shutil.copy2(model,local)
                new='${KIPRJMOD}/3dmodels/'+local.name
                content=content.replace('"'+old+'"','"'+new+'"')
                item['models'].append({'path':new,'available':True})
            else:item['models'].append({'path':old,'available':False})
        target.write_text(content)
        choices.setdefault(c['ref'],{})['footprint']='AnkleSensor:'+name
        audit.append(item)
    (HW/'component_choices.json').write_text(json.dumps(choices,indent=2)+'\n')
    (HW/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "AnkleSensor") (type "KiCad") (uri "${KIPRJMOD}/footprints/AnkleSensor.pretty") (options "") (descr "Vendored KiCad footprints and documented project variants")))\n')
    (ROOT/'reports/footprint_inventory.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('Prepared',len(audit),'footprint assignments; check inventory for unavailable3D models.')

if __name__=='__main__':main()
