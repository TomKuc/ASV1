> **Etap historyczny sprzed zmiany C9.** Aktualny stan określa [production_readiness_A1.md](production_readiness_A1.md). Oryginalne wyniki i hashe obliczeń zachowano; ich zastosowanie do nowego PCB opisują raporty produkcyjne i dowód identyczności geometrii.

# Końcowy przegląd PCBA i dostępu testowego A1

Stan: **2026-10-29**, commit `28d88f22a6a9c0c0e1feb639546009518a6b5f8e`, PCB SHA256:

`cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`

**Zalecam 3–5 prototypów laboratoryjnych w JLCPCB Standard PCBA po zamknięciu bramki A opisanej poniżej.** Zachować W25Q01JVZEIQ 128 MiB i obecny routing. Nie czekać z zamówieniem na wyniki F01–F20: wykonanie tych prób wymaga prototypów. Brak wybranego MPN oddzielnego akumulatora nie oznacza, że sama PCB jest niemontowalna. Pakiet musi być zakwalifikowany przed rzeczywistym ładowaniem i użyciem na nodze.

To rekomendacja próbnej partii, nie bezwarunkowe zwolnienie plików ani deklaracja działania urządzenia. Nie zmieniano PCB, schematu ani współdzielonych dokumentów. Nie uruchamiano firmware, nie składano zamówienia/rezerwacji i nie kontaktowano się z dostawcą. Szczegółowy odczyt natywnych padów, pinmap i źródeł: [JSON](../reports/pcba_testability_final_A1.json).

## BOM i montaż

Natywny KiCad 10.0.7: **69 footprintów, 33 grupy BOM i 59 pozycji CPL, wszystkie montowane na TOP**. Zbiory referencji BOM/CPL są identyczne; dla wszystkich 59 części pola MPN i C w natywnej PCB odpowiadają BOM. Porównanie numerów/netów padów wszystkich fizycznych komponentów z manifestem nie wykazało rozbieżności. To kontrola CAD, nie walidacja katalogowych parametrów części.

Poza CPL pozostają **J3 i TP1–TP9**: to miedź testowa, nie części do zamontowania. Złącze baterii **J2 jest montowane**. Oddzielnie zapewnić mating housing/contacts/wires, chroniony pakiet z PCM/NTC, pogo-SWD i stanowisko pomiarowe; nie dopisywać ich do automatycznego CPL płytki.

Ponownie odczytano publiczne karty JLC dla **30 z 33 grup**. Dla U7/R1/R20 próby URL i wyszukania nie dały karty JLC; exact MPN i C potwierdza LCSC/szlcsc. To otwarta ścieżka zakupowa, nie dowód braku komponentu lub błędu PCB. **Publiczny katalog/cache nie jest rezerwacją**; nie użyto opóźnionych liczb stock jako obietnicy wykonania. JLC montuje wyłącznie pozycje faktycznie dopasowane i wybrane; części z pre-order/global/consign muszą zostać przyjęte do magazynu. [JLC matching](https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders), [sourcing](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction).

**IMU C22461202: Standard Only, MSL3, X-ray Required. Raytac C5119772: Economic and Standard, także X-ray Required.** Całe zlecenie powinno być Standard; nie usuwać IMU z montażu, aby obejść to ograniczenie. Brak flagi MSL/X-ray w odczycie innej karty oznacza brak informacji, nie zwolnienie z wymagań procesu.

