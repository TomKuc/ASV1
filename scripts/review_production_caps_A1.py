#!/usr/bin/env python3
"""Read current capacitor CAD data; preserve the provenance of old power analyses.

Run with KiCad's native Python. No board write, PDN calculation or hardware test.
"""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import pcbnew

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def save(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


board_path = 'hardware/Ankle_Sensor_V1.kicad_pcb'
board_hash = sha(board_path)
board = pcbnew.LoadBoard(str(ROOT / board_path))
footprints = {f.GetReference(): f for f in board.GetFootprints()}
netxml_path = 'reports/Ankle_Sensor_V1.net.xml'
netxml = ET.parse(ROOT / netxml_path)
schematic_nets = {}
for net in netxml.findall('.//nets/net'):
    for node in net.findall('node'):
        schematic_nets[(node.get('ref'), node.get('pin'))] = net.get('name')
schematic_components = {c.get('ref'): c for c in netxml.findall('.//components/comp')}


def read_component(ref):
    f = footprints[ref]
    fields = {p.GetName(): p.GetText() for p in f.GetFields()}
    pads = {}
    mismatches = []
    for p in f.Pads():
        pin = p.GetNumber()
        if not pin or pin == 'MP':
            continue
        expected = schematic_nets.get((ref, pin))
        net = p.GetNetname()
        # KiCad encodes intentionally unconnected MCU pins only in the PCB.
        if expected is None and net.startswith('unconnected-'):
            expected = net
        if expected is None and not net:
            continue
        pads[pin] = {'pcb_net': net, 'schematic_net': expected,
                     'xy_mm': [pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)]}
        if net != expected:
            mismatches.append({'ref': ref, 'pin': pin, 'pcb_net': net, 'schematic_net': expected})
    sc = schematic_components[ref]
    if sc.findtext('value') != f.GetValue():
        mismatches.append({'ref': ref, 'value_mismatch': [f.GetValue(), sc.findtext('value')]})
    return {'value': f.GetValue(), 'mpn': fields.get('MPN'), 'jlcpcb': fields.get('JLCPCB'),
            'footprint': str(f.GetFPID().GetLibItemName()),
            'xy_mm': [pcbnew.ToMM(f.GetPosition().x), pcbnew.ToMM(f.GetPosition().y)],
            'rotation_deg': f.GetOrientationDegrees(), 'pads': pads}, mismatches


proof_path = 'reports/production_geometry_equivalence_A1.json'
proof = json.loads((ROOT / proof_path).read_text())
assert proof['after_sha256'] == board_hash
assert proof['status'] == 'PASS_NATIVE_CAD_GEOMETRY_IDENTICAL_EXCEPT_C9_PROPERTY_TEXT'
assert proof['changed_footprints'] == ['C9']
refs = ['C1', 'C5', 'C9', 'C10', 'C11']
components = {}
mismatches = []
for ref in refs:
    components[ref], mis = read_component(ref)
    mismatches.extend(mis)
assert not mismatches, mismatches
assert components['C9']['mpn'] == 'CL10A106KP8NNNC'
assert components['C11']['mpn'] == 'CL10A475KP8NNNC'

