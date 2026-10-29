#!/usr/bin/env python3
"""Create a real KiCad board from the KiCad-exported netlist and placement file.

Run with the Python3.9 shipped inside KiCad10 on macOS. This first creates an
unrouted board. It never declares a fabrication release or invents a DRC result.
"""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
import pcbnew as pcb

ROOT=Path(__file__).resolve().parents[1]
HW=ROOT/'hardware'
NAME='Ankle_Sensor_V1'

def vec(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))

def main():
    existing=HW/f'{NAME}.kicad_pcb'
    if existing.exists() and '--replace' not in sys.argv:
        previous=pcb.LoadBoard(str(existing))
        if any(previous.GetTracks()):
            raise RuntimeError('PCB already has routing. Use --replace only after saving a checkpoint.')
    netlist=ET.parse(ROOT/'reports'/f'{NAME}.net.xml').getroot()
    design=json.loads((HW/'design.json').read_text())
    config=json.loads((HW/'placement.json').read_text())
    byref={c['ref']:c for c in design['components']}
    board=pcb.BOARD()
    board.SetCopperLayerCount(4)
    board.SetFileName(str(HW/f'{NAME}.kicad_pcb'))
    board.GetDesignSettings().SetBoardThickness(pcb.FromMM(config['thickness_mm']))
    nets={}
    pin_nets={}
    for n in netlist.findall('nets/net'):
        name=n.attrib['name']
        info=pcb.NETINFO_ITEM(board,name)
        board.Add(info);nets[name]=info
        for node in n.findall('node'):
            pin_nets[(node.attrib['ref'],node.attrib['pin'])]=name
    footprints={}
    for component in netlist.findall('components/comp'):
        ref=component.attrib['ref']
        if ref.startswith('#'):continue
        data=byref[ref]
        identifier=component.findtext('footprint') or data['footprint']
        lib,name=identifier.split(':',1)
        if lib!='AnkleSensor':raise ValueError('Footprint is not project-local: '+identifier)
        fp=pcb.FootprintLoad(str(HW/'footprints/AnkleSensor.pretty'),name)
        if fp is None:raise ValueError('Could not load '+identifier)
        fp.SetReference(ref);fp.SetValue(data['value'])
        fp.SetFPID(pcb.LIB_ID(lib,name))
        fp.SetPath(pcb.KIID_PATH(component.find('sheetpath').attrib['tstamps']+component.findtext('tstamps')))
        board.Add(fp)
        placement=config['placements'][ref]
        fp.SetPosition(vec(placement[0],placement[1]))
        fp.SetOrientationDegrees(placement[2])
        if len(placement)>3 and placement[3]=='B':fp.Flip(fp.GetPosition(),False)
        for pad in fp.Pads():
            name=pin_nets.get((ref,pad.GetNumber()))
            if name:pad.SetNet(nets[name])
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        for field in component.findall('fields/field'):
            name=field.attrib['name']
            fp.SetField(name,field.text or '')
            fp.GetField(name).SetVisible(False)
        for field,value in [('Datasheet',data['datasheet'])]:
            fp.SetField(field,value);fp.GetField(field).SetVisible(False)
        footprints[ref]=fp
    left,top,right,bottom=config['outline_mm']
    # Connector shell deliberately overhangs the board. Clip only its printed
    # outline at the fabrication edge; keep the full mechanical F.Fab drawing.
    for graphic in footprints['J1'].GraphicalItems():
        if graphic.GetLayer()!=pcb.F_SilkS or not isinstance(graphic,pcb.PCB_SHAPE):continue
        if graphic.GetShape()!=pcb.SHAPE_T_SEGMENT:continue
        for getter,setter in [(graphic.GetStart,graphic.SetStart),(graphic.GetEnd,graphic.SetEnd)]:
            point=getter()
            if pcb.ToMM(point.y)>bottom-.25:setter(vec(pcb.ToMM(point.x),bottom-.25))
    points=[(left,top),(right,top),(right,bottom),(left,bottom)]
    for a,b in zip(points,points[1:]+points[:1]):
        edge=pcb.PCB_SHAPE(board);edge.SetShape(pcb.SHAPE_T_SEGMENT)
        edge.SetStart(vec(*a));edge.SetEnd(vec(*b));edge.SetLayer(pcb.Edge_Cuts)
        edge.SetWidth(pcb.FromMM(.05));board.Add(edge)
    # Plain rectangular outline intentionally leaves enclosure details to the
    # validated mechanical design; no unverified mounting holes are added.
    title=board.GetTitleBlock()
    title.SetTitle('Ankle Sensor V1');title.SetRevision('A1-WIP');title.SetDate('2026-10-28')
    text=pcb.PCB_TEXT(board);text.SetText('ANKLE SENSOR V1\nA1 PROTOTYPE')
    text.SetPosition(vec(64,79.7));text.SetLayer(pcb.B_SilkS);text.SetMirrored(True)
    text.SetTextSize(vec(.8,.8));text.SetTextThickness(pcb.FromMM(.12));board.Add(text)
    # Define, but do not fill, inner planes; footprint antenna keepouts are
    # honoured by KiCad's zone filler. Routing retains In1.Cu as continuous GND.
    for layer,netname in [(pcb.In1_Cu,'GND'),(pcb.In2_Cu,'+3V0')]:
        zone=pcb.ZONE(board);zone.SetLayer(layer);zone.SetNet(nets[netname])
        zone.SetLocalClearance(pcb.FromMM(.15));zone.SetPadConnection(pcb.ZONE_CONNECTION_FULL)
        zone.SetMinThickness(pcb.FromMM(.15));outline=zone.Outline();outline.NewOutline()
        for x,y in points:outline.Append(pcb.FromMM(x+.3 if x==left else x-.3),pcb.FromMM(y+.3 if y==top else y-.3))
        board.Add(zone)
    # Continue the vendor antenna keepout to the actual board edge. Without
    # this extension, zone fill can leave a copper strip in front of the aerial.
    keepout=pcb.ZONE(board);keepout.SetIsRuleArea(True)
    keepout.SetLayerSet(pcb.LSET.AllCuMask())
    keepout.SetDoNotAllowTracks(True);keepout.SetDoNotAllowVias(True)
    keepout.SetDoNotAllowPads(True);keepout.SetDoNotAllowZoneFills(True)
    keepout.SetDoNotAllowFootprints(False)
    poly=keepout.Outline();poly.NewOutline()
    for x,y in [(57.8,49.8),(70.2,49.8),(70.2,55),(57.8,55)]:poly.Append(pcb.FromMM(x),pcb.FromMM(y))
    board.Add(keepout)
    # Thermal connection leaves the exposed pad through masked copper necks.
    # The two holes sit outside the EP, avoiding an unqualified via-in-pad process.
    for x,y in [(63,91.0),(63,93.4)]:
        via=pcb.PCB_VIA(board);via.SetPosition(vec(x,y))
        via.SetWidth(pcb.FromMM(.5));via.SetDrill(pcb.FromMM(.25))
        via.SetViaType(pcb.VIATYPE_THROUGH);via.SetLayerPair(pcb.F_Cu,pcb.B_Cu)
        via.SetFrontTentingMode(pcb.TENTING_MODE_TENTED);via.SetBackTentingMode(pcb.TENTING_MODE_TENTED)
        via.SetNet(nets['GND']);board.Add(via)
        track=pcb.PCB_TRACK(board);track.SetStart(vec(63,92.2));track.SetEnd(vec(x,y))
        track.SetWidth(pcb.FromMM(.3));track.SetLayer(pcb.F_Cu);track.SetNet(nets['GND'])
        board.Add(track)
    board.BuildConnectivity()
    pcb.SaveBoard(str(HW/f'{NAME}.kicad_pcb'),board)
    project_path=HW/f'{NAME}.kicad_pro'
    project=json.loads(project_path.read_text())
    rules=project.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{})
    rules.update({'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.5,
                  'min_via_annular_width':.1,'min_through_hole_diameter':.25,
                  'min_copper_edge_clearance':.5})
    project['text_variables']['DESIGN_STATUS']='A1 WORK IN PROGRESS - NOT FOR FABRICATION'
    project_path.write_text(json.dumps(project,indent=2)+'\n')
    audit={'kicad_version':pcb.GetBuildVersion(),'status':'PLACEMENT_UNROUTED_NOT_FOR_FABRICATION','footprints':len(footprints),'net_count':len(nets),'source':'KiCad exportedXMLnetlist','outline_mm':config['outline_mm']}
    (ROOT/'reports/pcb_build.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit))

if __name__=='__main__':main()
