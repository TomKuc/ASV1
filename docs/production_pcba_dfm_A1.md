# A1 — zamknięcie A03/A04: PCBA, CPL i lokalne CAM/DFM

Stan odczytu: **2026-10-29**. PCB SHA256:

`1d3bb700a2b686ef68589bf3295488d2144a1d51a857cec7651e45be175a6134`

**A03 — EXTERNAL CONFIRMATION. A04 — EXTERNAL CONFIRMATION.** Zamknięto opisane niżej kontrole spójności i geometrii nominalnej; nie uzyskano akceptacji procesu ani rezerwacji części w JLCPCB. Nie wykryto w tym zakresie nowego potwierdzonego błędu wymagającego zmiany PCB. Nie zmieniono architektury, pamięci ani routingu.

Wyniki maszynowe: [PCBA/DFM JSON](../reports/production_pcba_dfm_A1.json), [pełna tabela części](../reports/production_component_status_A1.csv). Kontrola jest powtarzalna skryptem [review_production_pcba_A1.py](../scripts/review_production_pcba_A1.py), uruchamianym Pythonem dołączonym do KiCad. Skrypt tylko czyta PCB i eksporty. Po ponownym eksporcie należy uruchomić go ponownie, aby zapisał aktualne hashe Gerberów.

## A03 — części i dostępność

Natywny odczyt KiCad 10.0.7 i aktualne eksporty potwierdzają **69 footprintów, 33 grupy BOM, 59 części CPL, wszystkie TOP**. Zbiory referencji BOM/CPL są identyczne. Dla każdej pozycji sprawdzono dokładny MPN, C, footprint, współrzędne względem wspólnego origin oraz rotację CPL względem PCB. C9 jest teraz `CL10A106KP8NNNC / C19702`, w jednej grupie z C2/C5. C11 i C16 pozostają `CL10A475KP8NNNC / C1705`.

CSV ma oddzielny wiersz dla każdego z 59 montowanych elementów: dokładny wariant, C, footprint, współrzędne, kąt, położenie pinu1 jeśli występuje, polaryzację oraz wymagany proces. Dodatkowe trzy wiersze obejmują oddzielny pakiet, wiązkę i pogo fixture — **montaż ręczny**, poza automatycznym CPL. **J2 jest częścią montowaną; J3 i TP1–TP9 są miedzią PCB**, bez części do zakupu i lutowania.

Każdej z 59 pozycji nadano status **„wymaga potwierdzenia”**. Nie użyto statusu „dostępny”, ponieważ nie odczytano zalogowanego dopasowania BOM i stanu zamówienia. Nie użyto „niedostępny”, bo nie ma dowodu niedostępności. Dla 30/33 grup zachowano wcześniejsze publiczne dowody identyfikacji/usługi z tej samej daty; powiązano je ponownie według dokładnego MPN/C. Ponownie odczytano publiczne karty U1–U6, U8, J1, J2 i Y1. To rozróżnienie jest jawne w CSV/JSON; wcześniejszy odczyt pozostałych kart nie jest przedstawiany jako nowa rezerwacja. [Poprzedni zapis katalogowy](../reports/pcba_testability_final_A1.json).

| Grupa wymagająca szczególnego sprawdzenia | Dokładny MPN i C | Wynik końcowy |
|---|---|---|
| U7 | TLV7042DGKR / C2760466 | Ponowne wyszukanie i bezpośredni URL nie dostarczyły karty JLC dokładnego wariantu. To nie dowód braku części. Potwierdzić DGK8/VSSOP8, open-drain oraz Standard PCBA. |
| R1 | 0402WGF2402TCE / C25769 | Analogicznie: potwierdzić dokładne 24kΩ,1%,0402; nie zaakceptować automatycznie podobnego kodu/wartości. |
| R20 | RT0402BRD0727K4L / C852679 | Potwierdzić 27.4kΩ,0.1%,0402 i TCR dokładnej serii. Wynik wyszukiwania dla 17.4kΩ lub innego sufiksu nie jest zamiennikiem. |