| Referencje / ilość na PCB | Dokładny MPN | C / źródło | Odczyt usługi |
|---|---|---|---|
| R18 / 1 | ERA2AEB104X | [C445619](https://jlcpcb.com/partdetail/PANASONIC-ERA2AEB104X/C445619) | Economic and Standard |
| R3, R9, R10, R12, R13, R16, R22, R24 / 8 | 0402WGF1003TCE | [C25741](https://jlcpcb.com/partdetail/0402WGF1003TCE/C25741) | Economic and Standard |
| C6, C10, C12, C13, C15, C17, C18, C19 / 8 | CL05B104KO5NNNC | [C1525](https://jlcpcb.com/partdetail/CL05B104KO5NNNC/C1525) | Economic and Standard |
| R19, R21 / 2 | RT0402BRD0710KL | [C190095](https://jlcpcb.com/partdetail/YAGEO-RT0402BRD0710KL/C190095) | Economic and Standard |
| R4, R5, R8 / 3 | 0402WGF1002TCE | [C25744](https://jlcpcb.com/partdetail/C25744) | Economic and Standard |
| C7, C8 / 2 | CL05C100JB5NNNC | [C32949](https://jlcpcb.com/partdetail/C32949) | Economic and Standard |
| C2, C5 / 2 | CL10A106KP8NNNC | [C19702](https://jlcpcb.com/partdetail/CL10A106KP8NNNC/C19702) | Economic and Standard |
| R6, R7, R23 / 3 | 0402WGF1004TCE | [C26083](https://jlcpcb.com/partdetail/C26083) | Economic and Standard |
| R25 / 1 | 0402WGF1001TCE | [C11702](https://jlcpcb.com/partdetail/C11702) | Economic and Standard |
| C14 / 1 | CC0603KRX7R7BB105 | [C106248](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R7BB105/C106248) | Economic and Standard |
| R17 / 1 | 0402WGF2201TCE | [C25879](https://jlcpcb.com/partdetail/26622-0402WGF2201TCE/C25879) | Economic and Standard |
| C4 / 1 | CL10A225KO8NNNC | [C23630](https://jlcpcb.com/partdetail/CL10A225KO8NNNC/C23630) | Economic and Standard |
| C1, C3 / 2 | CL10A225KA8NNNC | [C57895](https://jlcpcb.com/partdetail/CL10A225KA8NNNC/C57895) | Economic and Standard |
| R11 / 1 | 0402WGF220JTCE | [C25092](https://jlcpcb.com/partdetail/25835-0402WGF220JTCE/C25092) | Economic and Standard |
| R1 / 1 | 0402WGF2402TCE | [C25769](https://www.lcsc.com/de/product-detail/Chip-Resistor-Surface-Mount_Uniroyal-Elec-0402WGF2402TCE_C25769.html) | JLC niepotwierdzone; exact ID w LCSC |
| R20 / 1 | RT0402BRD0727K4L | [C852679](https://item.szlcsc.com/913001.html) | JLC niepotwierdzone; exact ID w LCSC |
| R2 / 1 | RC0402FR-072KL | [C60488](https://jlcpcb.com/partdetail/YAGEO-RC0402FR072KL/C60488) | Economic and Standard |
| Y1 / 1 | ABS07-32.768KHZ-7-T | [C276424](https://jlcpcb.com/partdetail/AbraconLLC-ABS07_32_768KHZ_7T/C276424) | Economic and Standard |
| C9, C11, C16 / 3 | CL10A475KP8NNNC | [C1705](https://jlcpcb.com/partdetail/CL10A475KP8NNNC/C1705) | Economic and Standard |
| R14, R15 / 2 | 0402WGF5101TCE | [C25905](https://jlcpcb.com/partdetail/0402WGF5101TCE/C25905) | Economic and Standard |
| Q1, Q2 / 2 | AO3400A | [C20917](https://jlcpcb.com/partdetail/AO3400A/C20917) | Economic and Standard |
| U1 / 1 | BQ25185DLHR | [C19725033](https://jlcpcb.com/partdetail/TEXASINSTRUMENTS-BQ25185DLHR/C19725033) | Economic and Standard |
| D1 / 1 | 19-217/G7C-AN1P2/6T | [C2986030](https://jlcpcb.com/partdetail/EverlightElec-19_217_G7C_AN1P26T/C2986030) | Economic and Standard |
| J2 / 1 | SM03B-SRSS-TB(LF)(SN) | [C160403](https://jlcpcb.com/partdetail/Jst-SM03B_SRSS_TB_LF_SN/C160403) | Economic and Standard |
| U4 / 1 | LSM6DSV32XTR | [C22461202](https://jlcpcb.com/partdetail/STMicroelectronics-LSM6DSV32XTR/C22461202) | Standard Only; **X-ray** |
| U3 / 1 | MDBT50Q-P1MV2 | [C5119772](https://jlcpcb.com/partdetail/RAYTAC-MDBT50QP1MV2/C5119772) | Economic and Standard; **X-ray** |
| SW1 / 1 | SKQGABE010 | [C115351](https://jlcpcb.com/partdetail/ALPSALPINE-SKQGABE010/C115351) | Economic and Standard |
| U7 / 1 | TLV7042DGKR | [C2760466](https://www.lcsc.com/product-detail/comparators_texas-instruments-tlv7042dgkr_C2760466.html) | JLC niepotwierdzone; exact ID w LCSC |
| U8 / 1 | TLV803EA26DBZR | [C1852119](https://jlcpcb.com/partdetail/TexasInstruments-TLV803EA26DBZR/C1852119) | Economic and Standard |
| U2 / 1 | TPS7A2030PDBVR | [C963429](https://jlcpcb.com/partdetail/TexasInstruments-TPS7A2030PDBVR/C963429) | Economic and Standard |
| J1 / 1 | TYPE-C-31-M-12 | [C165948](https://jlcpcb.com/partdetail/Korean_HropartsElec-TYPE_C_31_M12/C165948) | Economic and Standard |
| U6 / 1 | USBLC6-2SC6 | [C7519](https://jlcpcb.com/partdetail/USBLC6-2SC6/C7519) | Economic and Standard |
| U5 / 1 | W25Q01JVZEIQ | [C5137036](https://jlcpcb.com/partdetail/WinbondElec-W25Q01JVZEIQ/C5137036) | Economic and Standard |

Ilości nominalne dla partii wynoszą 177–295 montowanych części; wymagany zapas technologiczny, MOQ i opłaty ustala JLC. Nie zatwierdzono zamienników. Dla precyzyjnych R18/R19/R20/R21 utrzymać 0,1% i właściwy TCR; sama zgodność obudowy 0402 nie zatwierdza podmiany. [BOM](../manufacturing/review/assembly/BOM_REVIEW_NOT_RELEASED.csv).

## Krytyczne footprinty — odczyt rzeczywistych padów

Porównano natywną numerację, wymiary i rozstawy, nie samą nazwę footprintu. Szczegóły wszystkich poniższych padów i współrzędne są w JSON. Nie uznano obecności biblioteki KiCad ani ogólnego STEP za akceptację producenta.

| Ref | Potwierdzony zakres i źródło | Pozostały warunek |
|---|---|---|
| U1 | TI DLH0010A: pitch0,40 mm, pady0,50×0,20 mm przy x=±1,05; EP0,90×1,50; pasta EP0,85×1,38. Pinout1–11 zgodny. [Źródło](https://www.ti.com/lit/ds/symlink/bq25185.pdf) | Akceptacja pasty/szablonu i lutowania EP; bez domysłu o kwalifikacji termiki. |
| U5 | WSON8 ZE: pitch1,27 mm; pady0,65×0,50; EP3,40×4,30 i cztery otwory pasty. Pinout1–8 oraz EP→GND zgodne z dokumentem. [Źródło](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf) | Landy są generic KiCad; końcowy DFM pasty/maski/tolerancji i rewizji dostawy. |
| U4 | 14 padów4+3+4+3, pitch0,50; landy0,575×0,35 (odpowiednio obrócone), zgodne z przyjętą adaptacją DS13511/TN1383. [Źródło](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf) | Proces MEMS, stencil, obsługa i X-ray; pomiar bias/noise/stress dopiero B. |
| U3 | 61 natywnych padów0,60×0,40, zgodne nety i exact P1MV2; pełny oficjalny VerL §2.1–2.5 dostępny tekstowo. [Źródło](https://www.raytac.com/download/index.php?index_id=43) | Rysunek landów/obrysu P1MV2 wymaga końcowego obejrzenia/akceptacji montażowej. Nie otrzymano bitmapy rysunku. |
| U6 | Pin1/6 DP,3/4 DN,2GND5VBUS; pitch0,95. Native land1,325×0,60 przy x±1,1375; ST zaleca1,20×0,60 z rozstawem2,30. [Źródło](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) | To większy wariant generic, nie dokładna kopia ST; zaakceptować stencil i pin1. Nie używać kierunku napisu jako jedynego znacznika. |
| U2/U7/U8 | DBV5: IN/GND/EN/NC/OUT; DGK8 open-drain TLV7042; default DBZ U8:1GND2RESET3VDD. Natywna mapa odpowiada schematowi. [Źródło](https://www.ti.com/lit/ds/symlink/tlv803e.pdf) | Nie podmieniać pakietów ani wariantów R/V supervisor lub push-pull comparator; pin1/landy generic sprawdzić w preview. |
| J1 | Zgodne aliasy wspólnych GND/VBUS;4 sloty SH oraz2NPTH. NativeNPTH±2,89/y−2,60/Ø0,65; sloty0,60×1,70 i0,60×1,20. [Źródło](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948) | **A:** obejrzeć aktualny rysunek dostawy: krótkie sloty, kołki i PCB EDGE. PDF obrazowy nie został wizualnie odczytany; nie twierdzę, że footprint jest błędny. |
| Y1 | Dwa landy1,00×1,80 przy x±1,25, obrót180; ABS07 suffix7=CL7pF. Footprint wywodzi się z EpsonFC135. [Źródło](https://abracon.com/Resonators/ABS07.pdf) | **A:** porównać land-pattern dokładnego ABS07 z rysunkiem. CL/ESR/start/frequency są B, nie warunkiem wcześniejszego pomiaru przed zakupem. |
| J2 | SH side-entry pitch1,00; pads1/2/3=VBAT/NTC/GND,0,60×1,55; dwie kotwy1,20×1,80. [Źródło](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf) | Widok od strony montażu, kotwy i polaryzację wiązki potwierdzić; kabel handlowy nie ma domyślnie właściwej kolejności. |
| Q1/Q2,SW1,D1,RC | SOT23 MOSFET1G2S3D; SW1 cztery fizyczne landy/dwie pary1/2; D1pad1K/2A; pakiety RC0402/0603 odpowiadają BOM i native. [Źródło](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf) | Kontrola polaryzacji/rotacji wszystkich59pozycji w preview JLC; nie przyjęto automatycznej translacji kątów. |

Dla J1/Y1 i rysunku Raytac screenshot narzędzia zwrócił wyłącznie tekst `ImageDisplayed`, bez bitmapy. Nie oznaczono ich jako obejrzanych. Dokumenty są publiczne i można zamknąć te kontrole bez wykonania prototypu: przez rzeczywiste porównanie rysunków i akceptację procesu montażu. To bramka A, odrębna od późniejszej kwalifikacji parametrów elektrycznych.

## Dostęp pomiarowy i programowanie

**J3 jest od spodu**, sześć pól1,20×1,20 mm w rastrze2,54 mm; to własny układ pogo, bez domniemania zgodności mechanicznej Tag-Connect/ARM-header. Natywne połączenie każdego pola z właściwym padem U3 potwierdzono przez graf łączności.

| J3 | Sygnał | Uwagi |
|---:|---|---|
|1|+3V0|VTref celu; nie podawać stąd przypadkowego zasilania debuggera|
|2|SWDIO|U3.51|
|3|GND|masa celu|
|4|SWCLK|U3.53|
|5|RESET_N|U3.40/P0.18; wymagane właściwe UICR nRESET; sterowanie open-drain|
|6|GND|masa celu|

Wszystkie **TP1–TP9 także są od spodu**, mają Ø1,00 mm i otwarcie B.Mask:

| TP | Net | X,Y PCB [mm] |
|---|---|---|
|TP1|VSYS|60.000, 90.000|
|TP2|+3V0|73.000, 84.000|
|TP3|VBAT|56.500, 93.500|
|TP4|GND|53.000, 95.300|
|TP5|RESET_N|71.500, 65.800|
|TP6|IMU_INT1|59.000, 74.000|
|TP7|IMU_INT2|59.000, 76.000|
|TP8|NTC_TS|56.000, 90.000|
|TP9|CHG_ALLOW_H|64.000, 86.000|

Zapewnić dostęp od spodu na płytce stołowej; nie zasłaniać go przyklejoną baterią/obudową przed próbami. SW1 jest przyciskiem GPIO, nie przyciskiem sprzętowego resetu Flash ani odłącznikiem zasilania. Własny reset MCU jest dostępny przez J3.5 i TP5.

**Nie ma dedykowanych pól/headera QSPI. Wszystkie 12 przelotek QSPI/CS jest tentowanych z obu stron** i nie należy traktować ich jako odsłoniętych pól sondy. Kandydaci dla mikrosond lub krótkich przewodów: CS=R10.2; CLK po rezystorze=R11.2; IO0=U5.5; IO1=U5.2; IO2=R12.2/U5.3; IO3=R13.2/U5.7. Toe WSON i rezystory0402 są małe: przygotować stanowisko pod mikroskopem i aktywne sondy o małej pojemności. Zmierzona z taką sondą magistrala jest obciążona sondą; porównać CRC/zachowanie z pomiarem odłączonym. Brak wygodnego QSPI headera jest ograniczeniem C, nie wykrytą koniecznością reroutingu A1.

Dostęp do IO0/IO1 nie jest gwarantowany zwykłym chwytakiem: wyjście landu poza korpus WSON jest niewielkie. Dla egzemplarza pomiarowego może być potrzebne lokalne odsłonięcie maski na trasie/polu przelotki, mikrolutowanie albo interposer. To kontrolowany rework jednego prototypu, z późniejszym sprawdzeniem zwarć i wpływu przewodów, nie zmiana kanonicznego PCB ani już wykonana czynność. Testy funkcjonalne CRC nie wymagają stałego podłączenia tych sond.

Spare GPIO nie wyprowadzono na J3. Diagnostyczny wolny marker można rozważyć na istniejącym wyjściu LED, zachowując ograniczenia Raytac dotyczące standard-drive/slow GPIO; nie używać go jako szybkiego TRACE. Do wyzwalania odcięcia wystarczy obserwacja CS lub izolowany marker testowy.

## Reset i zaniki bez niezamierzonego podtrzymywania

Płytka nie ma osobnego wyłącznika VCC Flash ani sprzętowej linii RESET Flash. F14 używa poleceń66/99, a całkowite power-cut testuje zanik całego urządzenia. Nie da się na obecnej PCB niezależnie obniżać wyłącznie VCC U5 bez zaprojektowanego stanowiska izolacji/rework; obecny plan F01–F20 tego nie wymaga.

Stanowisko: kontrolowane, ograniczone prądowo źródło zastępujące baterię na J2.1/J2.3, emulator właściwej rezystancji NTC na J2.2 oraz zewnętrzny przełącznik/sag. Mierzyć rzeczywiste VBAT, TP2/+3V0 i lokalne VCC U5; napięcie zadane na wejściu nie jest napięciem Flash po LDO. Nie wtłaczać napięcia w TP2 przy połączonym LDO bez analizy prądu wstecznego.

Przy rzeczywistym odcięciu usunąć albo niezależnie przełączać **USB VBUS**: samo odpięcie baterii przy USB może pozostawić SYS aktywne. Wyłączyć target-power debuggera, używać J3.1 jako VTref i na czas zaniku odłączyć/izolować także SWD/reset oraz wszystkie aktywne wyjścia instrumentów. Nie zakładać, że sonda/programator automatycznie przechodzi w HiZ przy niezasilonym celu. Potwierdzić przebiegiem na oscyloskopie, że żaden USB/data/probe/GPIO nie podtrzymuje szyny.

To wykonalny zewnętrzny fixture, nie funkcja już zamontowana w urządzeniu i nie wykonana próba. Pełny kontrakt resetu/DPD/dwóch dies i odpornego dziennika pozostaje w [audycie Flash](flash_compatibility_A1.md).

## Pokrycie planu F01–F20

Istniejące połączenia nie wykazały konieczności zmiany PCB dla planowanych prób. Potrzebne są firmware diagnostyczne, fixture i instrumenty. **Wszystkie 20 prób pozostają NOT_RUN; żadna nie uzyskała sprzętowego PASS.** F12 nie gwarantuje wymuszenia identycznej asymetrii czasowej obu dies na żądanie; test syntetycznych statusów jest tylko uzupełnieniem.

| Próby | Potrzebny dostęp |
|---|---|
|F01,F03–F11|SWD + diagnostyczny driver/host CRC; F02/F08/F09 dodatkowo sondowanie CS/CLK/IO i kontrola kontekstu dies|
|F02,F12|Mikrosondy/analizator i log SR obu dies; warunki C2/WEL zgodne z pozyskaną dokumentacją|
|F13–F15|J3.5/TP5 dla MCU-reset; QSPI dla software-reset/DPD/wake; żadnego domniemania POR Flash po resecie MCU|
|F16–F17|Kontrolowane odcięcie obu możliwych źródeł i brak backpower; TP3/TP2/lokalneVCC + recovery journal|
|F18–F19|Host/programator, istniejące USB/BLE/IMU; TP6/TP7 IRQ i liczniki firmware|
|F20|Sondy małej pojemności, źródło, temperatura i pomiary timing/CRC pod obciążeniem|

Szczegóły każdego przypadku: [plan F01–F20](flash_firmware_test_plan_A1.md) i JSON tego audytu. Rzeczywista obsługa USB/BLE/RTT nadal wymaga implementacji; obecność fizycznego złącza nie oznacza gotowego eksportera danych.

## Bramki decyzji

**A — przed zamówieniem:** zamknąć exact BOM/stock/import dla wszystkich59pozycji, w szczególności U7/R1/R20; faktyczne rysunki/landy J1/Y1/Raytac; pin1/polaryzację/rotacje; stencil, maskę, EP, sloty/NPTH i proces marginesu0,150 mm; Standard/X-ray/MSL oraz panelizację/fiducjale. Uzgodnić konkretne warunki fabrykacji/stackup i elektryczne ograniczenia z końcowych audytów zasilania/Raytac/DFM. Same0DRC/opens nie są akceptacją procesu.

**B — po wykonaniu prototypów:** driver128MiB i AN/semantyka dies, wszystkie20prób, timing/SI QSPI/SPI/USB, prąd/USB suspend/inrush, IMU/BLE/termika, brownout i integralność dziennika. Kwalifikacja pakietu/PCM/NTC jest wymagana przed rzeczywistym ładowaniem/użyciem, a nie do samego montażu PCB. Pomiary tych właściwości nie mogą być warunkiem posiadania pierwszych egzemplarzy do ich pomiaru.

**C — późniejsze optymalizacje:** wygodniejsze pola QSPI, debug interposer lub opcjonalne sterowanie zasilaniem Flash. Obecny brak tych udogodnień nie uzasadnia zmiany pojemności ani pełnego reroutingu.

Po zamknięciu A zamówić **3–5 sztuk jako partię laboratoryjną**, zachować co najmniej jeden egzemplarz referencyjny oraz osobny do destrukcyjnych fault-injection/rework. Rozpocząć od kontroli montażu/X-ray i uruchomienia z kontrolowanego źródła, następnie wykonywać B. Ten raport nie stwierdza zamknięcia bramki A ani kwalifikacji gotowego produktu.
