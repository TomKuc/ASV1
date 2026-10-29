#!/usr/bin/env python3
"""Read-only survey of actual stored native plane fill below signal tracks.

Geometry checks are not impedance, return-current or USB compliance simulation.
"""
from pathlib import Path
import collections, hashlib, json, math
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
STEP=.01
POLY_ERROR=.001
GROUPS={
 'USB_MCU':['USB_DP','USB_DN'],
 'USB_CONNECTOR':['USB_DP_CONN','USB_DN_CONN'],
 'IMU':['IMU_SCK','IMU_MOSI','IMU_MISO','IMU_CS_N','IMU_INT1','IMU_INT2'],
 'QSPI':['QSPI_SCK','QSPI_CLK_FLASH','QSPI_IO0','QSPI_IO1','QSPI_IO2','QSPI_IO3','FLASH_CS_N']}

def mm(v):return pcbnew.ToMM(v)
def box(poly):
 b=poly.BBox();return [mm(b.GetLeft()),mm(b.GetTop()),mm(b.GetRight()),mm(b.GetBottom())]
def area(poly):return poly.Area()/1e12
def native_intersection(a,b):
 p=pcbnew.SHAPE_POLY_SET();p.BooleanIntersection(a,b);return p
def native_subtract(a,b):
 p=pcbnew.SHAPE_POLY_SET();p.BooleanSubtract(a,b);return p
def projection(tracks,band_width=None):
 out=pcbnew.SHAPE_POLY_SET()
 for t in tracks:
  p=pcbnew.SHAPE_POLY_SET()
  expand=0 if band_width is None else max(0,(band_width-mm(t.GetWidth()))/2)
  t.TransformShapeToPolygon(p,t.GetLayer(),pcbnew.FromMM(expand),pcbnew.FromMM(POLY_ERROR),pcbnew.ERROR_OUTSIDE)
  out.BooleanAdd(p)
 return out
def missing_reference_components(tracks,fill):
 """Join sampled missing intervals along continuous tracks on one layer."""
 graph=collections.defaultdict(list)
 for t in tracks:
  a,z=t.GetStart(),t.GetEnd();length=mm(t.GetLength());n=max(1,math.ceil(length/STEP));bad=[]
  for i in range(n):
   f=(i+.5)/n;p=pcbnew.VECTOR2I(round(a.x+(z.x-a.x)*f),round(a.y+(z.y-a.y)*f));bad.append(not fill.Contains(p))
  i=0
  while i<n:
   if not bad[i]:i+=1;continue
   j=i+1
   while j<n and bad[j]:j+=1
   u=(round(a.x+(z.x-a.x)*i/n),round(a.y+(z.y-a.y)*i/n));v=(round(a.x+(z.x-a.x)*j/n),round(a.y+(z.y-a.y)*j/n));w=length*(j-i)/n;graph[u].append((v,w));graph[v].append((u,w));i=j
 seen=set();components=[]
 for seed in graph:
  if seed in seen:continue
  todo=[seed];nodes=[];total=0
  while todo:
   q=todo.pop()
   if q in seen:continue
   seen.add(q);nodes.append(q)
   for p,d in graph[q]:total+=d;todo.append(p)
  xs=[mm(q[0]) for q in nodes];ys=[mm(q[1]) for q in nodes]
  components.append({'estimated_missing_trace_length_sum_mm':total/2,'bbox_mm':[min(xs),min(ys),max(xs),max(ys)],'max_graph_degree':max(len(graph[q]) for q in nodes)})
 return sorted(components,key=lambda c:c['estimated_missing_trace_length_sum_mm'],reverse=True)
