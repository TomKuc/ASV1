# Przegląd modeli i rozmieszczenia mechanicznego

Data: 2026-10-28. Odczytano aktualną płytkę KiCad, bez jej edytowania podczas routingu. Ślad kontroli i SHA256 analizowanego pliku: `reports/mechanical_placement_review.json`. Ten przegląd dotyczy geometrii nominalnej projektu; obudowy, baterii, śrub, przewodów i wtyczki USB nie ma w zespole.

## Pamięć U5 — jawny model gabarytowy

Nie znaleziono zgodnego modelu WSON8 8×6mm w zainstalowanej bibliotece KiCad. Dostępny WSON6×5mm ma inny obrys, dlatego nie został podstawiony.

Przygotowano `hardware/3dmodels/W25Q01JVZEIQ_ENVELOPE_MAX.step`: **prostokątny model maksymalnego gabarytu8.10×6.10×0.80mm**. Źródło: [dokument Winbond W25Q01JV RevE,2024-03-04, strona81, packageZE](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf): Dmax8.10,Emax6.10,Amax0.80mm. Wysokość1.20mm z sąsiedniej tabeli dotyczy BGA/TB, więc nie zastosowano jej doZE.

To **model ENVELOPE, nie CAD producenta**. Nie zawiera wyprowadzeń, EP, fazowań ani oznaczenia pinu1. Jest przeznaczony do rezerwacji miejsca i kontroli obudowy; należy dodać zapas montażowy na lutowanie i tolerancję położenia.

Geometrię utworzył natywny eksporter STEP KiCad/OCCT z tymczasowego pliku konstrukcyjnego. Sprawdzono obecność bryły BRep i zakresy współrzędnych:

| Oś | Minimum [mm] | Maksimum [mm] |
|---|---:|---:|
|X|-4.05|4.05|
|Y|-3.05|3.05|
|Z|0.00|0.80|

Model jest wycentrowany wXY i znajduje się **powyżej poziomuTOP** przy offset0,scale1,rotation0. Zalecany wpis dla footprintu jest w `reports/model_envelope_entry.sexpr`. Manifest źródeł, skrót modelu i ograniczenia: `hardware/geometry_sources/model_envelopes.json`. Odtwarzanie: `scripts/generate_model_envelopes.py` przez Python KiCad. Autor głównegoPCB wdrożył przypisanie; podczas ponownego odczytu modelU5 jest lokalny i istnieje. W przeglądzie nie edytowanoPCB.

## USB J1 — model pozostaje brakujący

