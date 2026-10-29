#!/usr/bin/env python3
"""Vendor-referenced KiCad library imports for U3/U4, with reproducible manifest.

Run with KiCad's bundled Python to validate loading and extract pad geometry.
Does not edit the electrical schematic or generate a PCB.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil
import uuid

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
LIB = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
DEST = ROOT / 'hardware/footprints/AnkleSensor.pretty'
MODELS = ROOT / 'hardware/3dmodels'
REPORTS = ROOT / 'reports'
SOURCES = ROOT / 'hardware/geometry_sources'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mm(v):
    return round(pcbnew.ToMM(v), 6)


def main():
    for p in (DEST, MODELS, REPORTS, SOURCES):
        p.mkdir(parents=True, exist_ok=True)
    ray_src = LIB / 'footprints/RF_Module.pretty/Raytac_MDBT50Q.kicad_mod'
    imu_src = LIB / 'footprints/Package_LGA.pretty/LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.kicad_mod'
    xtal_src = LIB / 'footprints/Crystal.pretty/Crystal_SMD_3215-2Pin_3.2x1.5mm.kicad_mod'
    sym_src = LIB / 'symbols/RF_Module.kicad_sym'
    sym = sym_src.read_text()
    exact = sym[sym.index('(symbol "MDBT50Q-P1MV2"'):sym.index('(symbol "MDBT50Q-P512K"')]
    assert '(extends "MDBT50Q-1MV2")' in exact
    assert '(property "Footprint" "RF_Module:Raytac_MDBT50Q"' in exact

    original_names = [
        ('RF_Module.3dshapes/Raytac_MDBT50Q.step', 'Raytac_MDBT50Q.step'),
        ('Package_LGA.3dshapes/LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step',
         'LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step'),
        ('Crystal.3dshapes/Crystal_SMD_3215-2Pin_3.2x1.5mm.step',
         'Crystal_SMD_3215-2Pin_3.2x1.5mm.step'),
    ]
    model_manifest = []
    for relative, name in original_names:
        src = LIB / '3dmodels' / relative
        dest = MODELS / name
        shutil.copyfile(src, dest)
        model_manifest.append({'source': str(src), 'destination': str(dest.relative_to(ROOT)), 'sha256': sha(dest)})
        if name == 'Raytac_MDBT50Q.step':
            model_manifest[-1].update({
                'status': 'GENERIC_KICAD_MODEL_NOT_VERIFIED_P1MV2_VENDOR_CAD',
                'selected_mpn': 'MDBT50Q-P1MV2',
                'library_model_bounds_mm': [[-5.25, 5.25], [-7.75, 7.75], [0, 2.06]],
                'manufacturer_nominal_body_mm': [10.5, 15.5, 2.0],
                'limitation': 'Rendered asset contains a discrete antenna block resembling the chip-antenna variant; selected P1MV2 specifies PCB antenna. Visual inference only. Base outline matches but exact antenna geometry and maximum tolerance envelope are not verified.',
                'manufacturer_source_url': 'https://www.raytac.com/product/ins.php?index_id=47',
            })

    ray = ray_src.read_text().replace(
        '${KICAD10_3DMODEL_DIR}/RF_Module.3dshapes/Raytac_MDBT50Q.step',
        '${KIPRJMOD}/3dmodels/Raytac_MDBT50Q.step')
    ray_dest = DEST / 'Raytac_MDBT50Q.kicad_mod'
    ray_dest.write_text(ray)

    imu_name = 'ST_LSM6DSV32X_LGA14_3x2.5mm_P0.5mm'
    imu = imu_src.read_text().replace(
        '(footprint "LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y"',
        f'(footprint "{imu_name}"', 1)
    imu = imu.replace('(property "Value" "LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y"',
                      f'(property "Value" "{imu_name}"')
    imu = imu.replace('(descr "LGA, 14 Pin (https://www.st.com/resource/en/datasheet/lsm6ds3tr-c.pdf)")',
                      '(descr "LSM6DSV32X: DS13511 Fig33, TN1383 pad +0.1mm. Derived from KiCad LGA14 library. Review docs/footprint_review.md")')
    imu = imu.replace('(size 0.625 0.35)', '(size 0.575 0.35)')
    imu = imu.replace('(size 0.35 0.625)', '(size 0.35 0.575)')
    imu = imu.replace('\t(attr smd)', '\t(attr smd)\n\t(solder_paste_margin_ratio -0.05)')
    imu = imu.replace('${KICAD10_3DMODEL_DIR}/Package_LGA.3dshapes/LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step',
                      '${KIPRJMOD}/3dmodels/LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step')
    zone_id = str(uuid.uuid5(uuid.NAMESPACE_URL, 'ankle-sensor-v1/imu-top-central-keepout'))
    zone = f'''\n\t(zone
        (layer "F.Cu")
        (uuid "{zone_id}")
        (hatch full 0.508)
        (connect_pads (clearance 0))
        (min_thickness 0.254)
        (keepout (tracks not_allowed) (vias not_allowed) (pads allowed)
                 (copperpour not_allowed) (footprints allowed))
        (polygon (pts (xy -0.85 -0.6) (xy 0.85 -0.6)
                      (xy 0.85 0.6) (xy -0.85 0.6)))
    )
'''
    imu = imu.replace('\t(embedded_fonts no)', zone + '\t(embedded_fonts no)')
    imu_dest = DEST / (imu_name + '.kicad_mod')
    imu_dest.write_text(imu)
    xtal_name = 'Crystal_SMD_3215-2Pin_3.2x1.5mm'
    xtal = xtal_src.read_text().replace(
        '${KICAD10_3DMODEL_DIR}/Crystal.3dshapes/Crystal_SMD_3215-2Pin_3.2x1.5mm.step',
        '${KIPRJMOD}/3dmodels/Crystal_SMD_3215-2Pin_3.2x1.5mm.step')
    xtal_dest = DEST / (xtal_name + '.kicad_mod')
    xtal_dest.write_text(xtal)

    components = {c['ref']: c for c in json.loads((ROOT / 'hardware/design.json').read_text())['components']}
    manifest = {'kicad_version': pcbnew.GetBuildVersion(), 'date': '2026-10-28', 'footprints': [], 'models': model_manifest}
    rows = []
    for ref, src, dest, name, count in (
        ('U3', ray_src, ray_dest, 'Raytac_MDBT50Q', 61),
        ('U4', imu_src, imu_dest, imu_name, 14),
        ('Y1', xtal_src, xtal_dest, xtal_name, 2),
    ):
        f = pcbnew.FootprintLoad(str(DEST), name)
        assert f is not None
        pads = sorted(f.Pads(), key=lambda p: int(p.GetNumber()))
        assert len(pads) == count
        assert {p.GetNumber() for p in pads} == {str(i) for i in range(1, count + 1)}
        assert set(components[ref]['pins']) == {p.GetNumber() for p in pads}
        assert len(list(f.Zones())) == {'U3': 2, 'U4': 1, 'Y1': 0}[ref]
        for p in pads:
            pos, size = p.GetPosition(), p.GetSize()
            paste = p.GetSolderPasteMargin(pcbnew.F_Paste)
            if ref == 'U4':
                dims = sorted((mm(size.x), mm(size.y)))
                assert dims == [0.35, 0.575]
            rows.append({'reference': ref, 'footprint': name, 'pad': p.GetNumber(),
                         'x_mm': mm(pos.x), 'y_mm': mm(pos.y),
                         'rotation_deg': p.GetOrientationDegrees(),
                         'size_x_mm': mm(size.x), 'size_y_mm': mm(size.y),
                         'paste_margin_x_mm': mm(paste.x), 'paste_margin_y_mm': mm(paste.y),
                         'net': components[ref]['pins'][p.GetNumber()] or 'NC'})
        manifest['footprints'].append({'reference': ref, 'name': name, 'source': str(src),
            'source_sha256': sha(src), 'project_path': str(dest.relative_to(ROOT)),
            'project_sha256': sha(dest), 'pads': count, 'zones': len(list(f.Zones())),
            'validation': 'Native KiCad FootprintLoad passed; pad numbering matches design.json'})
    with (REPORTS / 'imu_rf_pad_geometry.csv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (SOURCES / 'imu_rf_geometry.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('U3: 61 pads/2 zones; U4: 14 pads/1 zone; Y1: 2 pads. Native loading and design.json pad sets verified.')


if __name__ == '__main__':
    main()
