#!/usr/bin/env python3
"""Read A1 USB geometry and reuse explicitly identified, unchanged FVM results.

Run with KiCad's bundled Python. This script never saves the PCB or runs the
field solver. Historical calculations remain identified by their original PCB.
"""
from pathlib import Path
import collections
import hashlib
import json
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'hardware/Ankle_Sensor_V1.kicad_pcb'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before = digest(BOARD)
    proof_path = ROOT / 'reports/production_geometry_equivalence_A1.json'
    proof = json.loads(proof_path.read_text())
    assert proof['after_sha256'] == before
    for key in ['all_copper_uuid_geometry_layer_width_net_unchanged',
                'all_pads_footprint_positions_layers_and_models_unchanged',
                'all_other_root_blocks_including_filled_zones_unchanged']:
        assert proof[key] is True, key
    historic_path = ROOT / 'reports/usb_stackup_final_A1.json'
    historic = json.loads(historic_path.read_text())
    calculated_on = historic.get('computed_on_board_sha256', historic['board_sha256'])
    assert calculated_on == proof['before_sha256']
    reference_path = ROOT / 'reports/return_path_review.json'
    reference = json.loads(reference_path.read_text())
    assert reference['board_sha256'] == before
    board = pcbnew.LoadBoard(str(BOARD))
    footprints = {f.GetReference(): f for f in board.GetFootprints()}
    nets = {}
    for name in ['USB_DP', 'USB_DN', 'USB_DP_CONN', 'USB_DN_CONN']:
        items = [t for t in board.Tracks() if t.GetNetname() == name]
        tracks = [t for t in items if t.Type() != pcbnew.PCB_VIA_T]
        widths = collections.Counter('%.3f' % pcbnew.ToMM(t.GetWidth()) for t in tracks)
        nets[name] = {
            'trace_length_mm': sum(pcbnew.ToMM(t.GetLength()) for t in tracks),
            'width_segment_counts_mm': dict(sorted(widths.items())),
            'via_count': len(items) - len(tracks),
            'actual_pad_connections': [
                {'ref': f.GetReference(), 'pad': p.GetNumber()}
                for f in board.GetFootprints() for p in f.Pads()
                if p.GetNetname() == name],
            'ground_reference_geometry': {
                k: reference['nets'][name][k] for k in
                ['native_projection_gnd_coverage_pct',
                 'max_missing_component_trace_length_sum_mm']}}
    for name in ['USB_DP', 'USB_DN']:
        assert nets[name]['width_segment_counts_mm']['0.170'] == 9
    calculations = [c for c in historic['calculations']
                    if c.get('width_mm') == .17 and c.get('pitch_mm') == .0025
                    and c['mode'] in ['in2', 'in2_coplanar']]
    assert len(calculations) == 2
    module = {p.GetNumber(): p.GetNetname() for p in footprints['U3'].Pads()
              if p.GetNumber() in ['28', '30', '31', '32', '34', '35']}
    out = {
        'date': '2026-10-29', 'status': 'EXTERNAL CONFIRMATION',
        'scope': 'A02 narrow closure; no new routing or FVM run',
        'board_sha256': before, 'native_kicad_version': pcbnew.GetBuildVersion(),
        'native_readback_performed': True, 'board_modified': False,
        'selected_stackup': historic['selected_design_basis'],
        'public_source_rechecked': [
            'https://cart.jlcpcb.com/client/template/placeOrder/impedance.html',
            'https://jlcpcb.com/impedance'],
        'public_listing_confirms_nominal_1mm_7628_option': True,
        'current_order_template_or_factory_acceptance_confirmed': False,
        'native_usb_nets': nets, 'native_raytac_power_and_usb_pads': module,
        'return_path_report': str(reference_path.relative_to(ROOT)),
        'return_path_report_sha256': digest(reference_path),
        'all_gnd_pads_one_native_component': reference['ground_fill']['all_gnd_pads_in_one_native_component'],
        'reused_model_with_verified_identical_geometry': {
            'computed_on_board_sha256': calculated_on,
            'calculation_source': str(historic_path.relative_to(ROOT)),
            'calculation_source_sha256': digest(historic_path),
            'geometry_proof': str(proof_path.relative_to(ROOT)),
            'geometry_proof_sha256': digest(proof_path),
            'new_field_solver_run_performed': False,
            'model': historic['model'], 'calculations': calculations,
            'scope': 'Nominal idealised 2D cross sections only; no full-path bound, factory guarantee or physical measurement'},
        'closed_subchecks': [
            'Exactly eighteen unchanged-centreline In2 trunk segments have width0.17mm/gap0.13mm',
            'Fresh native track/via/pad and stored ground-fill readback; no changed routing',
            'VDD/VDDH=3V0, VBUS=USB5V, DCCH unconnected; USB pin nets remain consistent',
            'No external USB series resistor addition: Nordic documents integrated PHY resistors'],
        'manufacturer_questions_not_sent': [
            'Return current 4-layer1.0mm JLC7628 order template ID and pressed stack, not the default1.6mm table.',
            'Confirm 35/15.2/15.2/35um copper, 0.2104/0.400/0.2104mm dielectric spacings and whether 0.45mm core-with-Cu note is a separate convention.',
            'Confirm Er7628=4.4 or4.6, ErCore=4.6, actual mask profile and laminate thickness tolerance.',
            'For current 0.17/0.13mm In2 pair and surrounding mixed3V0/B signals, confirm fab acceptance and state if90ohm controlled impedance is offered on this geometry.',
            'Report any proposed CAM trace/space or stack modification before applying it; do not silently rescale USB geometry.'],
        'prototype_tests_not_run': [
            'USB FullSpeed12Mb/s transfer/CRC/reconnect and both connector orientations',
            'Actual USB edges/eye using proper FS fixture and cable',
            'System ESD immunity; data-line and clamp return-path behaviour'],
        'decision': 'Retain existing routing for first prototypes; confirm order stack externally before production release. Native plane voids and nonuniform tails are documented, not treated as a proven continuous90ohm line.'}
    assert digest(BOARD) == before
    (ROOT / 'reports/production_usb_A1.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'board_sha256': before, 'status': out['status'],
                      'new_solver_run': False, 'model_source_board': calculated_on}))


if __name__ == '__main__':
    main()
