#!/usr/bin/env python3
"""Read canonical board; calculate explicitly idealised USB cross sections. Never saves PCB.
Run with KiCad's Python3.9 (pcbnew), clang++ and a writable /private/tmp.
"""
from pathlib import Path
import concurrent.futures, hashlib, json, math, subprocess, tempfile
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
BOARD=ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb'
SOURCES={
 'jlc_1mm_legacy_table':'https://cart.jlcpcb.com/client/template/placeOrder/impedance.html',
 'jlc_current_material_parameters':'https://jlcpcb.com/impedance',
 'jlc_capabilities':'https://jlcpcb.com/capabilities/pcb-capabilities/',
 'raytac_ver_L':'https://www.raytac.com/download/index.php?index_id=43',
 'nordic_power':'https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html',
 'nordic_dcch':'https://devzone.nordicsemi.com/f/nordic-q-a/108362/vdd-vddh-and-dcch-mistake',
 'nordic_usb_resistors':'https://devzone.nordicsemi.com/f/nordic-q-a/94955/resistors-for-d-and-d-',
 'quasi_tem_method':'https://www.comsol.com/support/learning-center/article/modeling-tem-and-quasi-tem-transmission-lines-21971',
 'quasi_tem_rlgc':'https://doc.comsol.com/6.4/doc/com.comsol.help.models.rf.transmission_line_coaxial/transmission_line_coaxial.html',
 'usb_fs_edges':'https://compliance.usb.org/index.asp?UpdateFile=Electrical',
 'usb_fs_vs_hs':'https://www.usb.org/node/214',
 'nordic_12Mbps':'https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/keyfeatures_html5.html'}

def shape(item,layer):
 p=pcbnew.SHAPE_POLY_SET(); item.TransformShapeToPolygon(p,layer,0,pcbnew.FromMM(.001),pcbnew.ERROR_OUTSIDE);return p
