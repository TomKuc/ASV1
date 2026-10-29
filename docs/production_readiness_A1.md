# Ankle Sensor V1 A1 — zamknięcie warunków produkcyjnych A01–A04

**Decyzja: CONDITIONAL READY dla 3–5 prototypów, 29.10.2026.** Można rozpocząć wycenę, import BOM/CPL i przegląd inżynierski JLCPCB. Przed zwolnieniem do wykonania trzeba uzyskać odpowiedzi opisane poniżej. Nie wykazano nowego błędu wymagającego reroutingu; nie uzyskano akceptacji fabryki ani pełnego potwierdzenia kondensatorów/rysunków modułu. Nie złożono zamówienia i nie wykonano testów sprzętowych.

To wąskie domknięcie poprzedniego raportu, bez ponownego pełnego audytu. Źródłem jest `hardware/`; pamięć **W25Q01JVZEIQ 128 MiB**, architektura i routing pozostają. Bazowy commit lokalny: `b17f1457de876ecb27e94dc514c9a4844be44bc0`. Aktualny PCB SHA256: **`1d3bb700a2b686ef68589bf3295488d2144a1d51a857cec7651e45be175a6134`**.

## Wynik A01–A04

| Warunek | Status całego warunku | Co zamknięto | Co musi jeszcze zostać zaakceptowane |
|---|---|---|---|
| **A01 — kondensatory i footprinty** | **EXTERNAL CONFIRMATION** | **CLOSED:** C9 zmieniony nominalnie na 10 µF, dokładny MPN i ten sam 0603; natywny odczyt wartości/netów i padów U3/J1/Y1; zgodność ich instancji z lokalnymi bibliotekami; aktualna miedź poza keepout anteny. | Raytac: dopuszczalny Ceff VDD i VBUS oraz C11=4,7 µF w tej aplikacji. Dane bias/T dla dokładnych MLCC. Czytelne rysunki/CAD dokładnych U3/J1/Y1 i akceptacja padów, otworów, pin1 i krawędzi PCB. |
| **A02 — USB i stackup** | **EXTERNAL CONFIRMATION** | **CLOSED:** publiczna oferta nominalnego JLC7628 4L/1,0 mm; bieżące szerokości/nety/via i odniesienie GND; identyczna geometria pozwala użyć poprzednich obliczeń bez nowego solvera. Nie ma uzasadnienia do kolejnego reroutingu. | JLC: aktualny szablon zamówienia, pressed stack, Dk/Cu/tolerancje i akceptacja rzeczywistego toru. Około 94 Ω nie jest gwarancją fabryczną całego USB. |
| **A03 — BOM/CPL i komponenty** | **EXTERNAL CONFIRMATION** | **CLOSED:** 59 części TOP, 33 grupy dokładnych MPN; spójność wartości/MPN/C, referencji, współrzędnych i natywnych rotacji. Pełna tabela każdej pozycji. | JLC: zakup wszystkich dokładnych części, szczególnie U7/R1/R20, Standard PCBA, podgląd translacji/rotacji/pin1 i X-ray U3/U4. Brak dostępu do zamówienia nie jest potwierdzonym stanem magazynu. |
| **A04 — CAM/DFM** | **EXTERNAL CONFIRMATION** | **CLOSED:** pliki Gerber/Drill, obrys, CPL i otwory zgodne z PCB; rzeczywiste otwarcia maski/pasty trzech minimów sprawdzone; nominalnie brak przecięcia otworu z padem/pastą. | JLC: tolerancje wiercenia/registration i tenting, stencil LGA/WSON, lutowanie kotew J1, panel/szyny/fiducjale i oddzielanie bez naruszenia RF/IMU. |

Żaden cały warunek A01–A04 nie otrzymał sztucznego `CLOSED`. `EXTERNAL CONFIRMATION` oznacza brak wskazanego dowodu lub akceptacji procesu; **nie oznacza wykrytego i zignorowanego błędu elektrycznego**. W tym etapie nie ma potwierdzonej usterki oznaczonej `BLOCKED`. Jeżeli dostawca odrzuci land, C11 lub geometrię, odpowiedni warunek staje się `BLOCKED` do uzasadnionej lokalnej poprawki.

## A01 — minimalna poprawka i granica dowodu