def net_geometry(board,tracks,vias,gnd,adjacent_power):
 layers=collections.defaultdict(float);widths=collections.Counter();runs=[];graph=collections.defaultdict(list)
 max_missing_distance=0;missing_outside_own_via_probe=0
 for t in tracks:
  start,end=t.GetStart(),t.GetEnd();x0,y0,x1,y1=[mm(v) for v in [start.x,start.y,end.x,end.y]]
  length=mm(t.GetLength());layer=t.GetLayer();layers[board.GetLayerName(layer)]+=length;widths[f'{mm(t.GetWidth()):.3f}']+=1
  n=max(1,math.ceil(length/STEP));step=length/n
  states=[]
  for i in range(n):
   f=(i+.5)/n;p=pcbnew.VECTOR2I(round(start.x+(end.x-start.x)*f),round(start.y+(end.y-start.y)*f));absent=not gnd.Contains(p);states.append(absent)
   if absent:
    distances=[math.hypot(mm(p.x-v.GetPosition().x),mm(p.y-v.GetPosition().y)) for v in vias]
    d=min(distances) if distances else float('inf');max_missing_distance=max(max_missing_distance,d)
    if not distances or d>.42:missing_outside_own_via_probe+=1
  i=0
  while i<n:
   if not states[i]:i+=1;continue
   j=i+1
   while j<n and states[j]:j+=1
   a=(round(start.x+(end.x-start.x)*i/n),round(start.y+(end.y-start.y)*i/n),layer)
   z=(round(start.x+(end.x-start.x)*j/n),round(start.y+(end.y-start.y)*j/n),layer)
   length_bad=(j-i)*step;graph[a].append((z,length_bad));graph[z].append((a,length_bad))
   runs.append({'track_uuid':t.m_Uuid.AsString(),'layer':board.GetLayerName(layer),'start_mm':[mm(a[0]),mm(a[1])],'end_mm':[mm(z[0]),mm(z[1])],'estimated_length_mm':length_bad})
   i=j
 # A through via joins the missing trace-projection intervals at the same XY.
 byxy=collections.defaultdict(list)
 for p in graph:byxy[p[:2]].append(p)
 for v in vias:
  p=v.GetPosition();nodes=byxy.get((p.x,p.y),[])
  for a,z in zip(nodes,nodes[1:]):graph[a].append((z,0));graph[z].append((a,0))
 seen=set();components=[]
 for seed in graph:
  if seed in seen:continue
  todo=[seed];nodes=[];total=0
  while todo:
   q=todo.pop()
   if q in seen:continue
   seen.add(q);nodes.append(q)
   for z,w in graph[q]:total+=w;todo.append(z)
  xs=[mm(q[0]) for q in nodes];ys=[mm(q[1]) for q in nodes]
  bb=[min(xs),min(ys),max(xs),max(ys)]
  near=[]
  for v in board.Tracks():
   if v.Type()!=pcbnew.PCB_VIA_T or v.GetNetname()=='GND':continue
   p=v.GetPosition();x,y=mm(p.x),mm(p.y)
   dx=max(bb[0]-x,0,x-bb[2]);dy=max(bb[1]-y,0,y-bb[3]);d=math.hypot(dx,dy)
   if d<=.50:near.append({'net':v.GetNetname(),'xy_mm':[x,y],'diameter_mm':mm(v.GetWidth(pcbnew.In1_Cu)),'distance_to_gap_bbox_mm':d})
  components.append({'estimated_missing_trace_length_sum_mm':total/2,'bbox_mm':bb,'bbox_diagonal_mm':math.hypot(bb[2]-bb[0],bb[3]-bb[1]),'max_graph_degree':max(len(graph[q]) for q in nodes),'nearby_non_ground_through_vias':near})
 proj=projection(tracks);inter=native_intersection(proj,gnd);missing=native_subtract(proj,gnd)
 own_antipad_probe=pcbnew.SHAPE_POLY_SET()
 for v in vias:
  p=pcbnew.SHAPE_POLY_SET();v.TransformShapeToPolygon(p,pcbnew.In1_Cu,pcbnew.FromMM(.17),pcbnew.FromMM(POLY_ERROR),pcbnew.ERROR_OUTSIDE);own_antipad_probe.BooleanAdd(p)
 unexplained=native_subtract(missing,own_antipad_probe)
 unexplained_components=[]
 for i in range(unexplained.OutlineCount()):
  p=pcbnew.SHAPE_POLY_SET();p.AddOutline(unexplained.Outline(i));unexplained_components.append({'area_mm2':area(p),'bbox_mm':box(p)})
 band=projection(tracks,.5);bandgnd=native_intersection(band,gnd)
 missingcomponents=[]
 for i in range(missing.OutlineCount()):
  p=pcbnew.SHAPE_POLY_SET();p.AddOutline(missing.Outline(i));missingcomponents.append({'area_mm2':area(p),'bbox_mm':box(p)})
 out={'track_count':len(tracks),'trace_length_mm':sum(layers.values()),'trace_length_by_layer_mm':dict(layers),'trace_width_segment_counts_mm':dict(widths),'via_count':len(vias),'native_projection_area_mm2':area(proj),'native_projection_over_gnd_mm2':area(inter),'native_projection_without_gnd_mm2':area(missing),'native_projection_gnd_coverage_pct':min(100,100*area(inter)/area(proj)),'native_projection_without_gnd_outside_own_via_0p42mm_probe_mm2':area(unexplained),'projection_without_gnd_outside_own_via_probe_components':unexplained_components,'missing_centerline_max_distance_to_own_via_mm':max_missing_distance,'missing_centerline_samples_outside_own_via_0p42mm_probe':missing_outside_own_via_probe,'survey_band_width_mm':.5,'native_survey_band_area_mm2':area(band),'native_survey_band_over_gnd_mm2':area(bandgnd),'native_survey_band_gnd_coverage_pct':min(100,100*area(bandgnd)/area(band)),'estimated_centerline_without_gnd_total_mm':sum(r['estimated_length_mm'] for r in runs),'max_missing_component_trace_length_sum_mm':max([c['estimated_missing_trace_length_sum_mm'] for c in components] or [0]),'centerline_missing_components':sorted(components,key=lambda c:c['estimated_missing_trace_length_sum_mm'],reverse=True),'projection_missing_area_components':sorted(missingcomponents,key=lambda c:c['area_mm2'],reverse=True),'centerline_missing_runs':runs}
 btracks=[t for t in tracks if t.GetLayer()==pcbnew.B_Cu]
 if btracks:
  bp=projection(btracks);inter=native_intersection(bp,adjacent_power)
  out['b_cu_adjacent_in2_power_projection_coverage_pct']=100*area(inter)/area(bp)
  out['b_cu_adjacent_in2_power_missing_centerline_components']=missing_reference_components(btracks,adjacent_power)
 if not math.isfinite(max_missing_distance):out['missing_centerline_max_distance_to_own_via_mm']=None
 return out

