#!/usr/bin/env python3
"""Package the editable project and current evidence, excluding old checkpoints."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REPORTS=(
    'Ankle_Sensor_V1_A1_schematic.pdf','Ankle_Sensor_V1_A1_mechanical_review.step',
    'Ankle_Sensor_V1_A1_3d_review.png','Ankle_Sensor_V1.net.xml',
    'bom_draft.csv','bom_from_design.csv','pinmap.csv','erc_current.json','drc_final.json',
    'validation_status.json','kicad_checks_status.json','charge_temperature_corners.json',
    'static_design_verification.json','static_design_verification.md',
    'footprint_inventory.json','footprint_flash_usb_audit.json','imu_rf_pad_geometry.csv',
    'mechanical_placement_review.json','rf_filled_copper_review.json',
    'signal_geometry_review.json','return_path_review.json','usb_routing_review.json',
    'power_routing_review.json','via_pad_audit.json','pcb_native_statistics.json',
    'manufacturing_geometry_review.json','manufacturing_export_log.txt','pcb_placement.svg',
    'repair_merge_final.json','repair_merge_lfxo.json','repair_merge_c3_via.json',
    'repair_merge_flash_power.json','flash_decoupling_repair.json',
    'lfxo_repair_report.json','c3_via_repair.json','final_board_metadata.json',
    'audit_geometry_changes_A1.json','audit_charge_default_A1.json',
    'audit_merge_root_A1.json','audit_merge_final_A1.json',
    'drc_audit_all_checks_before.json','erc_audit_all_checks_before.json',
    'drc_audit_geometry_candidate.json','drc_audit_charge_candidate.json',
    'erc_audit_charge_candidate.json','via_pad_audit_A1_candidate.json',
    'flash_compatibility_A1.json','power_audit_A1.json','usb_raytac_audit_A1.json',
    'audit_changed_files.txt','baselines/A1_before_audit_manifest.json',
    'baselines/A1_routed_before_audit_2026-10-29.zip',
    'baselines/A1_before_final_verification_2026-10-29.zip',
    'baselines/A1_before_final_verification_manifest.json',
    'charge_startup_final_A1.json','pcba_testability_final_A1.json','usb_stackup_final_A1.json',
    'usb_width_correction_A1.json','usb_audit_netlist_A1.xml','provenance_final_A1.json',
    'github_verification_final_A1.json','final_verification_A1.json','current_A1_manifest.json',
    'package_native_validation_A1.json',
    'final_changed_files_A1.txt',
)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', default='Ankle_Sensor_V1_A1_FINAL_REVIEW.zip')
    args=parser.parse_args()
    archive=ROOT/args.archive
    preserved={'Ankle_Sensor_V1_A0_REVIEW.zip','Ankle_Sensor_V1_A1_REVIEW.zip','Ankle_Sensor_V1_A1_AUDIT_REVIEW.zip'}
    if archive.name in preserved:
        raise SystemExit('Refusing to overwrite a preserved A0/A1 baseline archive')
    validation=json.loads((ROOT/'reports/validation_status.json').read_text())
    board=ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb'
    board_hash=sha(board)
    for key in ('erc_errors','drc_geometry_errors','drc_warnings','unconnected_items','schematic_parity_findings'):
        assert validation[key]==0,key
    for rel,expected in validation['inputs'].items():
        assert sha(ROOT/rel)==expected,rel
    export=json.loads((ROOT/'manufacturing/review/export_manifest.json').read_text())
    assert export['board_sha256']==board_hash
    for rel,expected in export['files'].items():
        assert sha(ROOT/rel)==expected,rel
    for filename,key in (
        ('rf_filled_copper_review.json','board_sha256_at_read'),
        ('signal_geometry_review.json','board_sha256'),
        ('return_path_review.json','board_sha256'),
        ('usb_routing_review.json','canonical_board_sha256'),
        ('manufacturing_geometry_review.json','board_sha256'),
        ('power_routing_review.json','source_sha256'),
        ('via_pad_audit.json','source_sha256'),
    ):
        data=json.loads((ROOT/'reports'/filename).read_text())
        assert data[key]==board_hash,filename
    current=json.loads((ROOT/'reports/current_A1_manifest.json').read_text())
    assert current['board_sha256']==board_hash
    for rel,expected in current['files_sha256'].items():
        assert sha(ROOT/rel)==expected,rel
    files={ROOT/'README.md',ROOT/'.gitignore'}
    for folder in ('hardware','docs','scripts','manufacturing','reports/guide'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and not p.name.startswith('.')
                     and not any(part.endswith('-backups') for part in p.parts)
                     and not p.name.endswith(('.pyc','.kicad_prl','.lck')))
    for name in REPORTS:
        p=ROOT/'reports'/name
        assert p.is_file(),str(p)
        files.add(p)
    metadata={
        'status':'A1_FINAL_REVIEW_CONDITIONAL_READY_NOT_ORDER_RELEASE',
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'kicad_version':validation['kicad_version'],'board_sha256':board_hash,
        'native_drc':{'violations':0,'unconnected_items':0,'schematic_parity':0},
        'native_erc':{'errors':0,'warnings':2,'review':'Intentional grounded IMU pins2/3; see validation_status.json'},
        'project':'hardware/Ankle_Sensor_V1.kicad_pro',
        'outputs':{'editable_schematic_and_routed_pcb':True,'jlc_bom_and_cpl_review':True,
                   'gerber_and_excellon_review':True,'native_step':True,'complete_vendor_3d_assembly':False},
        'prototype_status':'CONDITIONAL READY',
        'open_gates':'docs/release_checklist.md',
        'step_limitations':'Missing USB-C model, generic Raytac, Flash envelope, IMU height limit; no battery/case',
        'assembly_limitations':'Native footprint anchors/rotations, JLC translations and procurement unconfirmed',
        'physical_qualification':'Firmware and physical prototype tests are outstanding',
        'audit_report':'docs/final_verification_A1.md',
        'ignored_check_classes':{'erc':validation['erc_ignored_checks'],
                                 'drc':validation['drc_ignored_checks']},
        'preserved_baseline':'reports/baselines/A1_routed_before_audit_2026-10-29.zip',
        'current_source_manifest':'reports/current_A1_manifest.json',
        'commit_delivery':'Final Git bundle and final_commit_delivery_A1.json are delivered beside this archive after committing; not recursively included',
        'files_without_manifest_or_checksum_list':len(files)
    }
    manifest=ROOT/'reports/review_package_manifest.json'
    manifest.write_text(json.dumps(metadata,indent=2)+'\n');files.add(manifest)
    checksums=ROOT/'reports/source_hashes.sha256'
    checksums.write_text(''.join(sha(p)+'  '+str(p.relative_to(ROOT))+'\n' for p in sorted(files)))
    files.add(checksums)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(p,str(Path(archive.stem)/p.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)
    result={'archive':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,
            'file_count':len(files),'crc_check':'PASS','board_sha256':board_hash,
            'fabrication_release':False}
    (ROOT/'reports/package_integrity.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
