# Ankle Sensor V1 A1 — questions for quotation and engineering review

Draft for the owner to submit; **not sent and not approved**. Quantity: 3–5 assembled prototypes, Standard PCBA. Current package: `Ankle_Sensor_V1_A1_PRODUCTION_REVIEW.zip`; source/hash index: `reports/current_A1_manifest.json`. PCB SHA256: `1d3bb700a2b686ef68589bf3295488d2144a1d51a857cec7651e45be175a6134`. Please return written answers and the final assembly preview/panel drawing before production release. No substitutions or copper changes without approval.

## 1. Stack and USB — A02

Please confirm that your **current order service** supports JLC7628, 4 layers, nominal 1.0 mm, outer 1 oz / inner 0.5 oz, green solder mask, ENIG, and give the selected order-template identifier and pressed stack:

| Layer / dielectric | Published nominal thickness |
|---|---:|
| L1 F.Cu | 0.035 mm |
| 7628 prepreg | 0.2104 mm |
| L2 In1.Cu, GND | 0.0152 mm |
| Core | 0.400 mm |
| L3 In2.Cu | 0.0152 mm |
| 7628 prepreg | 0.2104 mm |
| L4 B.Cu | 0.035 mm |

These values total 1.0212 mm before mask; your legacy page also labels the core-with-copper as 0.45 mm. Please explain base versus finished Cu, nominal versus pressed dielectric distances, total-thickness tolerance, prepreg/core Dk (legacy 7628 Dk 4.6 versus current page 4.4), frequency, and actual mask thickness/Dk. State if the material or order option changes these values.

USB is **Full Speed 12 Mbit/s**. Main pair is on L3, width 0.17 mm, edge gap 0.13 mm, GND on L2. L3 also has nearby +3V0 fill; L4 is mixed copper, not a continuous ground plane. The path includes 0.15 mm separated tails, four vias per net and ESD/connector pads. Our nominal 2D model of the main section gives 94.14 ohm against L2 GND, or 87.16 ohm if nearby +3V0 is treated as an ideal AC reference. Neither is a full-route guarantee or a measured eye diagram.

Please review the **actual layer artwork**, confirm the stack and manufacturable geometry/tolerance, and explain what impedance commitment (if any) your service offers for this nonuniform route. Do not adjust the Cu widths/gap automatically. The automatic KiCad Gerber Job is reference-only and excluded from the fabrication ZIP; do not use its generic stack.

## 2. Exact land patterns and parts — A01 / A03

Please compare supplied lands/pad numbering and pin-1 orientation with the exact supplied component drawings for **Raytac MDBT50Q-P1MV2 (U3), HRO TYPE-C-31-M-12 / C165948 (J1), Abracon ABS07-32.768KHZ-7-T / C276424 (Y1)**. Provide the drawing revision or vendor CAD used. In particular verify J1's two Ø0.65 NPTH, four plated slots (two 0.60×1.70 and two 0.60×1.20 mm), pin row and PCB edge position (local y=+2.60 mm); confirm how the shell anchors, which have no paste apertures, will be soldered. Y1 current pads are 1.00×1.80 mm, centres 2.50 mm apart; verify exact ABS07 recommended land, not ABS07-LR.

BOM has **33 exact-MPN groups, 59 components on Top**. Please confirm all listed MPN/C numbers can be procured and assembled in this Standard PCBA order, including:

- U7: TI **TLV7042DGKR / C2760466**, VSSOP-8.
- R1: UNI-ROYAL **0402WGF2402TCE / C25769**, 24 kΩ, 1%, 0402.
- R20: Yageo **RT0402BRD0727K4L / C852679**, 27.4 kΩ, 0.1%, 0402.
- C9: Samsung **CL10A106KP8NNNC / C19702**, now 10 µF/10 V/X5R/0603; C11 remains CL10A475KP8NNNC/C1705, 4.7 µF.
- Flash remains **Winbond W25Q01JVZEIQ**, 128 MiB; do not substitute voltage/package variants.

