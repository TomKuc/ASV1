#!/usr/bin/env python3
"""Reload actual packaged hardware with native KiCad, including local libraries/rules."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT/'Ankle_Sensor_V1_A1_PRODUCTION_REVIEW.zip')
    args = parser.parse_args()
    (ROOT/'.work').mkdir(exist_ok=True)
    hardware = {str(p.relative_to(ROOT)): digest(p) for p in (ROOT/'hardware').rglob('*')
                if p.is_file() and not p.name.startswith('.') and '__pycache__' not in p.parts
                and not any(part.endswith('-backups') for part in p.parts)
                and not p.name.endswith(('.pyc','.lck','.kicad_prl'))}
    with tempfile.TemporaryDirectory(prefix='native-package-', dir=ROOT/'.work') as temp:
        temp = Path(temp)
        with zipfile.ZipFile(args.archive) as z:
            assert z.testzip() is None
            found = {}
            for member in z.namelist():
                parts = Path(member).parts
                if 'hardware' not in parts:
                    continue
                i = parts.index('hardware')
                rel = Path(*parts[i:])
                assert '..' not in rel.parts and not rel.is_absolute()
                assert str(rel) in hardware, rel
                target = temp/rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(member))
                found[str(rel)] = digest(target)
        assert found == hardware
        assert 'hardware/Ankle_Sensor_V1.kicad_dru' in found
        cli = ['sh', str(ROOT/'scripts/kicad_cli.sh')]
        for kind, cmd in (
            ('erc', ['sch','erc','--format','json','--severity-all','--output',str(temp/'erc.json'),str(temp/'hardware/Ankle_Sensor_V1.kicad_sch')]),
            ('drc', ['pcb','drc','--format','json','--severity-all','--all-track-errors','--schematic-parity','--refill-zones','--output',str(temp/'drc.json'),str(temp/'hardware/Ankle_Sensor_V1.kicad_pcb')])):
            run = subprocess.run(cli+cmd, cwd=ROOT, text=True, capture_output=True)
            (ROOT/'.work'/('production_package_'+kind+'.log')).write_text(run.stdout+run.stderr)
            assert run.returncode == 0, kind
        erc = json.loads((temp/'erc.json').read_text())
        drc = json.loads((temp/'drc.json').read_text())
        ev = [v for s in erc['sheets'] for v in s['violations']]
        assert sum(v['severity']=='error' for v in ev) == 0
        assert sum(v['severity']=='warning' for v in ev) == 2
        assert not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity']
        assert erc.get('ignored_checks',[]) == drc.get('ignored_checks',[]) == []
        assert all(digest(temp/rel) == expected for rel, expected in hardware.items())
    report = {
        'status':'PASS_EXTRACTED_NATIVE_HARDWARE_RELOAD_NOT_FAB_RELEASE',
        'method':'Extract actual package hardware including rules/libraries; byte-compare every hardware file with current source, then run native ERC/DRC/parity. Result binds the hardware map; subsequent documentation/package timestamp changes do not relabel a hardware test.',
        'archive_name':args.archive.name,
        'archive_binding':'Hardware file SHA256 map below; full final ZIP SHA256 is recorded separately in package_integrity.json to avoid a self-hash cycle.',
        'board_sha256':hardware['hardware/Ankle_Sensor_V1.kicad_pcb'],
        'kicad_version':erc['kicad_version'],
        'drc_violations':0,'unconnected_items':0,'schematic_parity':0,
        'erc_errors':0,'erc_warnings':2,'ignored_checks':[],
        'hardware_file_count':len(hardware),'hardware_files_sha256':hardware,
        'hardware_tests_performed':False}
    (ROOT/'reports/package_native_validation_A1.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='hardware_files_sha256'}))


if __name__ == '__main__':
    main()
