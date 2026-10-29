#!/usr/bin/env python3
"""Export real KiCad fabrication data after a current, connected native DRC.

This produces REVIEW data, never a fabrication release or rotation approval.
All coordinates use the PCB's drill/place origin. JLC format reference:
https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad
"""
from pathlib import Path
from collections import defaultdict
import csv
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'manufacturing/review'
PCB = ROOT / 'hardware/Ankle_Sensor_V1.kicad_pcb'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    validation = json.loads((ROOT/'reports/validation_status.json').read_text())
    for key in ('erc_errors', 'drc_geometry_errors', 'drc_warnings',
                'unconnected_items', 'schematic_parity_findings'):
        if validation[key] != 0:
            raise SystemExit('Export refused: ' + key + '=' + str(validation[key]))
    for rel, expected in validation['inputs'].items():
        if digest(ROOT/rel) != expected:
            raise SystemExit('Export refused: validation input changed: ' + rel)
    OUT.mkdir(parents=True, exist_ok=True)
    for folder in ('gerbers', 'drill', 'assembly'):
        (OUT/folder).mkdir(exist_ok=True)
    log = []
    commands = []

    def cli(*args):
        command = ['sh', str(ROOT/'scripts/kicad_cli.sh'), *map(str, args)]
        result = subprocess.run(command, cwd=ROOT, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        commands.append({'arguments': list(map(str,args)), 'exit_code': result.returncode})
        log.append('$ kicad-cli ' + ' '.join(map(str,args)) + '\n' + result.stdout)
        (ROOT/'reports/manufacturing_export_log.txt').write_text('\n'.join(log))
        if result.returncode:
            raise SystemExit('KiCad export failed; see reports/manufacturing_export_log.txt')

    cli('pcb', 'export', 'gerbers', '--output', str(OUT/'gerbers')+'/',
        '--layers', 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts',
        '--check-zones', '--use-drill-file-origin', '--no-protel-ext', PCB)
    cli('pcb', 'export', 'drill', '--output', str(OUT/'drill')+'/',
        '--format', 'excellon', '--drill-origin', 'plot', '--excellon-units', 'mm',
        '--excellon-separate-th', '--generate-map', '--map-format', 'pdf',
        '--generate-report', '--report-path', OUT/'drill/drill_report.txt', PCB)
    positions = OUT/'assembly/KiCad_positions_REVIEW.csv'
    cli('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'front',
        '--smd-only', '--exclude-dnp', '--use-drill-file-origin', '--output', positions, PCB)

    design = json.loads((ROOT/'hardware/design.json').read_text())
    parts = {c['ref']: c for c in design['components'] if c['populate']}
    groups = defaultdict(list)
    for ref, c in parts.items():
        if not c['mpn'] or not re.fullmatch(r'C[0-9]+', c['jlcpcb']):
            raise SystemExit('Missing exact MPN/C number: ' + ref)
        groups[(c['value'], c['footprint'], c['jlcpcb'], c['mpn'], c['status'])].append(ref)
    bom = OUT/'assembly/BOM_REVIEW_NOT_RELEASED.csv'
    with bom.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Comment', 'Designator', 'Footprint', 'JLCPCB Part #',
                         'Manufacturer Part Number', 'Quantity', 'Review Status'])
        for (value, footprint, code, mpn, status), refs in sorted(groups.items()):
            writer.writerow([value, ','.join(refs), footprint, code, mpn, len(refs), status])
    rows = list(csv.DictReader(positions.open()))
    if len(rows) != len(parts) or {r['Ref'] for r in rows} != set(parts):
        raise SystemExit('Native placement references do not equal fitted BOM references')
    cpl = OUT/'assembly/CPL_REVIEW_ROTATIONS_UNCONFIRMED.csv'
    with cpl.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer'])
        for r in rows:
            if r['Side'] != 'top':
                raise SystemExit('Unexpected bottom-side assembled part: ' + r['Ref'])
            if not (0 <= float(r['PosX']) <= 30 and 0 <= float(r['PosY']) <= 51.6):
                raise SystemExit('Check drill/place origin and placement: ' + r['Ref'])
            # Native origin and rotation retained; no unverified JLC translation.
            writer.writerow([r['Ref'], r['PosX'], r['PosY'], r['Rot'], 'Top'])
    for filename in (positions, bom, cpl):
        (ROOT/'reports/assembly_review'/filename.name).write_bytes(filename.read_bytes())
    gerbers = list((OUT/'gerbers').glob('*.gbr'))
    drills = list((OUT/'drill').glob('*.drl'))
    if len(gerbers) != 11 or len(drills) != 2:
        raise SystemExit('Unexpected native fabrication output count')
    for p in gerbers:
        content = p.read_text()
        if not content.rstrip().endswith('M02*'):
            raise SystemExit('Incomplete Gerber: ' + p.name)
    for p in drills:
        content = p.read_text()
        if not content.startswith('M48') or 'M30' not in content:
            raise SystemExit('Incomplete Excellon: ' + p.name)
    package = OUT/'Ankle_Sensor_V1_A1_GERBERS_DRILL_REVIEW.zip'
    (OUT/'README.txt').write_text(
        'A1 REVIEW - NOT FOR FABRICATION OR ASSEMBLY ORDER\n'
        'Real KiCad 10.0.7 exports from the PCB hash in export_manifest.json.\n'
        'Shared drill/place origin: native (50,101.6) mm, bottom-left board corner.\n'
        'Gerber/drill/CPL: mm, X right, Y up. Profile centreline: 30 x 51.6 mm.\n'
        'Four copper layers: F.Cu, In1.Cu(GND), In2.Cu(mixed), B.Cu.\n'
        'Working thickness 1.0 mm. Gerber job stackup is an automatically generated\n'
        'generic KiCad stack (0.28 mm dielectrics), NOT a selected JLC stackup.\n'
        'No qualified 90-ohm USB impedance or material/finish specification.\n'
        'B.Paste is intentionally empty; 59 components assembled on Top only.\n'
        'Drill tool sizes, hole counts and plated slots: see drill/drill_report.txt.\n'
        'CPL preserves native rotations: JLC translations/pin1 preview unapproved.\n'
        'Panel rails/fiducials, exact sourcing, MLCC Ceff, RF/USB, connector/clock\n'
        'land patterns and JLC DFM must be closed before prototype ordering.\n'
        'See ../../docs/release_checklist.md in the full project package.\n')
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(OUT/'README.txt', 'README.txt')
        for folder in ('gerbers', 'drill'):
            for p in sorted((OUT/folder).iterdir()):
                if p.is_file():
                    z.write(p, str(p.relative_to(OUT)))
    summary = {
        'status': 'NATIVE_EXPORTS_FOR_REVIEW_NOT_FABRICATION_RELEASE',
        'kicad_version': validation['kicad_version'], 'board_sha256': digest(PCB),
        'coordinates': 'mm, shared native drill/place origin; positive Y upwards; no bottom mirror',
        'fitted_bom_parts': len(parts), 'bom_groups': len(groups), 'placement_rows': len(rows),
        'placement_policy': 'Native KiCad origins and rotations; JLC part translations NOT applied or approved',
        'checks': 'Current native DRC/parity; BOM/CPL reference equality; Gerber/Excellon termination; SHA256. No independent CAM geometry or JLC DFM approval.',
        'commands': commands,
        'files': {str(p.relative_to(ROOT)): digest(p) for p in sorted(OUT.rglob('*'))
                  if p.is_file() and p.name != 'export_manifest.json'}
    }
    (OUT/'export_manifest.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k: summary[k] for k in ('status','fitted_bom_parts','bom_groups','placement_rows')}))


if __name__ == '__main__':
    main()
