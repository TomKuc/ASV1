#!/usr/bin/env python3
"""Verify the precise C9-only delta against the preserved native A1 source."""
from pathlib import Path
import sys,zipfile,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from merge_pcb_repairs import load,norm
from verify_design import parse_sexpr
r=Path(__file__).resolve().parents[1]; (r/'.work/production_closure').mkdir(parents=True,exist_ok=True);before=r/'.work/production_closure/board_before.kicad_pcb';zpath=r/'reports/baselines/A1_before_production_closure_2026-10-29.zip'
with zipfile.ZipFile(zpath) as z:before.write_bytes(z.read('hardware/Ankle_Sensor_V1.kicad_pcb'))
a=load(before);b=load(r/'hardware/Ankle_Sensor_V1.kicad_pcb');assert a['nets']==b['nets'];assert a['copper'].keys()==b['copper'].keys()
assert all(a['copper'][u][1]==b['copper'][u][1] for u in a['copper']);assert a['footprints'].keys()==b['footprints'].keys()
changed=[]
for ref in a['footprints']:
 if a['footprints'][ref][1]!=b['footprints'][ref][1]:
  assert ref=='C9';changed.append(ref)
  nodes=[]
  for fp in [a['footprints'][ref][0],b['footprints'][ref][0]]:
   n=parse_sexpr(fp);nodes.append(norm([x for x in n if not(isinstance(x,list) and x[0]=='property' and x[1] in ['Value','MPN','JLCPCB','Note'])]))
  assert nodes[0]==nodes[1]
assert changed==['C9']
others=lambda q:norm([x[3] for x in q['blocks'] if x[3][0] not in ['footprint','segment','arc','via']])
assert others(a)==others(b)
j={'status':'PASS_NATIVE_CAD_GEOMETRY_IDENTICAL_EXCEPT_C9_PROPERTY_TEXT','before_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256((r/'hardware/Ankle_Sensor_V1.kicad_pcb').read_bytes()).hexdigest(),'same_net_table':True,'all_copper_uuid_geometry_layer_width_net_unchanged':True,'all_pads_footprint_positions_layers_and_models_unchanged':True,'all_other_root_blocks_including_filled_zones_unchanged':True,'changed_footprints':['C9'],'allowed_C9_property_changes':['Value','MPN','JLCPCB','Note'],'copper_items_checked':len(a['copper']),'footprints_checked':len(a['footprints']),'method':'Parse complete native S-expressions; decimal-normalised UUID blocks and full footprint nodes; only four C9 text properties excluded. Not a PDN simulation or hardware test.','before_archive':str(zpath.relative_to(r)),'before_archive_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'hardware_tested':False}
(r/'reports/production_geometry_equivalence_A1.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j))