Dokładny model HRO TYPE-C-31-M-12 nie występuje w lokalnej bibliotece. [Oficjalna strona HRO](https://en.krhro.com/Product-Details/726.html) podaje **nominalne8.94×7.35×3.16mm**, lecz nie uzyskano wiarygodnie odczytanych maksymalnych wymiarów, tolerancji i bazy montażowej z rysunku. Nie zastosowano modelu innego złącza ani nie wygenerowano bryły podszywającej się pod model producenta.

Końcowy STEP płytki powinien jawnie wymieniać ten brak. Wycięcie obudowy i przestrzeń dla wtyczki wymagają rysunku/modelu HRO albo pomiaru rzeczywistego egzemplarza. ObrysFAB na obecnymPCB wystaje około1.05mm poza krawędźy=101.6mm; jest to wystawienie portu, które trzeba uwzględnić w obudowie.

## U3 — model biblioteczny nie jest dokładnym CAD wariantuP1MV2

Obejrzano `reports/Ankle_Sensor_V1_A1_3d_review.png` i sprawdzono nazwy w natywnym `reports/Ankle_Sensor_V1_A1_mechanical_review.step`. InstancjaU3 wskazuje PRODUCT`Raytac_MDBT50Q`; wewnątrzSTEP nie ma deklaracji modeluP1MV2 ani1MV2.

Na renderze widać osobny blok antenowy przypominający antenę typu chip. To **wniosek z wyglądu modelu**, nie zweryfikowana adnotacja jego autora. Wybrany [MDBT50Q-P1MV2 producent opisuje jako PCBantenna,10.5×15.5×2.0mm](https://www.raytac.com/product/ins.php?index_id=47). BibliotecznySTEP ma obrys10.5×15.5mm i zakresZ0…2.06mm. Zgodność podstawy nie potwierdza dokładnej anteny ani maksymalnego gabarytu wariantuP1 z tolerancjami.

ModelU3 należy oznaczać **generic KiCad, przybliżony dla wybranegoP1MV2**, nie jako CAD producenta tej części. Służy orientacyjnej rezerwacji miejsca. GeometrięRF wyznacza dokumentacja i keepoutPCB, nie widoczny bloczek3D. Potrzebny jest właściwy model RaytacP1MV2 lub pomiar części przed zamknięciem mechaniki obudowy. Informację dopisano do manifestu `imu_rf_geometry.json`; nie zmieniono symbolu, BOM aniPCB.

## IMU i nominalne kolizje

Natywny KiCad odczytał pozycje i przetestował przecinanie wielokątów courtyard dla montowanych elementów po tej samej stronie: **zero przecinających się par**. Nie jest to test przecięcia pełnych bryłSTEP.

| Element względemIMU | Odległość środków [mm] | Minimalny odstęp prostokątówFAB ze stroke [mm] |
|---|---:|---:|
|SW1|21.86|16.20|
|USB J1|23.95|17.63|
|Bateria J2|14.71|10.65|
|Ładowarka U1|17.27|14.09|
|LDO U2|15.89|12.65|

Przycisk i USB są dalej niż zalecane10mm od sensora. Należy nadal sprawdzić naprężenia po zamontowaniu baterii i obudowy; brak tych części nie pozwala zatwierdzić pełnego zespołu mechanicznego. Dla modeluIMU biblioteczne0.8mm nie zastępuje limitu0.86mm ST.

## Obowiązkowe przedłużenie keepout anteny

Przy U3=(64,59) biblioteczna strefa anteny zajmuje x=57.8…70.2mm,y=51.25…55.0mm, podczas gdy górna krawędźPCB ma y=50.0mm. Same biblioteczne granice zostawiają obszar płytki przed anteną, do którego mogłyby wejść wylewki.

**Wymagany board-level keepout na wszystkich warstwach miedzi: x=57.8…70.2mm,y=49.8…55.0mm — został wdrożony i sprawdzony na aktualnymPCB.** Blokuje wylewki, ścieżki, vias i pady naF.Cu/B.Cu/In1.Cu/In2.Cu oraz dochodzi poza krawędźPCB. Zwykła soldermaska nie jest metalem i nie wymaga wycięcia w tej strefie.

`scripts/verify_rf_filled_copper.py` sprawdził **rzeczywiście zapisane wypełnienia**, z otworami, przez natywne przecięcie wielokątów. DlaIn1/GND iIn2/+3V0 pole miedzi przecinające całykeepout oraz pasek przed anteną wynosi **0.0mm²**. Dodatkowe35punktów na każdej warstwie nie trafiło w miedź. Kontrola dodatnia poza keepout daje23.993mm²Cu na każdej warstwie, więc wynik nie pochodzi z pustych danych. Wyniki i skrót analizowanegoPCB: `reports/rf_filled_copper_review.json`.

Ostateczny przegląd musi powtórzyć tę kontrolę po ukończeniu routingu i ostatnimrefill oraz sprawdzić plikiGerber. W końcowym A1 wszystkie połączenia są poprowadzone, a kontrolę zapisanych wypełnień powtórzono na końcowym PCB; hashe są w aktualnych raportach. Wynik nie jest kwalifikacją RF ani zwolnieniem do produkcji. Bateria i metalowe części obudowy również muszą pozostawać poza anteną. Kontrola elektrycznej geometriiRF nie zastępuje prób zasięgu na nodze.
