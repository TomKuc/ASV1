# Warunki ukończenia i zwolnienia A1

Stan: **A1 AUDIT REVIEW / NOT FOR FABRICATION**, 2026-10-29. Istnieją rzeczywisty schemat, PCB, routing i natywne raporty KiCad 10.0.7. Projekt nie jest jeszcze zwolniony do zamówienia PCBA. Odhaczenie czynności przeglądu nie zastępuje końcowej kontroli plików ani prób prototypu. Zamknięcie elektryki, DFM i zaopatrzenia pozwala osobno zwolnić prototypy; kwalifikacja właściwości urządzenia wymaga dopiero ich badań.

Końcowy [DRC](../reports/drc_final.json) po audycie, lokalnych poprawkach via/R24/USB i ponownym wypełnieniu stref: **0 naruszeń, 0 niepołączonych elementów, 0 rozbieżności schemat–PCB**. [Raport walidacji](../reports/validation_status.json) i [manifest eksportu](../manufacturing/review/export_manifest.json) identyfikują ten sam PCB hash. Wcześniejsze raporty są historią, nie bieżącym wynikiem.

## Schemat i części

- [x] Przegląd oficjalnych dokumentów podstawowych IC i pinmap: Raytac 61 pinów, IMU, Flash, ładowarka, LDO i okno temperatury.
- [x] Edytowalny projekt KiCad, pięć arkuszy funkcjonalnych i główny arkusz hierarchii; 72 symbole. Odczyt i eksport PDF wykonane przez KiCad 10.0.7.
- [x] Schemat zasilania, USB, SWD, SPI z dwoma przerwaniami, QSPI, LFXO i UI; konkretne wartości oraz MPN w roboczym BOM.
- [x] Wybrana pamięć **W25Q01JVZEIQ / C5137036, 128 MiB**, korpus 8×6 mm. Obsługa obu matryc jest wymaganiem firmware.
- [x] Sprzętowe okno NTC U7/U8/Q1/Q2; obliczenia tolerancji i warunki odbioru pakietu zapisane w raportach.
- [x] Natywny ERC: **0 błędów, 2 świadome ostrzeżenia** dla uziemionych pinów 2/3 U4 w udokumentowanym trybie głównego SPI. Ostrzeżenia pozostają widoczne.
- [x] Dobór MPN UI i pasywów; C1/C3 mają 2.2 µF/25 V, R25 1 kΩ ogranicza rozładowanie C17 przez przycisk.
- [ ] Końcowe porównanie Raytac §8.3 i zasilania USB/DCCH z aktualnym schematem oraz pojemnościami.
- [ ] Zamknięcie LFXO: land-pattern dokładnego ABS07, ESR, CL, tolerancja i obciążenie z pasożytami PCB; model biblioteczny nie stanowi CAD producenta.
- [ ] Minimalna pojemność efektywna i ESR krytycznych MLCC po DC-bias, tolerancji, temperaturze i starzeniu; pełny budżet prądu i termiki LDO/ładowarki.
- [ ] Konkretny chroniony pakiet LiPo 1S/4.2 V, preferowane 300 mAh: MPN, PCM, dopuszczalny prąd/temperatura ładowania, wymiary, wiązka i NTC fizycznie na ogniwie. JST: 1 PACK+, 2 NTC, 3 PACK−.
- [ ] Pełny cykl ładowania docelowego pakietu przy limicie wejścia BQ 100 mA i timerze 360 min typowo. Dla 500 mAh pełne ładowanie nie jest zagwarantowane. Nie przyjęto detekcji źródła ani szybkiego ładowania.
- [ ] USB: kwalifikacja **całego prądu z portu**, rozruchu/inrush i suspend. Bezpośrednia gałąź VBUS modułu omija BQ.IN; sam ILIM nie zamyka budżetu płytki. Wymagania w `firmware_contract.md`.
- [ ] Ocena ochrony CC/VBUS, mapowania zdublowanych padów, połączenia ekranu i rysunku mechanicznego aktualnej dostawy USB-C.
- [ ] Akceptacja rzeczywistego BOM przez JLCPCB, zakup/rezerwacja exact MPN i sprawdzenie zamienników. Numer C nie potwierdza dostępności ani rezerwacji.

- [x] Wszystkie wcześniej ignorowane klasy ERC/DRC włączono. Jedenaście ostrzeżeń końców ścieżek poprawiono lokalnie.
- [x] Pinmapa IMU uzgodniona: INT1=P0.11, INT2=P0.12, bez zmiany połączeń.
- [x] R24=100k zmieniono na pull-up do 3V0: HIGH/HiZ/reset inhibituje ładowanie; LOW zwalnia okno U7/U8. Brak autonomicznego ładowania bez firmware jest jawny.
- [ ] Wyjaśnienie Winbond AN0000035/statusów obu dies oraz przypięty SDK i własna warstwa Flash; testy [F01–F20](flash_firmware_test_plan_A1.md) po wykonaniu prototypów.

## PCB

