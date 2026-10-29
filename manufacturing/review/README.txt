A1 PRODUCTION REVIEW - CONDITIONAL READY; NOT AN ASSEMBLY ORDER RELEASE
Real KiCad 10.0.7 exports from the PCB hash in export_manifest.json.
Shared drill/place origin: native (50,101.6) mm, bottom-left board corner.
Gerber/drill/CPL: mm, X right, Y up. Profile centreline: 30 x 51.6 mm.
Four copper layers: F.Cu, In1.Cu(GND), In2.Cu(mixed), B.Cu.
Requested profile: JLC7628, 4L/1.0 mm nominal, outer1oz/inner0.5oz, green/ENIG.
Published: pp0.2104 / core0.400 / pp0.2104 mm; Cu0.035/0.0152/0.0152/0.035.
JLC must confirm current pressed stack/Dk and exact order compatibility.
See hardware/manufacturing_profile_A1.json and docs/production_usb_A1.md.
Native generic Gerber Job is in reference/, explicitly NOT FOR ORDER;
it is excluded from this Gerber/Drill upload ZIP.
USB retained In2 trunk0.17/0.13 mm: nominal2D model about94 ohm ground-only,
about87 ohm conditional coplanar3V0. Full-route90 ohm/USB eye unqualified.
B.Paste is intentionally empty; 59 components assembled on Top only.
Drill tool sizes, hole counts and plated slots: see drill/drill_report.txt.
CPL preserves native rotations: JLC translations/pin1 preview unapproved.
C9 now10uF nominal; C11 remains4.7uF. Raytac VBUS/Ceff and exact
U3/J1/Y1 land drawings require confirmation before release.
JLC: confirm current stack and BOM/CPL/sourcing/panel/mask/stencil DFM.
Standard PCBA; X-ray for Raytac U3 and IMU U4. Battery/harness not fitted.
Physical Flash/IMU/BLE/USB/charging/thermal qualification follows prototypes;
start with limited bench supply, not an unqualified real LiPo.
See ../../docs/release_checklist.md in the full project package.
