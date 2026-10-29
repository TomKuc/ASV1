#!/usr/bin/env python3
"""Read-only narrow A03/A04 source/placement and exported-mask check.

Run with KiCad's Python. No SaveBoard, refill, placement translation or ordering.
The deliberately limited Gerber parser accepts this export's aperture flashes
only and rejects regions/strokes/polarity changes, rather than claiming full CAM.
Public catalog evidence is inherited explicitly; it is never a stock reservation.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gerber_flashes(path):
    text = path.read_text()
    assert '%FSLAX46Y46*%' in text and '%MOMM*%' in text
    assert not re.search(r'D0[12]\*|G36\*|%LPC', text)
    apertures = {}
    for number, kind, values in re.findall(r'%ADD(\d+)([A-Za-z]+),([^*]+)\*%', text):
        params = [float(v) for v in values.split('X')]
        assert kind in ('C', 'R', 'O', 'RoundRect'), kind
        apertures[int(number)] = (kind, params)
    active = None
    component = None
    flashes = []
    for line in text.splitlines():
        select = re.fullmatch(r'D(\d+)\*', line)
        comp = re.fullmatch(r'%TO.C,([^*]+)\*%', line)
        coord = re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*', line)
        if select:
            active = int(select[1])
        if comp:
            component = comp[1]
        if line == '%TD*%':
            component = None
        if coord:
            flashes.append({'xy_mm': [int(coord[1]) / 1e6, int(coord[2]) / 1e6],
                            'component': component, 'aperture': active,
                            'shape': apertures[active]})
    assert text.strip().endswith('M02*')
    return flashes


def shape_distance(point, flash):
    kind, values = flash['shape']
    x, y = [a - b for a, b in zip(point, flash['xy_mm'])]
    if kind == 'RoundRect':
        assert len(values) == 10 and values[-1] == 0
        radius = values[0]
        xs, ys = values[1:9:2], values[2:9:2]
        x -= (min(xs) + max(xs)) / 2
        y -= (min(ys) + max(ys)) / 2
        hx, hy = (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2
    else:
        width = values[0]
        height = values[1] if len(values) > 1 else width
        radius = width / 2 if kind == 'C' else min(width, height) / 2 if kind == 'O' else 0
        hx, hy = width / 2 - radius, height / 2 - radius
    dx, dy = abs(x) - hx, abs(y) - hy
    return math.hypot(max(dx, 0), max(dy, 0)) + min(max(dx, dy), 0) - radius


def main():
    board_path = ROOT / 'hardware/Ankle_Sensor_V1.kicad_pcb'
    before = digest(board_path)
    board = pcb.LoadBoard(str(board_path))
    footprints = {f.GetReference(): f for f in board.GetFootprints()}
    bom_path = ROOT / 'manufacturing/review/assembly/BOM_REVIEW_NOT_RELEASED.csv'
    cpl_path = ROOT / 'manufacturing/review/assembly/CPL_REVIEW_ROTATIONS_UNCONFIRMED.csv'
    bom = list(csv.DictReader(bom_path.open()))
    cpl = {row['Designator']: row for row in csv.DictReader(cpl_path.open())}
    by_ref = {ref: row for row in bom for ref in row['Designator'].split(',')}
    assert len(bom) == 33 and len(cpl) == 59 and set(cpl) == set(by_ref)
    old_path = ROOT / 'reports/pcba_testability_final_A1.json'
    old = json.loads(old_path.read_text())
    catalog = {row['c_number']: row for row in old['sourcing']['parts']}
    refreshed = {'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U8', 'J1', 'J2', 'Y1'}
    polarity = {
        'D1': 'pad1=K; pad2=A; potwierdzić znacznik katody w preview',
        'Q1': '1=G;2=S;3=D; potwierdzić pin1',
        'Q2': '1=G;2=S;3=D; potwierdzić pin1',
        'J1': 'złącze kierunkowe; otwór USB ku dolnej krawędzi PCB; sprawdzić SH/kołki',
        'J2': '1=VBAT;2=NTC;3=GND; sprawdzić orientację złącza i przewodu',
        'Y1': 'kwarc dwukońcówkowy bez polaryzacji; zgodność landów wymaga akceptacji',
        'SW1': 'sprawdzić pary styków i kierunek korpusu',
    }
    rows = []
    for ref in sorted(cpl, key=lambda s: (re.sub(r'\d+', '', s), int(re.search(r'\d+', s)[0]))):
        footprint = footprints[ref]
        fields = {f.GetName(): f.GetText() for f in footprint.GetFields()}
        item, placement = by_ref[ref], cpl[ref]
        assert fields['MPN'] == item['Manufacturer Part Number']
        assert fields['JLCPCB'] == item['JLCPCB Part #']
        assert str(footprint.GetFPID().GetLibNickname()) + ':' + str(footprint.GetFPID().GetLibItemName()) == item['Footprint']
        source = catalog[item['JLCPCB Part #']]
        origin = board.GetDesignSettings().GetAuxOrigin()
        expected = [pcb.ToMM(footprint.GetPosition().x-origin.x),
                    pcb.ToMM(origin.y-footprint.GetPosition().y)]
        assert abs(expected[0] - float(placement['Mid X'])) < 1e-6
        assert abs(expected[1] - float(placement['Mid Y'])) < 1e-6
        assert abs((float(placement['Rotation']) - footprint.GetOrientation().AsDegrees()) % 360) < 1e-6
        assert placement['Layer'] == 'Top'
        pin1 = [p for p in footprint.Pads() if p.GetNumber() == '1']
        pin1 = [round(pcb.ToMM(pin1[0].GetPosition().x),6),round(pcb.ToMM(pin1[0].GetPosition().y),6)] if pin1 else None
        rows.append({'designator': ref, 'value': item['Comment'], 'MPN': fields['MPN'],
                     'JLCPCB_LCSC': fields['JLCPCB'], 'footprint': item['Footprint'],
                     'status': 'wymaga potwierdzenia',
                     'public_catalog_service': source['PCBA_type'] or 'JLC niepotwierdzone',
                     'public_catalog_url': source['jlc_card_url'],
                     'catalog_evidence': 'refreshed public read 2026-10-29' if ref in refreshed else
                         'prior public read 2026-10-29 reused by exact MPN/C' if source['jlc_card_read_2026_10_29'] else
                         'fresh exact search/direct read failed; LCSC identity only',
                     'CPL_X_mm': placement['Mid X'], 'CPL_Y_mm': placement['Mid Y'],
                     'CPL_rotation_deg': placement['Rotation'], 'side': 'Top',
                     'pin1_PCB_xy_mm': json.dumps(pin1),
                     'polarity_orientation': polarity.get(ref, 'potwierdzić pin1/znacznik i tape orientation w preview' if ref.startswith('U') else 'bez polaryzacji; zgodność obudowy RC'),
                     'orientation_approved_by_JLC': 'NO',
                     'MSL': source['MSL_if_shown'] or 'nie uzyskano; nie oznacza zwolnienia',
                     'Xray': source['Xray_if_shown'] or 'nie uzyskano; uzgodnić proces',
                     'quantity_3boards': 3, 'quantity_5boards': 5})
    for ref, value in [('PACK_EXTERNAL','Chroniony Li-Po1S z PCM i NTC na ogniwie; dokładny MPN nie wybrany'),
                       ('HARNESS_EXTERNAL','Wiązka do J2;1=PACK+;2=NTC;3=PACK-; elementy dobierać do JSTSH'),
                       ('SWD_FIXTURE_EXTERNAL','Własny pogo fixture do J3; nie jest częścią PCB')]:
        rows.append({'designator':ref,'value':value,'MPN':'NIE WYBRANO','status':'montaż ręczny',
                     'polarity_orientation':value,'orientation_approved_by_JLC':'N/A'})
    csv_path = ROOT / 'reports/production_component_status_A1.csv'
    with csv_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), restval='')
        writer.writeheader(); writer.writerows(rows)
    via_path = ROOT / 'reports/via_pad_audit.json'
    vias = json.loads(via_path.read_text())
    assert vias['source_sha256'] == before
    pairs = [v for v in vias['copper']['pairs_below_0_25mm'] if v['ref'] in ('U6','C4','C5') and v['pin']=='2']
    assert len(pairs)==3
    layers = {}
    for layer in ['F_Mask','B_Mask','F_Paste','B_Paste']:
        path = ROOT / ('manufacturing/review/gerbers/Ankle_Sensor_V1-'+layer+'.gbr')
        layers[layer] = (path, gerber_flashes(path))
    local = []
    for pair in pairs:
        xy = pair['via_xy_mm']; plot = [xy[0]-50,101.6-xy[1]]
        checks = {}
        for layer, (path, flashes) in layers.items():
            nearest = min(flashes, key=lambda f:shape_distance(plot,f)) if flashes else None
            distance = shape_distance(plot,nearest) if nearest else None
            checks[layer] = {'file':str(path.relative_to(ROOT)), 'sha256':digest(path),
                             'flash_count':len(flashes),'via_center_inside_any_opening':distance is not None and distance<=0,
                             'via_hole_overlaps_any_opening':distance is not None and distance<=.125,
                             'nearest_opening_ref':nearest['component'] if nearest else None,
                             'nearest_aperture':nearest['aperture'] if nearest else None,
                             'hole_edge_to_opening_mm':round(distance-.125,6) if nearest else None,
                             'annulus_edge_to_opening_mm':round(distance-.25,6) if nearest else None}
            assert not checks[layer]['via_hole_overlaps_any_opening']
        local.append({**pair,'via_diameter_mm':.5,'plot_via_xy_mm':plot,'exported_openings':checks})
    result = {'schema_version':1,'read_date':'2026-10-29','board_sha256':before,
              'A03_status':'EXTERNAL CONFIRMATION','A04_status':'EXTERNAL CONFIRMATION',
              'hardware_changed_by_this_check':False,'hardware_tests_performed':False,
              'manufacturer_CAM_approval_obtained':False,'order_stock_or_placement_approval_obtained':False,
              'assembly':{'footprints':len(footprints),'BOM_groups':len(bom),'CPL_parts':len(cpl),
                          'all_TOP':True,'BOM_CPL_native_metadata_origins_rotations_match':True,
                          'BOM_sha256':digest(bom_path),'CPL_sha256':digest(cpl_path),
                          'component_status_csv_sha256':digest(csv_path),
                          'excluded_bare_copper':sorted(set(footprints)-set(cpl)),
                          'orientation_scope':'Native placement and pin1 coordinates only, no tape-convention conversion or JLC preview acceptance.'},
              'catalog':{'historical_30of33_identity_service_evidence':str(old_path.relative_to(ROOT)),
                         'historical_evidence_sha256':digest(old_path),'exact_MPN_C_reuse':True,
                         'critical_cards_reread_in_this_closure':sorted(refreshed),
                         'U7_R1_R20_fresh_search_and_direct_read':'Exact JLC cards not retrieved; no inference of unavailability.',
                         'all_59_fitted_status':'wymaga potwierdzenia',
                         'no_part_marked_unavailable_without_evidence':True},
              'CAM_scope':'Literal Gerber aperture flashes checked locally at three tied minima; not independent full-board CAM or tolerance approval.',
              'hole_pad_minima':local,
              'sources':{'via_covering':'https://jlcpcb.com/help/article/pcb-via-covering',
                         'capabilities':'https://jlcpcb.com/capabilities/pcb-capabilities/',
                         'rails':'https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order',
                         'matching':'https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders'},
              'open_JLC_acceptance':['Exact stock/procurement/attrition for all33groups, especially U7/R1/R20.',
                                     'All59 component orientations and pin1/polarity in actual placement preview.',
                                     'Three0.150001mm hole-to-pad/paste minima and0.025mm annulus-to-mask-opening nominal margin with actual drill/registration/mask process.',
                                     'WSON/LGA stencils and EP paste, reflow/MSL, U3/U4 Xray.',
                                     'Manufacturer-created rails/fiducials/panel; preserve RF keepout and avoid IMU depanel stress.']}
    assert before == digest(board_path)
    (ROOT/'reports/production_pcba_dfm_A1.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'board_sha256':before,'parts':len(cpl),'groups':len(bom),'local_checks':len(local)}))


if __name__ == '__main__':
    main()
