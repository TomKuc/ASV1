# A1 — warunki zamówienia prototypów

Stan: **CONDITIONAL READY**, 29.10.2026. Obowiązuje [raport warunków produkcyjnych](production_readiness_A1.md) i [manifest bieżących plików](../reports/current_A1_manifest.json). Dawne raporty bazowe i paczki A0/A1/AUDIT/FINAL zachowano jako historię.

## A — zamknąć przed zamówieniem 3–5 PCBA

- [ ] **A01 — EXTERNAL CONFIRMATION:** C9 nominalnie poprawiony na10µF, ten sam0603; Raytac C11/Ceff VDD/VBUS i dokładne rysunki U3/J1/Y1 do zatwierdzenia. Nie stosować limitu DECUSB do VBUS. [Kondensatory](production_caps_A1.md), [footprinty](production_footprints_A1.md).
- [ ] **A02 — EXTERNAL CONFIRMATION:** JLC aktualny JLC7628 4L/1mm, pressed stack/Dk/Cu/tolerancje i USB0.17/0.13. Model nominalny94.139/87.162Ω jawnie ponownie użyty na identycznej geometrii; nie gwarantuje całego USB. [USB](production_usb_A1.md).
- [ ] **A03 — EXTERNAL CONFIRMATION:** wszystkie33grupy/59TOP zakupione i dopasowane exactMPN, szczególnie U7/R1/R20; preview rotacji/pin1, Standard i X-ray U3/U4. [Pełna tabela](../reports/production_component_status_A1.csv).
- [ ] **A04 — EXTERNAL CONFIRMATION:** trzy minima U6.2/C4.2/C5.2 otwór→pad/pasta0.150001mm, annulus→otwarcie0.025mm; JLC CAM/tenting/tolerancje/stencil/kotwy/panel/fiducjale. [Opis do producenta](JLCPCB_A1_confirmation_request.md).

Można rozpocząć wycenę/import/DFM; przed zwolnieniem wykonania zapisać odpowiedzi i akceptację właściciela. Żadnej korespondencji ani zamówienia nie wysłano.

## Kontrole wykonane na obecnej A1

- [x] W tym etapie tylko C9 nominalnie4.7→10µF. 1822obiekty Cu,69footprintów oraz wypełnienia/warstwy/pozycje/pady identyczne z poprzednią A1; dowód strukturalny zapisany. Poprzednia szerokość USB0.17mm zachowana.
- [x] Natywne KiCad10.0.7: ERC0errors/2 widoczne uzasadnione ostrzeżenia U4.2/3; DRC0 naruszeń/ostrzeżeń,0opens,0schematic-parity. Brak ignorowanych klas.
- [x] Jawna reguła USB minclearance/diffgap0.125mm, optimumgap0.13mm; poza parą pozostaje0.15mm. Plik.kicad_dru jest częścią źródeł i paczki.
- [x] Spójne BOM/CPL/PCB:59 pozycji TOP,33 grupy,69 footprintów; SWD i9TP nie są brakującymi częściami do montażu.
- [x] Ponowny audyt164vias/255CuSMD/243paste:0 nominalnych przecięć, minimum0.150001mm. Antena:0mm² Cu w zadeklarowanym keepout.
- [x] Po zmianie źródła odświeżono rzeczywiste Gerbery/Drill/BOM/CPL/PDF/STEP/render; współrzędne59CPL,164vias,4sloty PTH,2NPTH porównano z PCB.
- [x] Stan HiZ ładowarki sprawdzony z netlistą; nie odwrócono ponownie R24. Udokumentowano hang LOW, System OFF, USB boot bez baterii i PCM-open.

## B — próby po otrzymaniu prototypów

- [ ] Pierwsze zasilanie ograniczonym bench supply, symulatorem baterii/NTC, bez niezamierzonego USB/SWD backpower. Start bez baterii, przy niskim VBAT i PCM-open; rampy, CE, inrush i cały prąd USB.
- [ ] Firmware inhibit przy boot, przed System OFF, po awarii/WDT; brak pętli restartów CE/timera. Suspend/resume i źródło USB zgodnie z przyznanym budżetem.
- [ ] Przed ładowaniem rzeczywistego pakietu: jego MPN/PCM/recovery/NTC odniesiony do PACK−, wiązka i polaryzacja; progi/rampy, open/short/factory recovery, pełny cykl i termika. Brak baterii w BOM nie blokuje wykonania samej PCBA.
- [ ] F01–F20 Flash128MiB: wszystkie NOT_RUN; oba dies,32-bit,16/32/64/128MiB, BUSY/WEL, CRC, reset/DPD/power-cut. Przypięty SDK i kontrakt AN0000035 do kwalifikacji firmware.
- [ ] Cały USB: funkcjonalny transfer, eye/ESD; ripple/zasilanie/Ceff/termika; IMU ODR/FS/FIFO/szum/temperatura/luki; BLE i synchronizacja obu nóg.
- [ ] Obudowa i bateria poza anteną, podparcie PCB bez docisku IMU, naprężenia/reflow/kalibracja. Niekompletny STEP nie stanowi finalnej geometrii obudowy.

## C — dalsza rewizja

Optymalizacja138µA przy zachowaniu ochrony, mniejszy obrys, ergonomia, dedykowane QSPI TP/odłączany rail i ewentualny termiczny odczyt ogniwa przez MCU lub niezależny heartbeat. Nie są samodzielnymi blockerami tej partii prototypowej.

Nie wykonano testów fizycznych. Nie złożono zamówienia. Po zamknięciu A01–A04 decyzję i zlecenie podejmuje użytkownik; B pozostaje planem uruchomienia.