LCSC potwierdzało wcześniej tożsamość tych trzech części, lecz obecność C w LCSC nie potwierdza obsługi wybranego zamówienia PCBA. Jeżeli katalog nie dopasuje pozycji: JLC ma potwierdzić procurement/preorder/global sourcing/consignment i przyjęcie do magazynu **przed** zwolnieniem zlecenia. Tylko zaznaczone i dopasowane pozycje są montowane. [JLC — component matching](https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders).

W publicznym katalogu **U4 LSM6DSV32XTR/C22461202 jest Standard Only, MSL3, X-ray Required**; **U3 MDBT50Q-P1MV2/C5119772 wymaga X-ray**, obsługuje Economic and Standard. Wybrać **Standard PCBA dla całej płytki**. U1 BQ25185DLHR i U5 W25Q01JVZEIQ mają odczytane MSL3. Brak uzyskanej flagi MSL/X-ray dla innej pozycji nie zwalnia z wymagań jej dokumentacji. [U4](https://jlcpcb.com/partdetail/STMicroelectronics-LSM6DSV32XTR/C22461202), [U3](https://jlcpcb.com/partdetail/RAYTAC-MDBT50QP1MV2/C5119772), [U1](https://jlcpcb.com/partdetail/TEXASINSTRUMENTS-BQ25185DLHR/C19725033), [U5](https://jlcpcb.com/partdetail/WinbondElec-W25Q01JVZEIQ/C5137036).

**Rotacje są zgodne z natywnym CAD, lecz nie są jeszcze zatwierdzone do montażu.** Nie zastosowano zgadywanej korekty kątów pod taśmę JLC. Trzeba zatwierdzić wszystkie 59 pozycji w rzeczywistym preview: szczególnie pin1 U1–U8, bramkę/źródło Q1/Q2, katodę D1, kierunek USB J1 i polaryzację J2. D1 ma pad1=K/pad2=A; Q1/Q2:1G/2S/3D; J2:1VBAT/2NTC/3GND. Rezystory i MLCC nie mają polaryzacji. Y1 jest dwukońcówkowym kwarcem bez polaryzacji, ale dopasowanie jego landów jest oddzielnym warunkiem A01. Bezpośrednie karty J1/Y1/J2 potwierdzają MPN i usługę, nie ostateczną geometrię landów. [J1](https://jlcpcb.com/partdetail/Korean_HropartsElec-TYPE_C_31_M12/C165948), [Y1](https://jlcpcb.com/partdetail/AbraconLLC-ABS07_32_768KHZ_7T/C276424), [J2](https://jlcpcb.com/partdetail/Jst-SM03B_SRSS_TB_LF_SN/C160403).

Nominalna ilość części dla 3–5 płytek wynosi 177–295; zapas technologiczny, MOQ, faktyczną ilość montowanych PCB i lead time ma podać JLC. Nie zatwierdzono zamienników. Dla R18/R19/R20/R21 zachować klasę0.1% i właściwy TCR. Oznaczenia DRAFT przy C7/C8/R11 są odziedziczonymi opisami parametrów do kwalifikacji oscylatora/QSPI, a nie zgodą na dowolne MPN; dokładne części pozostają w BOM.

## A04 — trzy rzeczywiste minima odstępu

Globalne minimum jest współdzielone przez **trzy pary**, nie tylko jedną. Współrzędne poniżej są natywnymi PCB mm; współrzędne plot/drill/CPL używają origin(50,101.6) i dodatniego Y w górę.

| Pad / środek [mm] | Środek via [mm] | UUID via | Otwór→SMD/pasta CAD |
|---|---|---|---|
| U6.2/GND (70.4625,93.3000) | (71.4000,93.3000) | 0000186c-eba4-42e1-b568-6e74e683c917 | 0.150001mm |
| C5.2/GND (71.4500,79.0250) | (71.4500,78.3000) | c33d0a5e-877f-4174-8489-0b7f8e8987d2 | 0.150001mm |
| C4.2/GND (69.1500,79.0250) | (69.1500,78.3000) | f66c258b-1003-4c4d-a48e-ab8594dec65a | 0.150001mm |

Każde via ma otwór0.25mm i średnicę miedzi0.50mm. Odległość zewnętrznego pierścienia via od sąsiedniego otwarcia maski/pasty wynosi nominalnie tylko **0.025mm**. To nie jest wymagany mostek między dwoma otworami maski: via nie ma własnego otwarcia. Miedź jest tego samego netu GND, więc sama bliskość pierścienia nie stanowi zwarcia różnych netów. Istotne pozostaje utrzymanie maski nad otworem oraz unikanie odpływu lutu.

Wykonano **bezpośredni odczyt aktualnych F.Mask/B.Mask/F.Paste/B.Paste Gerber**, nie tylko flag tentingu w KiCad. Odczytano wszystkie błyski apertur w tych plikach i policzono odległość od trzech otworów. Eksportowane F.Mask/F.Paste mają odległość **0.150000mm** od krawędzi otworu (różnica1nm wynika z konserwatywnego progu natywnej kontroli). Żaden otwór via nie przecina apertury maski ani pasty. Odległości B.Mask są odpowiednio3.058314/5.281987/6.253408mm; B.Paste nie zawiera apertur. Parser odrzuca nieobsługiwane operacje Gerber; to ograniczona kontrola lokalna, **nie pełny niezależny CAM ani analiza tolerancji fabrycznych**. [Źródłowy audyt geometrii](../reports/via_pad_audit.json).

JLC podaje, że otwory VIA nie mają określonej tolerancji średnicy; **nie wolno zastosować do nich tolerancji +0.13/−0.08mm dla otworów padów PTH**. JLC wskazuje też ryzyko niepełnego pokrycia via przy zbyt bliskim otwarciu maski. Zatem nominalne0.150mm i brak kolizji nie stanowią dowodu pewnego tentingu po wierceniu/rejestracji/maskowaniu. Zachować **ENIG i tenting**, a nie wybierać HASL/exposed vias bez analizy. Nie zlecać automatycznie ink plugging: JLC ma osobne ograniczenia bliskości padów dla tego procesu. [JLC — via covering](https://jlcpcb.com/help/article/pcb-via-covering).

**Wymagana odpowiedź CAM:** akceptacja trzech wskazanych miejsc dla rzeczywistego wiercenia/rejestracji i procesu maski/pasty; potwierdzenie ochrony otworów przed pobieraniem lutu podczas reflow. Jeśli JLC odrzuci geometrię, dopiero wtedy uzgodnić lokalne przesunięcie tych via lub odpowiedni proces. Nie ma obecnie dowodu uzasadniającego pełny rerouting.

## WSON, LGA, maska i pasta

Ponowny natywny odczyt i dowód niezmienności geometrii pozwalają zachować wcześniejsze porównania pinów/landów bez udawania nowego pełnego audytu. [Dowód geometrii](../reports/production_geometry_equivalence_A1.json), [wcześniejsze szczegółowe footprinty](pcba_testability_final_A1.md), [aktualne J1/Y1/Raytac](production_footprints_A1.md).

| Element | Aktualna geometria | Akceptacja procesu do uzyskania |
|---|---|---|
| U1 BQ25185DLHR | pitch0.40mm, landy0.50×0.20; EP0.90×1.50 i oddzielna apertura pasty0.85×1.38 z zaokrągleniem | Grubość szablonu, ilość pasty, zwilżenie EP i voiding zgodnie z TI; odczyt CAD nie kwalifikuje termiki. [TI](https://www.ti.com/lit/ds/symlink/bq25185.pdf) |
| U5 W25Q01JVZEIQ | ZE WSON8 8×6mm, pitch1.27; landy0.65×0.50; EP3.40×4.30; cztery osobne apertury pasty1.37×1.73, zaokrąglone | Aktualny rysunek dostawy ZE, EP, stencil, MSL3/reflow/voiding. Zachować128MiB i dokładny sufiks. [Winbond — dokument producenta w mirrorze](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf) |
| U4 LSM6DSV32XTR | LGA14, układ4+3+4+3, pitch0.50; landy0.575×0.35 obrócone wg boku; zachowany środek bez miedzi | Szablon/obsługa MEMS, reflow/MSL3, X-ray; nie dociskać sensora i ograniczyć naprężenia depanelizacji. [ST TN1383](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf) |

Te geometrie są w eksportach, lecz producent może wymagać dostosowania **szablonu procesu**; każdą zmianę landów/maski lub copper uzgodnić osobno. Nie zatwierdzono automatycznych zmian CAM.

## Warstwy, wiercenia, panel i fiducjale

Aktualny zestaw ma 11 Gerberów: F.Cu/In1.Cu/In2.Cu/B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS oraz Edge.Cuts; osobne Excellon PTH i NPTH, mapy i raport wierceń. Zapis Gerber/Excellon, wspólny origin, hashe i równość BOM/CPL sprawdza [export_manifest.json](../manufacturing/review/export_manifest.json) oraz [kontrola geometrii produkcyjnej](../reports/manufacturing_geometry_review.json). ZIP do wgrania jako PCB zawiera Gerber/Drill; BOM/CPL wgrywa się osobno. Generic KiCad stackup job jest tylko referencją **NOT_FOR_ORDER**, poza upload ZIP. Nie zastępuje ustalenia stackupu A02.

Na pojedynczej PCB brak dedykowanych fiducjali i szyn transportowych. To wymaga rozwiązania przez **zaakceptowany panel/rails JLC dla Standard PCBA**, a nie dopisywania ich w obszarze sensora lub anteny. Oficjalne zalecenie: szyny≥5mm, fiducjale CuØ1mm z maskąØ2mm,3–4 znaczniki, wymagany odstęp od krawędzi3.35mm z obszarem odniesienia. JLC ma przedstawić rysunek panelu/procesu; zatwierdzić orientację, podpory, depanelizację i sposób dostawy. Nie zastosowano wymagań paneli flex do tej sztywnej PCB. [JLC — rails/fiducials](https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order).

Panelowa miedź, tooling, taby i szyny nie mogą wchodzić w keepout RF ani wymuszać łamania blisko IMU. Należy uzgodnić usunięcie szyn lub ich bezpieczne odcięcie; domyślnie JLC może dostarczyć płytki z szynami. Nie wygenerowano fikcyjnego zatwierdzonego panelu.

## Co nie blokuje wykonania PCB

Nie trzeba czekać na fizyczne F01–F20 Flash, pomiary IMU/BLE, poboru prądu, USB, oscylatora i termiki — wszystkie pozostają do wykonania na prototypach, bez sprzętowych PASS. Obecny SWD/reset/testpoints i ścieżka testów pozostają geometrycznie identyczne jak we wcześniejszym raporcie; C9 nie zmienia ich połączeń. Nie wykonywano nowego pełnego audytu dostępu testowego. Oddzielny pakiet/NTC/PCM musi być zakwalifikowany przed rzeczywistym ładowaniem i użyciem na nodze; bezpieczne uruchamianie stołowe przewiduje ograniczone prądowo źródło i kontrolowany fixture.

Przed zwolnieniem PCBA pozostają konkretne odpowiedzi JLC: pełne dopasowanie części/stock,59 orientacji, trzy lokalne minima i tenting, stencil/reflow/X-ray oraz panel/rails/fiducjale. **Można rozpocząć wycenę/import/DFM; nie ma jeszcze akceptacji produkcyjnej producenta.**