- [x] Natywne PCB z **69 footprintami**, obrysem **30×51.6 mm**, czterema warstwami i roboczą grubością 1.0 mm. Roboczy CPL zawiera 59 pozycji montażowych; pozostałe footprinty to pola/przyłącza bez montażu.
- [x] Projektowe symbole i footprinty oraz dostępne modele są lokalne; opisano źródła, numerację i geometrię Raytac/IMU/Flash. Ograniczenia pozostają jawne w raportach footprintów.
- [x] Rozmieszczenie odsprzęgania i lokalne połączenia zasilania poprawione; ładowarka ma przelotki termiczne poza EP, bez zakładania procesu via-in-pad.
- [x] Keepout anteny przedłużony do krawędzi na wszystkich warstwach. Kontrola zapisanych wypełnień wykazała 0 mm² miedzi w zakazanym obszarze dla sprawdzonego snapshotu.
- [x] Wszystkie połączenia, w tym USB, ukończone. Poprawiono LFXO i odsunięto otwór przelotki od pada C3. Końcowy natywny DRC z `--schematic-parity`, po refill/save: 0 naruszeń, 0 braków, 0 rozbieżności.
- [x] Pomierzono geometrię SPI/QSPI/LFXO/USB i zapisane drogi odniesienia. Raporty `signal_geometry_review.json` oraz `return_path_review.json` opisują lokalne antypady i odległą referencję GND dla B.Cu. In1 jest GND, In2 mieszaną warstwą zasilania/sygnałów; to nie kwalifikacja SI.
- [ ] Kwalifikacja czasowa/SI QSPI/SPI i całego USB, uwzględniająca odcinki B.Cu nad mieszaną In2 oraz przejścia warstw.
- [ ] Konkretny stos 4L/1.0 mm z oferty JLCPCB i przegląd geometrii/impedancji USB dla tego stosu; obecne trasowanie nie dowodzi 90 Ω.
- [ ] Końcowa kontrola EP/pasty/maski WSON, LGA IMU, pinów wewnętrznych modułu, wyjść IMU na zewnątrz oraz niedozwolonej miedzi/vias pod sensorem.
- [x] Odstęp otwór–SMD/pasta przy U5.7 poprawiono 0.090→0.230 mm i przy J1 0.105→0.175 mm. Globalne minimum wynosi 0.150 mm; brak nominalnych przecięć.
- [ ] Akceptacja aktualnych zbliżeń, tentingu, maski i szablonu przez JLCPCB z tolerancjami procesu.
- [x] Kontrola keepout na końcowych natywnych wypełnieniach: 0 mm² Cu w zabronionym obszarze obu warstw wewnętrznych.
- [ ] Niezależny przegląd keepout na Gerberach oraz potwierdzenie baterii/metalu poza anteną.
- [ ] Dostęp USB/SWD/przycisku, przewodów i baterii; podparcie oraz brak docisku i naprężeń IMU. Obudowa i pakiet nie należą do obecnego zespołu STEP.
- [ ] Panelizacja dla JLCPCB Standard: **szyny co najmniej 5 mm**, fiducjale na szynach, zalecane 3–4 znaczniki z padem Cu 1 mm i otwarciem maski 2 mm; minimum 3.35 mm od krawędzi z uwzględnieniem obszaru keepout według rysunku wykonawcy. [Wymagania JLCPCB](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order). Szyny, mostki i ich metal nie mogą naruszyć obszaru anteny; panel i oddzielanie wymagają DFM. Nie dodano teraz ciasno rozmieszczonych fiducjali do modułu.

## Paczka do przeglądu i produkcji

- [x] Robocze BOM i CPL istnieją w `reports/assembly_review/`; nie zatwierdzono rotacji JLC ani zamówienia montażu.
- [x] Natywny STEP płytki i render KiCad istnieją w `reports/`. Ograniczenia: **brak USB-C**, model Raytac jest ogólny, Flash ma jawny model gabarytowy, a IMU w CAD ma 0.80 mm zamiast maksymalnych 0.86 mm ST.
- [ ] Modele/rysunki i maksymalne gabaryty umożliwiające zamknięcie obudowy; uzupełnienie USB-C i potwierdzenie wariantu Raytac. Obecny STEP służy przeglądowi.
- [x] Rzeczywiste 11 Gerberów i Excellon PTH/NPTH z końcowego PCB, po 0 DRC/opens; wspólny aux origin **(50,101.6) mm**. Porównano obrys, 59 pozycji, 164 otworów via, 4 sloty PTH i 2 NPTH z natywnym PCB (`manufacturing_geometry_review.json`).
- [ ] Niezależny przegląd CAM całej miedzi/maski/pasty i drill-map. Gerber Job ma ogólny stos KiCad, nie wybrany stos JLCPCB.
- [ ] Finalne BOM/PnP z exact MPN, numerami C, warstwą, jednostkami, wspólnym origin i rotacją sprawdzoną w JLCPCB. Zweryfikować osobny zespół baterii.
- [x] Raporty ERC/DRC, RF, dróg powrotnych i eksportu zidentyfikowane hashami końcowego PCB; świadome wyjątki ERC i nierozwiązane ograniczenia opisane.
- [x] Globalny audyt otworów 164 przelotek względem 255 padów SMD Cu i 243 apertur pasty: brak przecięć po poprawce C3.
- [ ] DFM marginesu otwór–pad/pasta: minimum geometryczne 0.150 mm; uwzględnić tolerancję wiercenia, maski i pasty. Audyt nominalny nie kwalifikuje procesu.
- [ ] Akceptacja DFM, footprintów, pasty, polaryzacji, rotacji i zaopatrzenia w podglądzie JLCPCB; dopiero potem świadome zwolnienie prototypów do zamówienia.

## Weryfikacja fizyczna

Próby z `firmware_contract.md` i `power_review.md` obejmują zasilanie i termikę pakietu, NTC i brownout, cały budżet USB/suspend/inrush, zapis po odcięciach, obie matryce Flash, przepustowość, synchronizację i niepewność czasu dwóch nóg, szum/filtrację/saturację IMU oraz wpływ obudowy i naprężeń. Firmware nie został zaimplementowany ani uruchomiony. Natywny ERC/DRC nie zastępuje tych prób.