report = {
    'date': '2026-10-29', 'condition': 'A01_CAPACITORS', 'status': 'EXTERNAL CONFIRMATION',
    'current_source_sha256': board_hash, 'schematic_netlist_sha256': sha(netxml_path),
    'method': 'Read-only KiCad pcbnew: current values/MPN/JLC/pads/nets/coordinates compared to fresh native schematic netlist. Engineering reference arithmetic is not measurement or guaranteed Ceff.',
    'native': {'version': pcbnew.GetBuildVersion(), 'components': components,
               'netlist_mismatches': mismatches},
    'geometry_proof': {'path': proof_path, 'sha256': sha(proof_path), 'status': proof['status']},
    'C9': {'status': 'CLOSED', 'scope': 'nominal correction, exact MPN, same footprint only',
           'before_uF': 4.7, 'after_uF': 10.0, 'effective_10uF_guaranteed': False,
           'Ceff_minimum_status': 'EXTERNAL CONFIRMATION'},
    'C11': {'status': 'EXTERNAL CONFIRMATION', 'changed': False, 'nominal_uF': 4.7,
            'initial_tolerance_fraction': 0.1, 'initial_capacitance_range_uF': [4.23, 5.17],
            'exact_5V_or_5p5V_bias_curve_read': False, 'guaranteed_Ceff_uF': None,
            'DECUSB_capacitance_limit_applied_to_VBUS': False,
            'decision': 'Keep current component pending Raytac VBUS application clarification; lack of bias data is not a demonstrated hardware defect.'},
    'C9_bias_reference': {'mpn': 'CL10A106KP8NNNC', 'reference': 'TI LM3281 Table6 printed page16',
                          'voltage_V': 3.3, 'effective_uF': 5.2,
                          'guaranteed_minimum_for_this_board': False,
                          'tolerance_already_included': 'NOT_SPECIFIED',
                          'conditional_arithmetic_uF': 3.978,
                          'conditional_arithmetic': '5.2 * 0.90 * 0.85; only if those deratings are independent and not already included; not a guaranteed lower bound.'},
    'direct_VBUS_capacitance': {
        'current': {'C1_uF': 2.2, 'C11_uF': 4.7, 'nominal_sum_uF': 6.9,
                    'initial_10pct_range_uF': [6.21, 7.59]},
        'rejected_automatic_C11_10uF': {'nominal_sum_uF': 12.2, 'initial_10pct_range_uF': [10.98, 13.42]},
        'scope': 'Only C1+C11 directly on VBUS, excluding other input capacitance and startup loads. These sums do not certify the complete USB port or inrush charge.',
        'C9_is_behind_BQ_and_LDO': True, 'inrush_measured': False},
    'manufacturer_questions': {
        'Raytac': ['Are the section8.3 10uF figures nominal examples or effective minima?',
                   'What effective capacitance/ESR limits apply separately to VDD/VDDH and VBUS?',
                   'Is C11 CL10A475KP8NNNC 4.7uF/10V acceptable on VBUS with the separate C1=2.2uF USB input load?',
                   'Is C9 CL10A106KP8NNNC 10uF plus100nF appropriate at3.0V?'],
        'Samsung': ['Provide exact C(V,T), Bias TCC, aging and guaranteed versus typical limits for both MPNs.'],
        'JLCPCB': ['Confirm exact MPN procurement and assembly; ordinary CAM approval does not certify Raytac application or inrush.']},
    'sources': [
        {'title': 'Raytac official document index VerL', 'url': 'https://www.raytac.com/download/index.php?index_id=43',
         'limitation': 'No readable bitmap obtained;10uF reference value is supplied by the user, not a claimed visual read.'},
        {'title': 'Samsung CL10A106KP8NNN', 'url': 'https://product.samsungsem.com/mlcc/CL10A106KP8NNN.do'},
        {'title': 'Samsung CL10A475KP8NNN', 'url': 'https://product.samsungsem.com/mlcc/CL10A475KP8NNN.do'},
        {'title': 'TI LM3281 Table6', 'url': 'https://www.ti.com/lit/ds/symlink/lm3281.pdf'},
        {'title': 'TI SLVA129 input capacitance and inrush', 'url': 'https://www.ti.com/lit/pdf/slva129'},
        {'title': 'Nordic nRF52840 power VBUS versus DECUSB', 'url': 'https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html'},
        {'title': 'Nordic nRF52840 PS v1.9 section5.3.8.6 page156', 'url': 'https://docs-be.nordicsemi.com/bundle/nRF52840_PS_v1.9/raw/resource/enus/nRF52840_PS_v1.9.pdf'}],
    'hardware_tested': False, 'simulation_run': False, 'manufacturer_contacted': False,
    'manufacturer_approval_received': False,
}
assert sha(board_path) == board_hash
report['source_unchanged_during_read'] = True
save('reports/production_caps_A1.json', report)

# Retain original computation/input hashes. Explicitly record how old analyses
# apply to this metadata-only revision; never call this a new graph/PDN analysis.
for path in ['reports/power_routing_review.json', 'reports/power_audit_A1.json',
             'reports/charge_startup_final_A1.json']:
    d = json.loads((ROOT / path).read_text())
    refset = list(d.get('native_readback', {}).get('components', {}))
    current = {}
    differences = []
    for ref in refset:
        current[ref], mis = read_component(ref)
        differences.extend(mis)
        old = d['native_readback']['components'][ref]
        if old['value'] != current[ref]['value']:
            differences.append({'ref': ref, 'old_value': old['value'], 'current_value': current[ref]['value']})
        for pin, oldnet in old.get('pads', {}).items():
            if isinstance(oldnet, dict):
                oldnet = oldnet.get('pcb_net')
            if pin not in current[ref]['pads'] or current[ref]['pads'][pin]['pcb_net'] != oldnet:
                differences.append({'ref': ref, 'pin': pin, 'old_net': oldnet, 'current_pad': current[ref]['pads'].get(pin)})
    assert not differences, (path, differences)
    d['current_source_sha256'] = board_hash
    d['current_applicability'] = {
        'status': 'APPLICABLE_WITH_VERIFIED_IDENTICAL_GEOMETRY_AND_CHECKED_POWER_COMPONENTS',
        'current_source_sha256': board_hash, 'schematic_netlist_sha256': sha(netxml_path),
        'geometry_proof_path': proof_path, 'geometry_proof_sha256': sha(proof_path),
        'fresh_native_refs_checked': refset, 'fresh_native_components': current,
        'netlist_and_previous_power_component_mismatches': differences,
        'C9_change': 'Only C9 value/MPN/JLC/note changed; see production_caps_A1.json for current capacitance conclusions. No old current/startup estimate is claimed newly measured or simulated.',
        'computation_rerun': False,
        'method': 'Fresh native readback versus current XML and previous component nets/values, plus complete CAD geometry equivalence. Original computation hashes retained.'}
    save(path, d)
print(json.dumps({'status': report['status'], 'current_source_sha256': board_hash,
                  'caps_read': refs, 'legacy_reports_current_applicability_added': 3}))
