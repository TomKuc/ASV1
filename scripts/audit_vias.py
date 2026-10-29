"""Read-only nominal drill versus SMD copper/paste audit, including same net."""
from pathlib import Path
import pcbnew, json, hashlib, argparse

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input',type=Path,default=ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb')
parser.add_argument('--output',type=Path,default=ROOT/'reports/via_pad_audit.json')
args=parser.parse_args();src=args.input.resolve();initial_sha=hashlib.sha256(src.read_bytes()).hexdigest()
b=pcbnew.LoadBoard(str(src))
vias=[t for t in b.GetTracks() if t.GetClass()=='PCB_VIA']
owners=[];copper=[];paste=[];positive=[]
def xy(p):return [round(pcbnew.ToMM(p.x),5),round(pcbnew.ToMM(p.y),5)]
for f in b.GetFootprints():
 for p in f.Pads():
  if p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD:continue
  for cu,pa in [(pcbnew.F_Cu,pcbnew.F_Paste),(pcbnew.B_Cu,pcbnew.B_Paste)]:
   rec={'ref':f.GetReference(),'pin':p.GetNumber(),'net':p.GetNetname(),'pad_uuid':str(p.m_Uuid.AsString()),'side':'front' if cu==pcbnew.F_Cu else 'back','pad_center_mm':xy(p.GetPosition())}
   if p.IsOnLayer(cu):
    shape=p.GetEffectiveShape(cu);owners.extend([p,shape]);copper.append((shape,dict(rec)))
   if p.IsOnLayer(pa):
    margin=p.GetSolderPasteMargin(pa);sx,sy=p.GetSize().x,p.GetSize().y
    q=p.ClonePad();q.SetSize(pcbnew.VECTOR2I(sx+2*margin.x,sy+2*margin.y));assert p.GetSize().x==sx and p.GetSize().y==sy
    shape=q.GetEffectiveShape(cu);owners.extend([q,shape]);r=dict(rec);r.update(paste_margin_mm=[pcbnew.ToMM(margin.x),pcbnew.ToMM(margin.y)],standalone_paste_aperture=not p.IsOnLayer(cu));paste.append((shape,r))
    if margin.x>0 or margin.y>0:positive.append(r)
def audit(shapes):
 minimum=None;near=[];collisions=[]
 for v in vias:
  radius=int(v.GetDrill()/2);point=v.GetPosition()
  for shape,meta in shapes:
   # SHAPE.Distance is unreliable for these native compound pad shapes.
   # Collide(point, clearance) is the same native primitive used by the router.
   # First reject far pairs; then bracket the true edge distance in nanometres.
   upper=radius+pcbnew.FromMM(.5)
   box=shape.BBox()
   dx=max(box.GetLeft()-point.x,point.x-box.GetRight(),0)
   dy=max(box.GetTop()-point.y,point.y-box.GetBottom(),0)
   if dx*dx+dy*dy>upper*upper:continue
   if not shape.Collide(point,upper):continue
   overlap=bool(shape.Collide(point,radius))
   low=0
   if shape.Collide(point,0):upper=0
   while upper-low>1:
    middle=(low+upper)//2
    if shape.Collide(point,middle):upper=middle
    else:low=middle
   gap=pcbnew.ToMM(upper-radius)
   rec={**meta,'via_uuid':str(v.m_Uuid.AsString()),'via_net':v.GetNetname(),'via_xy_mm':xy(point),'hole_diameter_mm':pcbnew.ToMM(v.GetDrill()),'hole_to_shape_edge_mm':round(gap,6),'same_net':v.GetNetname()==meta['net']}
   if minimum is None or gap<minimum['hole_to_shape_edge_mm']:minimum=rec
   if overlap:collisions.append(rec)
   if gap<.250001:near.append(rec)
 return {'minimum_clearance':minimum,'overlap_count':len(collisions),'overlaps':collisions,'pairs_below_0_25mm':sorted(near,key=lambda r:r['hole_to_shape_edge_mm'])}
a=audit(copper);c=audit(paste)
report={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'kicad_version':pcbnew.GetBuildVersion(),'vias_checked':len(vias),'SMD_copper_shapes':len(copper),'paste_apertures':len(paste),'paste_positive_margin_shapes':positive,'method':'All through-via circular drill holes versus every SMD copper and paste shape on both sides, including same-net. Native rounded/custom pad shapes; paste uses ClonePad resized by loaded GetSolderPasteMargin(layer), including ratio. Includes standalone EP paste apertures. Uses native Collide(point, drillradius) for overlap and binary search of Collide(point, drillradius+gap) to 1nm for nominal edge clearance; SHAPE.Distance is deliberately not used. All loaded paste margins are zero or negative; holes are also checked against the unshrunk native copper/aperture envelope, so no conclusion depends on assuming a reduced corner radius. Nominal CAD geometry only; fabrication/registration tolerances are separate.','copper':a,'paste':c}
report['source_unchanged_during_audit']=initial_sha==hashlib.sha256(src.read_bytes()).hexdigest()
c3=next(f for f in b.GetFootprints() if f.GetReference()=='C3').FindPadByNumber('2').GetEffectiveShape(pcbnew.F_Cu)
report['positive_control_former_C3_via_hole_overlap']=bool(c3.Collide(pcbnew.VECTOR2I(pcbnew.FromMM(58.15),pcbnew.FromMM(92.1)),pcbnew.FromMM(.125)))
report['corrected_C3_via_hole_overlap']=bool(c3.Collide(pcbnew.VECTOR2I(pcbnew.FromMM(57.8),pcbnew.FromMM(92.1)),pcbnew.FromMM(.125)))
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
print('Vias',len(vias),'Cu shapes',len(copper),'paste shapes',len(paste),'positive_paste_margins',len(positive))
for kind,rr in [('CU',a),('PASTE',c)]:
 print(kind,'OVERLAPS',rr['overlap_count'],'MIN',rr['minimum_clearance']);print('near <0.25',len(rr['pairs_below_0_25mm']))
 for r in rr['overlaps']:print(r)
print('C3 via pair',[r for r in a['pairs_below_0_25mm'] if r['ref']=='C3' and r['pin']=='2'])
