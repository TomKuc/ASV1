# A1 — warunki zamówienia prototypów

Stan: **CONDITIONAL READY**, 29.10.2026. Obowiązuje [raport końcowy](final_verification_A1.md) i [manifest bieżących plików](../reports/current_A1_manifest.json). Dawne raporty bazowe i paczki A0/A1/AUDIT zachowano jako historię.

## A — zamknąć przed zamówieniem 3–5 PCBA

- [ ] **A01 — rysunki producentów:** literalne porównanie Raytac VerL§8.3 i kondensatorów/zasilania; akceptacja wymiarowanych rysunków footprintów Raytac, USB-C J1 i ABS07 Y1 wskazanych w przeglądzie PCBA. Brak bitmap w narzędziach nie oznacza wykonanego przeglądu.
- [ ] **A02 — laminacja i USB:** JLC potwierdza wybrany JLC7628 4L/1.0mm, Dk/Cu/grubości oraz geometrię0.17/0.13mm. Własny model nominalny94.14/87.16Ω dotyczy przekrojów trunku, nie pełnego toru/padów/vias/ESD. Nie zamawiać na podstawie ogólnego Gerber Job KiCad; znajduje się w reference/, poza ZIP do uploadu.
- [ ] **A03 — Standard PCBA:** wszystkie33 grupy/59TOP zaakceptowane w BOM/CPL, szczególnie U7 C2760466, R1 C25769 i R20 C852679; exact MPN, procurement, rotacje/pin1 i przesunięcia zatwierdzone. X-ray U3 Raytac i U4 IMU; IMU Standard Only.
- [ ] **A04 — CAM/DFM:** maska/pasta LGA/WSON, tenting i nominalne minimum otwór→Cu/pasta0.150mm, panel/szyny/fiducjale oraz oddzielenie bez naruszenia RF i naprężeń IMU. Akceptacja pliku w formularzu nie jest tym przeglądem.

## Kontrole wykonane na obecnej A1

- [x] Routing zachowany. Tylko18 szerokości USB In2 zmieniono0.15→0.17mm; centra, warstwy, UUID, nety, vias, footprinty i pady bez zmian względem poprzedniej A1.
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
