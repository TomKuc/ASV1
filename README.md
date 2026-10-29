# Ankle Sensor V1 — A1 warunki produkcyjne A01–A04

**CONDITIONAL READY dla3–5 prototypów JLCPCB.** Można rozpocząć wycenę/import i przegląd JLCPCB. Zwolnienie wykonania wymaga zamknięcia warunków A01–A04 z [raportu gotowości](docs/production_readiness_A1.md). Nie złożono zamówienia i nie wykonano testów sprzętowych. Nie ma jeszcze uruchomionego firmware.

Jedyna aktualna wersja: [manifest A1](reports/current_A1_manifest.json). PCB SHA256: `1d3bb700a2b686ef68589bf3295488d2144a1d51a857cec7651e45be175a6134`. Aktualna paczka: **Ankle_Sensor_V1_A1_PRODUCTION_REVIEW.zip**. Dawne ZIP A0/A1/AUDIT/FINAL i raporty bazowe są historią.

## Co otwierać

- [Projekt KiCad](hardware/Ankle_Sensor_V1.kicad_pro), [schemat](hardware/Ankle_Sensor_V1.kicad_sch), [poprowadzone PCB](hardware/Ankle_Sensor_V1.kicad_pcb). Obok musi pozostać [plik reguł](hardware/Ankle_Sensor_V1.kicad_dru); zawiera uzasadnioną regułę tylko dla pary USB.
- [PDF schematu](reports/Ankle_Sensor_V1_A1_schematic.pdf), [STEP do przeglądu](reports/Ankle_Sensor_V1_A1_mechanical_review.step), [render KiCad](reports/Ankle_Sensor_V1_A1_3d_review.png), [przewodnik dla początkujących](reports/guide/ankle_sensor_przewodnik.html).
- [BOM](manufacturing/review/assembly/BOM_REVIEW_NOT_RELEASED.csv), [CPL/Pick and Place](manufacturing/review/assembly/CPL_REVIEW_ROTATIONS_UNCONFIRMED.csv), [Gerber/Drill](manufacturing/review/Ankle_Sensor_V1_A1_GERBERS_DRILL_REVIEW.zip), [manifest eksportu](manufacturing/review/export_manifest.json).
- [Warunki zamówienia A/B/C](docs/release_checklist.md), [wybrany profil JLCPCB](hardware/manufacturing_profile_A1.json), [tabela stanów ładowania](docs/charge_startup_final_A1.md), [USB i obliczenia](docs/production_usb_A1.md), [PCBA i DFM](docs/production_pcba_dfm_A1.md).

## Stan projektu

69 footprintów,59 części montowanych na TOP,4 warstwy, obrys30×51.6mm, nominalnie1.0mm. Pamięć **W25Q01JVZEIQ128MiB** pozostaje; nie zmieniono architektury. INT1=P0.11, INT2=P0.12. Zachowano centra wszystkich ścieżek, via i części. W tym etapie zmieniono tylko C9 na 10 µF / CL10A106KP8NNNC / C19702 w tym samym 0603. Pełna geometria PCB jest identyczna z poprzednim etapem; USB pozostaje 0.17/0.13 mm.

Wybrany profil do potwierdzenia zamówienia to **JLC7628 4L/1.0mm, outer1oz/inner0.5oz, zielona maska/ENIG**. Model2D trunku daje około94Ω względem In1 i87Ω przy idealnym warunkowym odniesieniu pobliskiej3V0. Nie jest to kwalifikacja całego toru ani fizyczny test USB. Ogólny plik Gerber Job KiCad jest oddzielnym plikiem referencyjnym, wyłączonym z ZIP do uploadu.

Natywne KiCad10.0.7: **ERC0 błędów/2 uzasadnione ostrzeżenia IMU; DRC0 naruszeń,0opens,0rozbieżności schemat–PCB, brak ignorowanych klas**. [Wyniki i hashe wejść](reports/validation_status.json). Sprawdzono współrzędne59 CPL,164vias,4sloty PTH i2NPTH względem PCB. Nie zatwierdzono jeszcze podglądu rotacji/MPN/panelu w JLCPCB.

R24 jest pull-up: HIGH/HiZ blokuje ładowanie; LOW zwalnia je tylko za zgodą sprzętowego okna. Hang LOW i System OFF wymagają jawnej obsługi firmware. **Bez działającego firmware bateria nie ładuje się**, ale USB może zasilać SYS i umożliwić programowanie przez SWD. Pakiet/wiązka/NTC są oddzielnym zespołem i wymagają kwalifikacji przed prawdziwym ładowaniem.

A01–A04: **EXTERNAL CONFIRMATION**. C11/Ceff i dokładne landy U3/J1/Y1 do akceptacji; aktualny stack, procurement/rotacje oraz CAM/DFM do JLC. [Gotowe pytania do producentów](docs/JLCPCB_A1_confirmation_request.md), [59 części i 3 pozycje zewnętrzne](reports/production_component_status_A1.csv). Testy Flash/IMU/BLE/USB/termiki wykonuje się po otrzymaniu prototypów. Zachowano [20 prób Flash, wszystkie NOT_RUN](docs/flash_firmware_test_plan_A1.md).

STEP jest niekompletny: brak USB-C, ogólny Raytac, gabaryt Flash i ograniczenie wysokości IMU. Bateria/obudowa nie są w modelu. [Ograniczenia mechaniczne](docs/mechanical_model_review.md).

## Historia i GitHub

`b5487d09…` to A1 sprzed audytu; `38545441…` po audycie; `cdcbd234…` poprzednia korekta USB; `1d3bb700…` obecna korekta nominału C9. [Pochodzenie i zachowane paczki](reports/production_provenance_A1.json).

Bazowy lokalny commit: b17f145. Nie potwierdzono ce616878 ani aktualnej rewizji na GitHubie; nie wykonano push. Nowy commit i bundle opisuje `reports/production_commit_delivery_A1.json`, dostarczany po utworzeniu commita. [Import i weryfikacja serwera](docs/github_delivery_production_A1.md).

Natywne pliki `hardware/` są źródłem projektu. `build_pcb.py --replace` usuwa routing, a `build_design.py` nadpisuje schematy — nie uruchamiać ich na tej A1 bez zabezpieczonej kopii. `sh scripts/kicad_cli.sh` izoluje cache KiCad w `.work`. Przegląd, obliczenia i eksporty nie zastępują testów prototypu ani akceptacji zamówienia.