def main():
 path=ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb';before=hashlib.sha256(path.read_bytes()).hexdigest();board=pcbnew.LoadBoard(str(path));board.BuildConnectivity()
 ground=next(z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.IsOnLayer(pcbnew.In1_Cu));gnd=ground.GetFilledPolysList(pcbnew.In1_Cu)
 power=next(z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='+3V0' and z.IsOnLayer(pcbnew.In2_Cu));pwr=power.GetFilledPolysList(pcbnew.In2_Cu)
 assert ground.IsFilled() and power.IsFilled() and gnd.OutlineCount()>0 and pwr.OutlineCount()>0
 nets={}
 for group,names in GROUPS.items():
  for name in names:
   tracks=[t for t in board.Tracks() if t.GetNetname()==name and t.Type()!=pcbnew.PCB_VIA_T];vias=[t for t in board.Tracks() if t.GetNetname()==name and t.Type()==pcbnew.PCB_VIA_T]
   if tracks:nets[name]=net_geometry(board,tracks,vias,gnd,pwr)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==before
 stable_usb_report=json.loads((ROOT/'reports/usb_routing_review.json').read_text())
 stable_usb=stable_usb_report['verified_mcu_proposal']
 usbsource={'board_sha256':stable_usb['proposal_board_sha256'],'native_connectivity':{n:{'trace_length_total_mm':v} for n,v in stable_usb['trace_length_only_mm'].items()},'trace_length_skew_mm':stable_usb['trace_length_skew_mm']}
 out={'date':'2026-10-28','board':'hardware/Ankle_Sensor_V1.kicad_pcb','board_sha256':before,'board_unchanged_after_read':True,'native_kicad_version':pcbnew.GetBuildVersion(),'status':'READ_ONLY_GEOMETRY_SURVEY_NO_IMPEDANCE_OR_USB_CERTIFICATION','method':{'native_fill':'Stored filled In1.Cu GND SHAPE_POLY_SET, preserving antipad voids; no refill/edit in this audit','area':'Native TransformShapeToPolygon/BooleanAdd/BooleanIntersection/BooleanSubtract; actual trace widths and fixed 0.50mm survey bands','poly_error_mm':POLY_ERROR,'centerline':'Native Contains at segment midpoints; missing intervals joined through same-net through-via endpoints','centerline_max_step_mm':STEP,'sampling_uncertainty_per_run_boundary_mm':STEP,'gap_component_metric':'Sum of absent-GND trace lengths connected at track/via endpoints; branches can overestimate one path. Component bboxes are XY extents, not field-solver results.','band_limitation':'0.50mm survey width is a repeatable geometric probe, not a derived return-current requirement.'},'stackup':{'order':['F.Cu','In1.Cu GND','In2.Cu +3V0 and signals','B.Cu'],'board_nominal_thickness_mm':mm(board.GetDesignSettings().GetBoardThickness()),'explicit_dielectric_stackup_in_pcb':False,'consequence':'No verified dielectric separations, Er or 90ohm differential impedance. B.Cu is adjacent to mixed In2, not directly to In1 ground.'},'ground_fill':{'outline_count':gnd.OutlineCount(),'area_mm2':area(gnd),'warning':'Stored fractured polygons can encode holes as cutouts; OutlineCount is not proof that return paths are electrically adequate.'},'groups':GROUPS,'nets':nets,'usb_lengths_copied_from_verified_proposal':{'source_file':'.work/final_repairs/usb/usb_verification.json','proposal_board_sha256':usbsource['board_sha256'],'trace_length_only_mm':{n:usbsource['native_connectivity'][n]['trace_length_total_mm'] for n in ['USB_DP','USB_DN']},'trace_length_skew_mm':usbsource['trace_length_skew_mm'],'equal_vias_per_net':2,'canonical_trace_lengths_match_proposal_within_0p001mm':all(abs(nets[n]['trace_length_mm']-usbsource['native_connectivity'][n]['trace_length_total_mm'])<.001 for n in ['USB_DP','USB_DN'])},'limitations':['Native DRC/parity do not qualify impedance, edge rates, return-current distribution, crosstalk or USB eye/EMC.','Own non-ground via antipads necessarily remove In1 copper directly below the layer transition; nearby ground stitching and actual reference geometry must be assessed against verified stackup.','Coverage of In1 ground below B.Cu does not prove the adjacent mixed In2 reference is continuous or adequately decoupled.']}
 out['usb_lengths_copied_from_verified_proposal']['source_file']='reports/usb_routing_review.json (verified_mcu_proposal)'
 out['method']['own_via_probe']='0.42mm radius around each target-net 0.50mm via: nominal0.25mm copper radius +0.15mm plane clearance +0.02mm geometric margin. Small residual edge slivers are listed separately.'
 out['stackup']['explicit_dielectric_stackup_in_pcb']='(stackup' in path.read_text()
 gpads=[p for p in board.GetPads() if p.GetNetname()=='GND'];todo=[gpads[0]];seen=set();conn=board.GetConnectivity()
 while todo:
  item=todo.pop();u=item.m_Uuid.AsString()
  if u in seen:continue
  seen.add(u);todo.extend(x for x in conn.GetConnectedItems(item) if x.m_Uuid.AsString() not in seen)
 out['ground_fill']['gnd_pad_count']=len(gpads)
 out['ground_fill']['all_gnd_pads_in_one_native_component']=all(p.m_Uuid.AsString() in seen for p in gpads)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==before
 (ROOT/'reports/return_path_review.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 stable_usb_report['canonical_board_sha256']=before
 stable_usb_report['canonical_nets']={n:{k:nets[n][k] for k in ['trace_length_mm','trace_length_by_layer_mm','via_count','native_projection_gnd_coverage_pct','max_missing_component_trace_length_sum_mm']} for n in ['USB_DP','USB_DN','USB_DP_CONN','USB_DN_CONN']}
 end={side:{'trace_length_only_mm':nets['USB_'+side]['trace_length_mm']+nets['USB_'+side+'_CONN']['trace_length_mm'],'via_count':nets['USB_'+side]['via_count']+nets['USB_'+side+'_CONN']['via_count']} for side in ['DP','DN']}
 stable_usb_report['whole_path_via_esd_to_connector']=end
 stable_usb_report['whole_path_planar_trace_length_difference_mm']=abs(end['DP']['trace_length_only_mm']-end['DN']['trace_length_only_mm'])
 stable_usb_report['limits']=['Only the MCU-side main In2 trunk was deliberately paired at nominal 0.15 mm gap. Endpoint fanouts and connector-side geometry are not qualified as a controlled-impedance differential pair.','Actual JLC dielectric stackup and Er are not defined; no 90 ohm or USB compliance claim.','Whole-path DP/DN via count differs (2 versus 4); equal MCU-side via counts do not establish whole-path matching.']
 (ROOT/'reports/usb_routing_review.json').write_text(json.dumps(stable_usb_report,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'board_sha256':before,'nets':{n:{'length_mm':d['trace_length_mm'],'gnd_coverage_pct':d['native_projection_gnd_coverage_pct'],'missing_centerline_mm':d['estimated_centerline_without_gnd_total_mm'],'max_component_trace_mm':d['max_missing_component_trace_length_sum_mm']} for n,d in nets.items()}},indent=2))

if __name__=='__main__':main()