**C9:** `4.7u 10V X5R / CL10A475KP8NNNC / C1705` zastąpiono `10u 10V X5R / CL10A106KP8NNNC / C19702`. Nominał odpowiada 10 µF wskazanemu przez użytkownika w Raytac Ver.L §8.3; ten sam MPN jest już na C2/C5. Samsung potwierdza 0603 i gabaryty, zatem nie zmieniono footprintu. Zaktualizowano schemat, PCB, design/choices i BOM. To korekta rozbieżności nominalnej, **nie dowód, że wcześniejsze 4,7 µF powodowało awarie ani gwarancja 10 µF efektywnie**. [Oficjalna specyfikacja Samsung](https://product.samsungsem.com/mlcc/CL10A106KP8NNN.do).

**C11 pozostaje 4,7 µF.** C1+C11 na VBUS wynoszą nominalnie 6,9 µF, do 7,59 µF przy początkowej tolerancji +10% obu. Zmiana C11 na 10 µF dałaby 12,2 µF, do 13,42 µF, przed uwzględnieniem reszty portu. Nie można jej automatycznie zalecić przy wymaganiach USB inrush. Spadek C przy końcowych 5 V nie zastępuje całki ładunku podczas załączania. [TI SLVA129](https://www.ti.com/lit/pdf/slva129).

Dla dokładnego nowego C9 TI podaje punkt **5,2 µF przy 3,3 V**; nie jest to gwarantowane minimum dla 3,0 V i całej temperatury. Nie odczytano krzywej C11 przy 5–5,5 V. Nie podano fikcyjnego deratingu. Limit Nordic C_DECUSB 2,35/4,7/5,5 µF dotyczy **DECUSB, nie C11 na VBUS**. [TI LM3281, tabela 6](https://www.ti.com/lit/ds/symlink/lm3281.pdf), [Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html).

Nie uzyskano czytelnej bitmapy całego rysunku Raytac §8.3 ani jednoznacznego wymiarowania wszystkich landów U3/J1/Y1. Odnalezienie PDF i zgodność z biblioteką nie zastępują tego sprawdzenia. Szczególnie Y1 wymaga dokładnego **ABS07, bez LR**: obecne pady 1,00×1,80 mm / rozstaw 2,50 mm nie zostały zmienione na podstawie niepewnego odczytu. J1 wymaga akceptacji slotów/NPTH, PCB EDGE i procesu lutowania kotew bez pasty. [Raytac](https://www.raytac.com/download/index.php?index_id=43), [HRO C165948 — rysunek producenta](https://datasheet.lcsc.com/lcsc/1903211732_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf), [Abracon ABS07](https://abracon.com/Resonators/ABS07.pdf).

Pełne uzasadnienie i pytania: [kondensatory](production_caps_A1.md), [footprinty i odczyt padów](production_footprints_A1.md). **JLC CAM nie może zatwierdzić wymaganego przez Raytac Ceff**; to oddzielna odpowiedź producenta modułu lub kompetentnego niezależnego projektanta na podstawie pełnego rysunku i danych MLCC.

## A02 — pozostawione USB

Wybrano JLC7628 4L/1,0 mm, outer 1 oz / inner 0,5 oz. Publiczna tabela podaje Cu 0,035/0,0152/0,0152/0,035 mm, prepreg 0,2104 mm po obu stronach i core 0,400 mm: suma 1,0212 mm bez maski. Starszy opis ma dodatkowo core-with-Cu 0,45 mm i Dk prepreg 4,6, bieżąca strona parametrów Dk 4,4. Definicje i obowiązujący szablon musi podać fabryka. [JLC — opublikowane stackupy](https://cart.jlcpcb.com/client/template/placeOrder/impedance.html), [bieżący kalkulator](https://jlcpcb.com/impedance).

Aktualny trunk USB na In2 ma szerokość 0,17 mm, gap 0,13 mm. Zachowano poprzedni nominalny model 2D **94,139 Ω** względem In1 GND oraz **87,162 Ω** przy idealnym warunkowym odniesieniu pobliskiej +3V0. Obliczenia wykonano na PCB `cdcbd234…`; pełny [dowód identyczności geometrii](../reports/production_geometry_equivalence_A1.json) i świeży odczyt bieżącego PCB uzasadniają ponowne użycie wyników. **Nie wykonywano nowej symulacji i nie przedstawia się tych liczb jako pomiaru ani tolerancji całego toru.**

Tor ma też rozdzielone końcówki 0,15 mm, po cztery via na cały net, odgałęzienia USB-C i pady ESD. Natywny przegląd odniesienia nie wykazał nowej przerwy wymagającej reroutingu; przejścia i miejscowe prądy powrotne pozostają nieciągłościami do pomiaru pełnego USB Full Speed. Nie dodano zewnętrznych 27 Ω: poprzednie uzasadnienie wewnętrznej terminacji PHY pozostaje. [Bieżący raport USB i pytania produkcyjne](production_usb_A1.md).

## A03 — co faktycznie wiadomo o montażu

[Tabela komponentów](../reports/production_component_status_A1.csv) obejmuje **każdą z 59 referencji** oraz oddzielnie elementy zewnętrzne do ręcznego złożenia. Status części montowanych to „wymaga potwierdzenia”; kolumna publicznego katalogu wskazuje dopasowanie MPN/C i usługę, a nie rezerwację magazynu. Nie ogłoszono części niedostępnymi wyłącznie dlatego, że narzędzie nie odczytało karty.

| Szczególna grupa | Dokładny wariant | Pozostały warunek |
|---|---|---|
| U7 | TLV7042DGKR / C2760466, VSSOP-8 | Dokładne dopasowanie i procurement w zamówieniu |
| R1 | 0402WGF2402TCE / C25769, 24 kΩ 1%, 0402 | Jak wyżej; nie zamieniać na przypadkowy nominał/tolerancję |
| R20 | RT0402BRD0727K4L / C852679, 27,4 kΩ 0,1%, 0402 | Zachować dokładność sprzętowego progu temperatury |

Nie zatwierdzono konwencji taśmy/rotacji JLC. CPL jest poprawnym eksportem natywnych początków i kątów, a pin1/polaryzację trzeba przyjąć na podglądzie dostawcy. J2 jest montowane; J3 i TP1–TP9 to miedź. Chroniony akumulator, związany z nim NTC i wiązka są poza PCBA. X-ray U3/U4 i Standard PCBA pozostają warunkami procesu. [Szczegóły BOM i DFM](production_pcba_dfm_A1.md).

## A04 — dokładne miejsca do CAM

| Pad sąsiadujący | Via X/Y w PCB [mm] | Otwór→pad/pasta nominalnie | Annulus→otwarcie maski nominalnie |
|---|---|---:|---:|
| U6.2 | 71,400 / 93,300 | 0,150001 mm | około 0,025 mm |
| C4.2 | 69,150 / 78,300 | 0,150001 mm | około 0,025 mm |
| C5.2 | 71,450 / 78,300 | 0,150001 mm | około 0,025 mm |

W każdym miejscu drill Ø0,25 / Cu Ø0,50 mm, ten sam net GND, via tented z obu stron. To nie jest deklaracja 0,025 mm mostka pomiędzy dwoma oknami maski. Natywny odczyt i literalne Gerbery potwierdzają nominalny brak przecięcia otworu. Nie dowodzi to zachowania maski po tolerancjach. JLC publikuje, że via nie mają określonej tolerancji rozmiaru otworu; nie podstawiono tolerancji otworów komponentów PTH. [JLC — via covering](https://jlcpcb.com/help/article/pcb-via-covering).

Nie wykonano lokalnej zmiany via bez decyzji CAM. WSON/LGA mają otwarcia pasty w rzeczywistym eksporcie; proces stencil, ukryte połączenia, reflow/MSL, kotwy USB i ewentualny panel wymagają przyjęcia. Na płytce nie dodano globalnych fiducjali/szyn; ich konieczność i panel wykonawcy trzeba ustalić. Dodana miedź/panel nie mogą naruszyć keepoutu anteny, a depanelizacja nie powinna obciążać IMU. Konkretny opis, współrzędne obu układów odniesienia i pytania są w [gotowym szkicu do producenta](JLCPCB_A1_confirmation_request.md). Szkicu nie wysłano.

## Kontrole i jedna aktualna paczka

- Natywny **KiCad 10.0.7: ERC 0 błędów / 2 widoczne ostrzeżenia U4.2/U4.3**, celowe GND w wybranym trybie IMU, bez Qvar/sensor hub. **DRC 0 naruszeń, 0 opens, 0 rozbieżności schemat–PCB; brak ignorowanych klas.** Reguła USB pozostaje jawna w `.kicad_dru`. [Raport i hashe wejść](../reports/validation_status.json).
- Po C9 ponownie wyeksportowano schemat/netlistę, BOM, CPL, Gerber/Drill oraz PDF/STEP/render. Porównano 59 pozycji, 164 otwory via, 4 sloty PTH i 2 NPTH z PCB; [kontrola geometrii eksportu](../reports/manufacturing_geometry_review.json). Te kontrole nie są niezależnym zatwierdzeniem CAM.
- Dowód porównania pełnych struktur KiCad obejmuje **1822 obiekty Cu i 69 footprintów**: jedyna zmiana PCB to cztery pola tekstowe C9 (Value/MPN/JLCPCB/Note). Netlista, geometria padów, pozycje, ścieżki, via, warstwy i zapisane wypełnienia są identyczne. [Dowód](../reports/production_geometry_equivalence_A1.json).
- Źródła przed zmianą zabezpieczono w `reports/baselines/A1_before_production_closure_2026-10-29.zip`; dawne A0/A1/AUDIT/FINAL ZIP zachowano. Starsze raporty utrzymują prawdziwe hashe obliczeń, a aktualną stosowalność wskazują nowe raporty i dowód geometrii. Stary hash nie oznacza ponownego obliczenia na nowej wersji.

**Jedyny aktualny pełny pakiet:** `Ankle_Sensor_V1_A1_PRODUCTION_REVIEW.zip`. W środku edytowalne `hardware/`, lokalne biblioteki/reguły, raporty, dokumentacja i `manufacturing/review/`. Do importu CAM służy osobny `manufacturing/review/Ankle_Sensor_V1_A1_GERBERS_DRILL_REVIEW.zip`, a BOM/CPL są w `manufacturing/review/assembly/`. Ogólny Gerber Job jest tylko w `reference/`, poza ZIP do uploadu. [Manifest aktualnych plików](../reports/current_A1_manifest.json), `reports/package_integrity.json` dostarczany obok ZIP (poza jego wnętrzem, aby uniknąć samoodwołania), [natywna kontrola sprzętu wyjętego z ZIP](../reports/package_native_validation_A1.json).

STEP jest poglądowy: brak modelu USB-C, generyczny Raytac/Flash i ograniczenie wysokości IMU. Nie jest zatwierdzoną geometrią obudowy. Lista wszystkich zmienionych plików: [production_changed_files_A1.txt](../reports/production_changed_files_A1.txt). Główne grupy zmian to C9 w źródłach/BOM, nowe raporty A01–A04/tabela/brief, aktualne kontrole i eksporty oraz skrypty manifestu/pakowania/weryfikacji. Nie zmieniono pamięci, ładowarki ani USB.

## GitHub i identyfikacja commita

Sprawdzono wskazany `ce616878e294f008d29dcf12a0448222a8181249`: publiczny adres zwrócił 404, a `git ls-remote` nie rozwiązał DNS. **Obecność tego commita na GitHubie pozostaje niepotwierdzona; nie wykonano push.** Lokalnie jego 262 śledzone ścieżki porównano z bazą b17f145: poza `.gitignore` ich zawartość jest zgodna. Baza zawiera więc pliki poprzedniego etapu, ale to nie dowodzi jego tożsamości ani obecności na serwerze. [Wynik sprawdzenia](../reports/github_verification_production_A1.json).

Główny `.git` ma w tej sesji dostęp tylko do odczytu. Nowy rzeczywisty commit tworzony jest w odrębnym gitdir na bazie b17f145 i dostarczany jako `reports/ASV1_A1_PRODUCTION_2026-10-29.bundle`. Pełny SHA, hash bundle i sprawdzonego ZIP zapisuje **`reports/production_commit_delivery_A1.json`**, tworzony po commicie poza własnym drzewem, aby uniknąć samoodwołania. [Instrukcja bezpiecznego importu i sprawdzenia serwera](github_delivery_production_A1.md). Nie deklarujemy synchronizacji z GitHubem.

## Co blokuje zwolnienie, a co wymaga prototypu

**Przed zwolnieniem zamówienia:** odpowiedź o C11/Ceff i zatwierdzone dokładne landy U3/J1/Y1, potwierdzony aktualny stack, procurement/podgląd montażu, CAM/DFM/panel. To skończona lista A01–A04, bez wymogu wykonania pomiarów na nieistniejącej płytce.

**Po otrzymaniu prototypu:** zachowane 20 prób Flash, wszystkie `NOT_RUN`; pełne 128 MiB, oba dies, 32-bit, granice/CRC/BUSY/WEL/reset/power-cut. Dostęp SWD/reset/TP pozostaje jak w poprzednim przeglądzie. Dalej USB/inrush, ripple/Ceff, uruchomienie na ograniczonym zasilaczu i symulatorze baterii/NTC, progi/PCM/termika przed prawdziwym LiPo, IMU/FIFO/timing, BLE i obudowa. Brak tych wyników sam nie blokuje wykonania prototypów. [Plan Flash](flash_firmware_test_plan_A1.md), [checklista](release_checklist.md).

**CONDITIONAL READY. Możesz rozpocząć proces wyceny/importu i przeglądu JLCPCB teraz.** Finalne zwolnienie 3–5 prototypów następuje po zapisaniu odpowiedzi A01–A04 i Twojej akceptacji. Nie oznaczono projektu jako zatwierdzonego do produkcji ani testowanego na sprzęcie.
