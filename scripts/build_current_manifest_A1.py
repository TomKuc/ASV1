#!/usr/bin/env python3
"""Bind one current A1 production-review source and its actual evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = [
    'validation_status.json', 'drc_final.json', 'erc_current.json',
    'Ankle_Sensor_V1.net.xml', 'bom_draft.csv', 'bom_from_design.csv', 'pinmap.csv',
    'manufacturing_geometry_review.json', 'via_pad_audit.json',
    'rf_filled_copper_review.json', 'mechanical_placement_review.json',
    'return_path_review.json', 'usb_routing_review.json', 'signal_geometry_review.json',
    'production_changes_A1.json', 'production_geometry_equivalence_A1.json',
    'production_caps_A1.json', 'production_footprints_A1.json',
    'production_usb_A1.json', 'production_pcba_dfm_A1.json',
    'production_component_status_A1.csv', 'production_readiness_A1.json',
    'production_provenance_A1.json', 'github_verification_production_A1.json',
    'package_native_validation_A1.json', 'production_changed_files_A1.txt',
    'Ankle_Sensor_V1_A1_schematic.pdf', 'Ankle_Sensor_V1_A1_mechanical_review.step',
    'Ankle_Sensor_V1_A1_3d_review.png']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data(rel):
    return json.loads((ROOT/rel).read_text())


def main():
    board_sha = digest(ROOT/'hardware/Ankle_Sensor_V1.kicad_pcb')
    validation = data('reports/validation_status.json')
    for key in ('erc_errors', 'drc_geometry_errors', 'drc_warnings',
                'unconnected_items', 'schematic_parity_findings'):
        assert validation[key] == 0, key
    assert validation['erc_ignored_checks'] == validation['drc_ignored_checks'] == []
    for rel, expected in validation['inputs'].items():
        assert digest(ROOT/rel) == expected, rel
    assert 'hardware/Ankle_Sensor_V1.kicad_dru' in validation['inputs']
    export = data('manufacturing/review/export_manifest.json')
    assert export['board_sha256'] == board_sha
    for rel, expected in export['files'].items():
        assert digest(ROOT/rel) == expected, rel
    for name, key in (
        ('return_path_review.json', 'board_sha256'),
        ('signal_geometry_review.json', 'board_sha256'),
        ('production_caps_A1.json', 'current_source_sha256'),
        ('usb_routing_review.json', 'canonical_board_sha256'),
        ('via_pad_audit.json', 'source_sha256'),
        ('manufacturing_geometry_review.json', 'board_sha256'),
        ('rf_filled_copper_review.json', 'board_sha256_at_read'),
        ('mechanical_placement_review.json', 'board_sha256_at_read'),
        ('production_footprints_A1.json', 'board_sha256'),
        ('production_usb_A1.json', 'board_sha256'),
        ('production_pcba_dfm_A1.json', 'board_sha256'),
        ('package_native_validation_A1.json', 'board_sha256')):
        assert data('reports/'+name)[key] == board_sha, name
    proof = data('reports/production_geometry_equivalence_A1.json')
    assert proof['after_sha256'] == board_sha
    assert proof['all_other_root_blocks_including_filled_zones_unchanged']
    portable = data('reports/package_native_validation_A1.json')
    for rel, expected in portable['hardware_files_sha256'].items():
        assert digest(ROOT/rel) == expected, rel
    summary = data('reports/production_readiness_A1.json')
    assert summary['board_sha256'] == board_sha
    assert summary['fabrication_release'] is False
    paths = {ROOT/'README.md', ROOT/'.gitignore'}
    for folder in ('hardware', 'manufacturing/review', 'docs', 'scripts'):
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file()
                     and not p.name.startswith('.') and '__pycache__' not in p.parts
                     and not any(part.endswith('-backups') for part in p.parts)
                     and not p.name.endswith(('.lck', '.kicad_prl', '.pyc')))
    paths.update(ROOT/'reports'/name for name in REPORTS)
    manifest = {
        'revision': 'A1_PRODUCTION_REVIEW', 'status': summary['status'],
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'source_base_commit': 'b17f1457de876ecb27e94dc514c9a4844be44bc0',
        'board_sha256': board_sha,
        'project': 'hardware/Ankle_Sensor_V1.kicad_pro',
        'mandatory_custom_rules': 'hardware/Ankle_Sensor_V1.kicad_dru',
        'manufacturing_profile': 'hardware/manufacturing_profile_A1.json',
        'current_package': 'Ankle_Sensor_V1_A1_PRODUCTION_REVIEW.zip',
        'fabrication_upload_zip': 'manufacturing/review/Ankle_Sensor_V1_A1_GERBERS_DRILL_REVIEW.zip',
        'reference_only_not_for_upload': ['manufacturing/review/reference/KiCad_generic_stackup_NOT_FOR_ORDER.json'],
        'authoritative_checks': 'reports/validation_status.json',
        'authoritative_decision': 'docs/production_readiness_A1.md',
        'gate_A': summary['gate_A'], 'fabrication_release': False,
        'historical_evidence_policy': 'Old reports retain original computation hashes. New production reports and geometry equivalence state current applicability; no hardware tests implied.',
        'github_state': 'NOT_VERIFIED; no push; see github_verification_production_A1.json',
        'commit_identity_delivery': 'reports/production_commit_delivery_A1.json (created after commit, outside its own tree)',
        'historical_packages': ['Ankle_Sensor_V1_A0_REVIEW.zip', 'Ankle_Sensor_V1_A1_REVIEW.zip', 'Ankle_Sensor_V1_A1_AUDIT_REVIEW.zip', 'Ankle_Sensor_V1_A1_FINAL_REVIEW.zip'],
        'self_hash': 'Recorded by reports/source_hashes.sha256, excluded from own hash map',
        'files_sha256': {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}}
    (ROOT/'reports/current_A1_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'status': manifest['status'], 'files': len(paths), 'board_sha256': board_sha}))


if __name__ == '__main__':
    main()