See `reports/production_component_status_A1.csv` for the full per-reference matrix. Public catalogue matches are not stock reservations. Native CPL coordinates/angles are unmodified; please supply the translated placement preview and verify pin 1, LED, diodes/MOSFETs/ICs and connector orientations, including origins/rotation offsets. No automatic substitutions.

Please include X-ray for U3's hidden lands and U4 LGA IMU, and confirm WSON exposed-pad/stencil/reflow/inspection process. J2 is fitted. J3 and TP1–TP9 are bare copper contacts, not missing assembly components. Protected battery, bonded NTC and cable/harness are outside PCBA supply.

## 3. Actual CAM, tenting, stencil and panel — A04

At three equal minima, nominal Ø0.25 mm via drill edge to same-net SMD copper **and paste aperture** is 0.150001 mm. Via copper diameter is 0.50 mm, so outer annulus to the SMD mask opening is only about 0.025 mm. Vias are tented on both sides; this is not a claimed 0.025 mm web between two mask openings. Please assess drill registration, actual via-hole process tolerance, mask registration/coverage and solder wicking. Do not substitute your PTH-component-hole tolerance for unspecified via-hole tolerance.

| Adjacent pad | Native via centre X/Y mm | Gerber/CPL-origin X/Y mm | Adjacent pad centre native X/Y mm |
|---|---|---|---|
| U6.2 | 71.400 / 93.300 | 21.400 / 8.300 | 70.4625 / 93.300 |
| C4.2 | 69.150 / 78.300 | 19.150 / 23.300 | 69.150 / 79.025 |
| C5.2 | 71.450 / 78.300 | 21.450 / 23.300 | 71.450 / 79.025 |

Native datum is X=50.000/Y=101.600, exported X right/Y up. Please inspect the actual F.Mask/B.Mask/F.Paste artwork at these locations and confirm acceptability or specify a precise required local correction. No global rerouting is requested.

Please review exposed-pad WSON U1/U5 paste windows, U4 LGA and U3 land stencil, aperture reductions, mask bridges, MSL/bake/reflow requirements and plated USB anchor slots. Gerber set: four Cu + two mask + two paste + two silkscreen + Edge.Cuts; separate PTH/NPTH Excellon. B.Paste is intentionally empty.

Single board is 30×51.6 mm, no added global fiducials/handling rails. Please state whether your Standard line accepts a single board or requires panel rails/fiducials. If panelized, propose a drawing with suitable rails, tooling and fiducials (your guide describes 5 mm rails and 1 mm Cu fiducials with 2 mm mask opening); confirm exact current requirements. Keep all added copper/components/battery/metal fixtures outside U3 antenna keepout on **every Cu layer**, native x57.8…70.2 / y49.8…55.0 mm, extending to the board edge. No tabs/V-score/depanel stress close to U4 IMU without review. Obtain owner approval for the panel and separation method.

## 4. Separate question for Raytac / capacitor manufacturer — not a CAM approval

This section must be answered by the module/application authority or a competent independent designer; ordinary JLC CAM/BOM acceptance cannot approve it.

Configuration: MDBT50Q-P1MV2 normal-voltage mode, VDD28=VDDH30=3.0 V, DCCH31 unconnected, VBUS32=USB 4.35–5.5 V. C9 Samsung CL10A106KP8NNNC 10 µF/10 V/X5R plus C10 100 nF on +3V0. C11 CL10A475KP8NNNC 4.7 µF/10 V/X5R directly on VBUS; charger input also has C1 2.2 µF.

Does Ver.L §8.3's 10 µF specify a reference nominal or a minimum **effective** capacitance? Please give permissible effective capacitance/ESR for VDD and separately VBUS, and approve or reject the exact C9/C11 implementation. C11 is not the Nordic DECUSB capacitor. Raising C11 to 10 µF would make directly connected C1+C11 nominal 12.2 µF, initial +10% bound 13.42 µF; account for USB inrush before recommending that change. Existing direct nominal sum is 6.9 µF, not a whole-port inrush test.

Samsung: provide exact C(V,T)/bias-TCC/aging data and guaranteed versus typical limits for both MPNs. These curves have not been read at 5–5.5 V; no guaranteed Ceff is claimed. See `docs/production_caps_A1.md`.