def intervals(test,xc,y):
 d=.005; n=800; out=[]; start=None;last=None
 for i in range(n+1):
  x=xc-2+i*d;v=test(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
  if v!=last:
   if last:out.append({'x_mm':[round(start,5),round(x-d/2,5)],'nets':last})
   start=x-d/2;last=v
 if last:out.append({'x_mm':[round(start,5),round(x,5)],'nets':last})
 return out
def main():
 before=hashlib.sha256(BOARD.read_bytes()).hexdigest();board=pcbnew.LoadBoard(str(BOARD));board.BuildConnectivity()
 power=next(z.GetFilledPolysList(pcbnew.In2_Cu) for z in board.Zones() if z.GetNetname()=='+3V0' and z.IsOnLayer(pcbnew.In2_Cu))
 ground=next(z.GetFilledPolysList(pcbnew.In1_Cu) for z in board.Zones() if z.GetNetname()=='GND' and z.IsOnLayer(pcbnew.In1_Cu))
 bottom=[(t.GetNetname(),shape(t,pcbnew.B_Cu)) for t in board.Tracks() if t.IsOnLayer(pcbnew.B_Cu)]
 sections=[]
 for y,xc in [(68,70.9),(71,70.9),(73.5,71.1),(80,73.6),(84,73.6)]:
  sections.append({'y_mm':y,'pair_mid_x_mm':xc,'pair_centres_x_mm':[xc-.15,xc+.15],
   'in1_gnd_intervals':intervals(lambda p:['GND'] if ground.Contains(p) else [],xc,y),
   'in2_power_intervals':intervals(lambda p:['+3V0'] if power.Contains(p) else [],xc,y),
   'b_cu_intervals':intervals(lambda p:sorted({n for n,s in bottom if s.Contains(p)}),xc,y)})
 nets={}
 for name in ['USB_DP','USB_DN','USB_DP_CONN','USB_DN_CONN']:
  ts=[t for t in board.Tracks() if t.GetNetname()==name];layers={}
  for t in ts:
   if t.Type()==pcbnew.PCB_VIA_T:continue
   l=board.GetLayerName(t.GetLayer());layers[l]=layers.get(l,0)+pcbnew.ToMM(t.GetLength())
  nets[name]={'trace_length_mm':sum(layers.values()),'length_by_layer_mm':layers,
   'via_count':sum(t.Type()==pcbnew.PCB_VIA_T for t in ts),'widths_mm':sorted({pcbnew.ToMM(t.GetWidth()) for t in ts if t.Type()!=pcbnew.PCB_VIA_T})}
 u3=next(f for f in board.GetFootprints() if f.GetReference()=='U3')
 power_pads={p.GetNumber():p.GetNetname() for p in u3.Pads() if p.GetNumber() in ['28','30','31','32','34','35']}
 cases=[
  ('in2',.005,2.5,1.8,4.4,4.6,.15,.15),('in2',.0025,2.5,1.8,4.4,4.6,.15,.15),
  ('in2',.005,5,3.6,4.4,4.6,.15,.15),('in2',.005,2.5,1.8,4.6,4.6,.15,.15),
  ('in2_coplanar',.005,2.5,1.8,4.4,4.6,.15,.15),('in2_coplanar',.0025,2.5,1.8,4.4,4.6,.15,.15),
  ('in2_b_ground',.005,2.5,1.8,4.4,4.6,.15,.15),('in2_b_ground',.0025,2.5,1.8,4.4,4.6,.15,.15),
  ('in2_b_ground',.005,2.5,1.8,4.4,4.6,.15,.15,.75),
  ('in2_b_ground_coplanar',.005,2.5,1.8,4.4,4.6,.15,.15),
  ('front',.005,2.5,1.8,4.4,4.6,.15,.15),('front',.0025,2.5,1.8,4.4,4.6,.15,.15),
  ('single_front',.005,5,3.6,4.4,4.6,.15,.15),('single_in2',.005,5,3.6,4.4,4.6,.15,.15),
  ('in2',.005,2.5,1.8,4.4,4.6,.17,.13),('in2_coplanar',.005,2.5,1.8,4.4,4.6,.17,.13),
  ('in2',.0025,2.5,1.8,4.4,4.6,.17,.13),('in2_coplanar',.0025,2.5,1.8,4.4,4.6,.17,.13),
  ('parallel_plate',.005,2.5,.6,4.4,4.6,.15,.15)]
 with tempfile.TemporaryDirectory(prefix='ankle_usb_fd_',dir='/private/tmp') as td:
  exe=Path(td)/'usb_fd';subprocess.run(['clang++','-O3','-std=c++17',str(ROOT/'scripts/usb_cross_section_fd.cpp'),'-o',str(exe)],check=True)
  def calc(case):
   mode,d,x,y,pp,core,w,gap,*extra=case
   return json.loads(subprocess.check_output([str(exe),*[str(v) for v in [d,x,y,mode,pp,core,w,gap,*extra]]],text=True))
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(calc,cases))
 data={
  'date':'2026-10-29','status':'NOMINAL_2D_ESTIMATE_NOT_USB_COMPLIANCE_OR_FAB_RELEASE','board_sha256':before,'board_changed':False,
  'selected_design_basis':{'name':'JLC7628, 4-layer, nominal1.0mm, outer1oz, inner0.5oz',
   'selection_scope':'Selected for this engineering analysis and recommended order confirmation. No order or board stackup was modified.',
   'current_order_template_id_verified':False,'explicit_stackup_in_native_pcb':'(stackup' in BOARD.read_text(),
   'layers_top_to_bottom':[{'name':'F.Cu','cu_mm':.035},{'name':'prepreg7628x1','dielectric_mm':.2104,'er':4.4},{'name':'In1.Cu GND','cu_mm':.0152},{'name':'core','dielectric_mm':.4,'er':4.6},{'name':'In2.Cu signals/+3V0','cu_mm':.0152},{'name':'prepreg7628x1','dielectric_mm':.2104,'er':4.4},{'name':'B.Cu signals','cu_mm':.035}],
   'sum_without_mask_mm':1.0212,'older_table_pp_er':4.6,'current_jlc_pp_er':4.4,
   'source_uncertainty':'Official legacy static table exposes1.0mm geometry. Current page exposes material parameters but only SSR1.6mm geometry; live1mm POST API could not be fetched. Exact current order stack/template/material must be confirmed by JLC before production.',
   'mask_above_substrate_mm':.03048,'mask_above_trace_mm':.01524,'mask_er':3.8},
  'native_usb_nets':nets,'native_raytac_pad_nets':power_pads,'native_cross_sections':sections,
  'model_sources_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'scripts/usb_cross_section_fd.cpp',ROOT/'scripts/review_usb_stackup.py']},
  'accepted_width_correction':json.loads((ROOT/'reports/usb_width_correction_A1.json').read_text()),
  'model_scenario_classification':{'historical_trunk_geometry':'0.15mm width/0.15mm gap','current_trunk_geometry':'0.17mm width/0.13mm nominal gap','current_tails':'0.15mm, nonuniform coupling; no single whole-path Zdiff'},
  'native_cross_section_sample_step_mm':.005,
  'model':{'solver':'scripts/usb_cross_section_fd.cpp, finite-volume electrostatics with harmonic dielectric interfaces; PCG residual<1e-9',
   'equations':['div(epsilon grad V)=0','odd mode Vplus=+1V,Vminus=-1V; symmetry plane0V','Codd=Qplus/1V; repeat same geometry in vacuum to obtain Codd0','Zdiff=2/(c*sqrt(Codd*Codd0))'],
   'geometry':'Perfect rectangular copper; In1 idealGND. In2 trace thickness rounds to0.015mm at grids5/2.5um. Air above B and0.03048mm mask on unplated substrate; F mask0.03048mm between traces/0.01524mm over trace. No actual B signal conductors in base model.',
   'coplanar_case':'Ideal equipotential AC0 conductor outside both pair edges by0.15mm on In2. Conditional lower estimate: real+3V0 is not automaticallyGND, especially common mode or asymmetric gaps.',
   'b_ground_case':'Hypothetical continuous grounded B strip/plane0.2104mm from In2 copper. Not present in canonical.',
   'tails':'Not continuously parallel. front model is hypothetical paired F geometry; single cases estimate isolated traceZ0, not a Zdiff for separately routed tails.',
   'not_modelled':['frequency-dependentEr/loss/copperroughness/trapezoid','full3D bends/vias/antipads/module/ESD/pins/connector/cable','nonuniform+3V0 return impedance','manufacturing dimensional distributions','transienteye/ESD/EMC'],
   'validation_scope':'Analytic parallel-plate sanity check, mesh and box convergence. Not independently calibrated against a commercial field solver or impedance coupon.'},
  'calculations':results,
  'analytic_parallel_plate_sanity_check':{'model':'Ground0V atz=0; signal1V atz=0.4mm; sideNeumann boundaries; width2.5mm; homogeneousEr4.6',
   'C_F_per_m':8.8541878128e-12*4.6*2.5/.4,'Z_ohm':376.730313668*.4/(2.5*math.sqrt(4.6)),
   'scope':'Checks potential/charge extraction, units and quasiTEM factor against analytic parallel plate; does not validate actual heterogeneous cross sections.'},
  'rejected_b_ground_proposal':{'source':'Root native read of .work/usb_reference_candidate, not merged','rectangle_mm':[68.5,64,74.6,89],
   'native_axis_coverage_pct':{'USB_DP':69.3,'USB_DN':73.5},'reason':'B signals interrupt candidate fill. Ideal continuous93ohm cannot be assigned to this discontinuous geometry; no demonstrated net benefit.'},
  'raytac_8p3':{'text_verified':True,'visual_schematic_verified':False,'pdf_pages_zero_indexed':[39,40],
   'normal_mode':'U3.28VDD and.30VDDH on3V0, .31DCCH NC, .32VBUS5V consistent with Nordic normal mode; host C11 is VBUS decoupling, not exposedDECUSB.',
   'remaining_check':'Literal external capacitor values/placement and module internal decoupling from Raytac section8.3 drawing still require visual comparison.',
   'access_attempts':['OfficialPDF text retrieved from primaryRaytacURL','web screenshot returned references only','raw MCP screenshot result content contained text only: ImageDisplayed; no image blocks','shell DNS fails; no localPDF retrieved','officialRaytacblog reference image found but is MDBT50Q-RX dongle, not exactsection8.3; not substituted']},
  'gate_A_before_fabrication':['Confirm exact current JLC1mm7628 template/material/Cu/dielectrics and acceptable trace geometry; bind to fabrication instruction. Current nominal model alone is not90ohm qualification.','Complete visual Raytac8.3 comparison; no inferred capacitor/resistor changes.'],
  'gate_B_physical_qualification':['USB fullspeed12Mbps firmware, both connector orientations, long transfer/CRC/reconnect tests','MeasureFS signal quality with correctfixture/cable; compareeye and edges, notHS480Mbps mask','ESD/protection return testing and power/RF/thermal prototype tests'],
  'sources_primary':SOURCES}
 assert hashlib.sha256(BOARD.read_bytes()).hexdigest()==before
 out=ROOT/'reports/usb_stackup_final_A1.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'sha256':before,'models':[{k:r[k] for k in ['mode','pitch_mm','width_mm','gap_mm']+(['Z_diff_ohm'] if 'Z_diff_ohm'in r else ['Z_single_ohm'])} for r in results]},indent=2))
if __name__=='__main__':main()
