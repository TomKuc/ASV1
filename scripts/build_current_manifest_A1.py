#!/usr/bin/env python3
"""Bind current A1 source, checks and exports; never declares fabrication release."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = [
    {'id':'A01','status':'OPEN','condition':'Literal Raytac8.3 and manufacturer drawings for Raytac/J1/Y1 reviewed and accepted'},
    {'id':'A02','status':'OPEN','condition':'JLC confirms selected JLC7628 4L1.0mm pressed stack, Dk/Cu definitions and USB geometry acceptance'},
    {'id':'A03','status':'OPEN','condition':'Standard PCBA exact33BOMgroups/59TOP parts, procurement incl U7/R1/R20, CPL pin1/rotation and XrayU3/U4 accepted'},
    {'id':'A04','status':'OPEN','condition':'CAM/panel/rails/fiducials/mask/stencil/tenting/drill-clearance DFM accepted'}]
REPORTS = [
    'validation_status.json','drc_final.json','erc_current.json',
    'Ankle_Sensor_V1.net.xml','bom_draft.csv','bom_from_design.csv','pinmap.csv',
    'manufacturing_geometry_review.json','via_pad_audit.json',
    'rf_filled_copper_review.json','mechanical_placement_review.json',
    'signal_geometry_review.json','return_path_review.json','usb_routing_review.json',
    'usb_raytac_audit_A1.json','power_routing_review.json','power_audit_A1.json',
    'charge_startup_final_A1.json','pcba_testability_final_A1.json',
    'usb_stackup_final_A1.json','usb_width_correction_A1.json',
    'flash_compatibility_A1.json','charge_temperature_corners.json',
    'github_verification_final_A1.json','provenance_final_A1.json','package_native_validation_A1.json',
    'Ankle_Sensor_V1_A1_schematic.pdf','Ankle_Sensor_V1_A1_mechanical_review.step',
    'Ankle_Sensor_V1_A1_3d_review.png']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data(rel):
    return json.loads((ROOT/rel).read_text())


def main():
    board = ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb'
    board_sha = digest(board)
    validation = data('reports/validation_status.json')
    for key in ('erc_errors','drc_geometry_errors','drc_warnings','unconnected_items','schematic_parity_findings'):
        assert validation[key] == 0, key
    assert validation['erc_ignored_checks'] == validation['drc_ignored_checks'] == []
    for rel, expected in validation['inputs'].items():
        assert digest(ROOT/rel) == expected, rel
    assert 'hardware/Ankle_Sensor_V1.kicad_dru' in validation['inputs']
    export = data('manufacturing/review/export_manifest.json')
    assert export['board_sha256'] == board_sha
    for rel, expected in export['files'].items():
        assert digest(ROOT/rel) == expected, rel
    for name,key in [
        ('signal_geometry_review.json','board_sha256'),
        ('return_path_review.json','board_sha256'),
        ('usb_routing_review.json','canonical_board_sha256'),
        ('power_routing_review.json','source_sha256'),
        ('via_pad_audit.json','source_sha256'),
        ('manufacturing_geometry_review.json','board_sha256'),
        ('rf_filled_copper_review.json','board_sha256_at_read'),
        ('mechanical_placement_review.json','board_sha256_at_read'),
        ('pcba_testability_final_A1.json','board_sha256'),
        ('usb_stackup_final_A1.json','board_sha256')]:
        assert data('reports/'+name)[key] == board_sha, name
    assert data('reports/charge_startup_final_A1.json')['inputs_sha256']['hardware/Ankle_Sensor_V1.kicad_pcb'] == board_sha
    summary = {
        'revision':'A1_FINAL_PROTOTYPE_REVIEW','status':'CONDITIONAL READY',
        'quantity':[3,5],'board_sha256':board_sha,
        'report':'docs/final_verification_A1.md','gate_A':GATES,
        'confirmed_corrections':['18USBtrunk widths0.15to0.17mm, same centrelines; explicit0.125mm pair-only rule',
                                 'Firmware contract clarified for hangLOW/SystemOFF and no-reset-loop charging policy',
                                 'One current source/export index; historical hashes/deliveries labelled',
                                 'Generic KiCad GerberJob moved outside fabrication upload ZIP'],
        'native_checks':{k:validation[k] for k in ('erc_errors','erc_warnings','drc_geometry_errors','drc_warnings','unconnected_items','schematic_parity_findings','erc_ignored_checks','drc_ignored_checks')},
        'group_B':'Physical Flash20tests, acquisition/timing, IMU/BLE/USB, power/startup/charging/thermal and pack qualification after prototypes; before real LiPo use',
        'group_C':'Standby/size/ergonomics, dedicated QSPI TP or Flash isolation, MCU cell-temperature reading/heartbeat',
        'hardware_tests_performed':False,'firmware_implemented':False,
        'order_placed':False,'fabrication_release':False,'github_current_commit_verified':False}
    (ROOT/'reports/final_verification_A1.json').write_text(json.dumps(summary,indent=2)+'\n')
    paths = set()
    for folder in ('hardware','manufacturing/review'):
        for path in (ROOT/folder).rglob('*'):
            if path.is_file() and not path.name.startswith('.') and not path.name.endswith(('.lck','.kicad_prl','.pyc')) and not any(p.endswith('-backups') or p=='__pycache__' for p in path.parts):
                paths.add(path)
    paths.update(ROOT/'reports'/name for name in REPORTS)
    paths.add(ROOT/'reports/final_verification_A1.json')
    paths.add(ROOT/'README.md')
    paths.update(ROOT/'docs'/name for name in (
        'final_verification_A1.md','release_checklist.md','charge_startup_final_A1.md',
        'usb_stackup_final_A1.md','pcba_testability_final_A1.md','firmware_contract.md',
        'flash_firmware_test_plan_A1.md','github_delivery_final_A1.md'))
    manifest = {'revision':'A1_FINAL_PROTOTYPE_REVIEW','status':'CONDITIONAL READY',
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'source_base_commit':'28d88f22a6a9c0c0e1feb639546009518a6b5f8e',
        'board_sha256':board_sha,'project':'hardware/Ankle_Sensor_V1.kicad_pro',
        'mandatory_custom_rules':'hardware/Ankle_Sensor_V1.kicad_dru',
        'manufacturing_profile':'hardware/manufacturing_profile_A1.json',
        'current_package':'Ankle_Sensor_V1_A1_FINAL_REVIEW.zip',
        'fabrication_upload_zip':'manufacturing/review/Ankle_Sensor_V1_A1_GERBERS_DRILL_REVIEW.zip',
        'reference_only_not_for_upload':['manufacturing/review/reference/KiCad_generic_stackup_NOT_FOR_ORDER.json'],
        'authoritative_checks':'reports/validation_status.json',
        'gate_A':GATES,'fabrication_release':False,
        'github_state':'NOT_VERIFIED; see final_commit_delivery_A1.json and verify_github_A1.py after import/push',
        'commit_identity_delivery':'reports/final_commit_delivery_A1.json (created after commit, outside its own tree)',
        'historical_packages':['Ankle_Sensor_V1_A0_REVIEW.zip','Ankle_Sensor_V1_A1_REVIEW.zip','Ankle_Sensor_V1_A1_AUDIT_REVIEW.zip'],
        'self_hash':'Recorded by reports/source_hashes.sha256; not included in own hash map',
        'files_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)}}
    (ROOT/'reports/current_A1_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':manifest['status'],'files':len(paths),'board_sha256':board_sha}))


if __name__ == '__main__':
    main()
