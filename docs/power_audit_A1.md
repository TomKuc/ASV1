# Audyt zasilania A1 — ASV1

Data: **29.10.2026**. Audyt porównuje bazowy PCB `b5487d09753bbf0490bf91bda6c803934609b778283ef87c044309bc1514f678` z końcowym odczytem `cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`. W tym stanie prowadzący projekt wdrożył R24 pull-up do +3V0, relokację USB ESD U6 oraz poprawki geometrii. Odczyt `da211523…` był wcześniejszym stanem po R24, przed relokacją U6; zachowano go jako historię. Końcowy odczyt, skróty wejść i historia są w [power_audit_A1.json](../reports/power_audit_A1.json). W ramach tego przeglądu nie regenerowano projektu, nie edytowano PCB/schematu i nie przeprowadzono prób sprzętowych.

**Wniosek:** zachować BQ25185, chroniony pakiet i niezależne okno U7/U8/Q1/Q2. R24 pull-up domyślnie blokuje ładowanie po resecie MCU przy poprawnym +3V0. Odsprzęganie IMU i naprawiona lokalna gałąź Flash mają udokumentowaną ciągłość. Nie potwierdzono jeszcze zgodności całego USB, bezwarunkowych granic ochrony temperatury, czasu ładowania konkretnego pakietu ani temperatur w obudowie. Są to oddzielne warunki kwalifikacji; audyt nie jest zwolnieniem do produkcji.

Końcowe odświeżenie `cdcbd234…` obejmuje przyjęte poszerzenie 18 istniejących odcinków USB na In2 z 0.15 do 0.17 mm. Ponowny odczyt padów, przecięć miedzi i zapisanych fill potwierdził **identyczne wyniki wszystkich 17 pętli i 17 powrotów GND**, w tym lokalnych dróg In2. Połączenia zasilania i mostek Flash zachowano. Bieżący profil DRC zawiera jawną regułę pary USB: minimum 0.125 mm, optimum 0.13 mm; zerowy wynik geometryczny w tym profilu nie jest kwalifikacją SI.

Określenie „reset blokuje” w tym raporcie dotyczy resetu zwalniającego GPIO do HiZ. Retencję GPIO przy System OFF oraz hang z pozostawionym LOW rozróżnia [końcowa tabela rozruchu](charge_startup_final_A1.md); nie są one równoważne HiZ.

## Findings

| ID | Wynik / priorytet | Ustalenie |
|---|---|---|
| PWR-A1-01 | Potwierdzone w geometrii | 35 referencji zasilania porównano z eksportem netlisty: brak rozbieżności pinów/netów; końcowy native odczyt ma 0 opens. Ponownie sprawdzono 17 par IC–kondensator i wszystkie 17 padów GND/EP U1–U8. Mostek B.Cu Flash istnieje. |
| PWR-A1-02 | Korekta domyślnego inhibit wdrożona; USB nadal otwarte | R24 pull-up usuwa automatyczne zezwolenie po reset/HiZ. Nie ogranicza sam prądu portu ani nie klasyfikuje adaptera. |
| PWR-A1-03 | Wysoki, otwarte przed ładowaniem rzeczywistego pakietu | Brak kwalifikowanego MPN pakietu/PCM i potwierdzonego NTC na ogniwie. BQ nie zastępuje tych zabezpieczeń. |
| PWR-A1-04 | Wysoki, warunkowy dowód progów | Skrypt odtwarza podane narożniki. Budżet 22 mV zawiera założenie 1.5 mV poza gwarantowanymi danymi; potrzebna kwalifikacja lub dodatkowe limity producenta. |
| PWR-A1-05 | Otwarte, timer i prąd ładowania | 360 min jest TYP bez tolerancji min/max; /CE resetuje timer. Nie gwarantować pełnego ładowania 500 mAh ani łącznego limitu wielu cykli. |
| PWR-A1-06 | Otwarte, MLCC i termika | Nominały i lokalne połączenia są znane. Ceff oraz termika BQ/LDO/pakietu nie są potwierdzone; brak F.Cu GND pour przy BQ. |
| PWR-A1-07 | Jawny kompromis, zachować ochronę | Około138 µA dotyczy określonego stanu inhibit; pozostałe stany mają inny pobór. Nie usuwać okna dla redukcji standby. |
| PWR-A1-08 | Otwarte, zachowanie uszkodzonego NTC | Zwarcie TS może uzbroić factory mode; po odłączeniu USB SW1 nie wybudzi urządzenia. Sprawdzić obsługę tej usterki. |
| PWR-A1-09 | Wysoki, kwalifikacja integralności zapisu | U8 steruje wyłącznie ładowaniem. Nie jest sygnałem ważnego zasilania Flash ani resetem MCU. |

## Rzeczywiste połączenia i odsprzęganie — PWR-A1-01

Native PCB, eksport netlisty i raporty są porównywane jako oddzielne źródła. Zweryfikowano m.in. U1/U2/U3/U4/U5/U7/U8, Q1/Q2, programowanie prądów, odniesienia, kondensatory i J2. Wybrane połączenia:

- U1: IN10=VBUS, SYS1=VSYS, BAT2=VBAT, GND5/EP11=GND, TS6=NTC_TS, /CE4=CHG_CE_N.
- U2: IN1 i EN3=VSYS, OUT5=+3V0, GND2; EN nie jest sterowane przez firmware.
- U3: VDD28 i VDDH30=+3V0, VBUS32=VBUS. U4 VDD8/VDDIO5 i U5 VCC8 korzystają z +3V0.
- J2: 1=PACK+, 2=NTC_TS, 3=PACK−/GND. NTC_TS nie jest połączony z ADC MCU.
- /CE ma tylko U1.4, Q1.3 i R3; MCU dochodzi do bramki odrębnego Q2. Nie ma ścieżki GPIO wymuszającej zezwolenie wbrew U7/U8.

Odczyt KiCad 10.0.7 potwierdził R24.1=CHG_INHIBIT oraz R24.2=+3V0 w PCB i wyeksportowanym schemacie. Nienazwane/niepodłączone elektrycznie pola mocujące J2 nie są węzłami netlisty. Raport integracyjny z 29.10 o 17:52:55 ma **DRC 0 naruszeń, 0 opens, 0 parity**; ERC z 17:38:42 ma 0 błędów i 2 jawne ostrzeżenia dla U4.2/3. Są to kontrole połączeń i geometrii, a nie badanie działania.

[Raport rzeczywistego routingu](../reports/power_routing_review.json) odświeżono z finalnego `cdcbd234…`: ponownie wyznaczono 17 par pin–kondensator z natywnych przecięć miedzi F.Cu, lokalnych wielokątów In2 oraz 17 powrotów padów GND/EP do In1. Fizycznie odczytano mostek `699315a4-e5c7-49d0-b342-712824bf66c2`: +3V0, B.Cu, 0.30 mm, (71.75,72.5)→(72.9,73.0). Usuwa dawny objazd In2 długości około28 mm. U5→C15 ma około2.469 mm odcinków XY i dwa istniejące przejścia przez warstwy; C16 korzysta z lokalnego węzła C15 i około3.578 mm zapisanej In2. Nie mylić XY z długością trójwymiarową ani symulacją impedancji zasilania.

IMU ma osobne C12/C13 100 nF; lokalne odcinki zapisanej In2 między vias wynoszą około1.191/1.341 mm, a nie drogę przez resztę szyny. C14 jest dodatkowym bulk. Vias GND tych kondensatorów są około0.62 mm od środków padów i kontaktują In1. Nie zastąpiono odsprzęgania samym odległym kondensatorem zbiorczym. Parametry szumu i minima napięć nadal wymagają pomiaru.

U1 ma lokalne F.Cu do C1/C2/C3, a U2 do C4/C5; pozostałe lokalne gałęzie modułu, U7 i U8 nadal kontaktują zapisaną In2 w bezpośrednim otoczeniu. Po relokacji U6 do (71.6,93.3) jego GND ma 0.9375 mm F.Cu do via (71.4,93.3), z ośmioma próbkami pierścienia we fill In1. Odcinki złączowe USB skrócono do DP 12.997 mm i DN 15.552 mm. U3–C11 i jego powrót GND pozostały niezmienione; C11 nie jest lokalnym bypass U6. Dodatkowe przejścia, impedancja, SI i odporność ESD pozostają do kwalifikacji.

## Prąd i napięcie ładowania — PWR-A1-03/05

R1=24 kΩ wybiera 4.2 V i klasę ILIM100; R2=2 kΩ ustawia nominalnie150 mA. [Oficjalna tabela TI BQ25185 Rev.B](https://www.ti.com/lit/ds/symlink/bq25185.pdf) podaje przy określonych warunkach VIN=5 V:

| Parametr | Minimum / typ / maksimum |
|---|---|
| ILIM100 | 80 / 90 / 98 mA |
| ICHG dla dokładnego RISET=2 kΩ | 135 / 150 / 165 mA |
| Dokładność napięcia BAT | ±0.5%, czyli dla4.2 V:4.179–4.221 V |
| Timer fast charge | 360 min wyłącznie TYP |

Tolerancja RISET±1% daje dodatkowy błąd: sam początkowy rozrzut odpowiada około133.7–166.7 mA po konserwatywnym połączeniu z tabelą IC; dochodzą TCR/warunki rzeczywistego rezystora. Bieżące zasilanie ogranicza dostępny prąd znacznie wcześniej, ale pakiet musi odpowiadać nastawie ISET i dopuszczalnemu napięciu, a nie wyłącznie oczekiwanemu prądowi przy słabym porcie.

Wspólny limit wejścia zasila system i ładowanie. Realny prąd BAT może być niższy, zerowy, a przy dużym obciążeniu bateria może uzupełniać SYS. Ilustracyjnie:500 mAh/80 mA=6.25 h, jeszcze bez obciążenia systemu i CV; dla300 mAh jest to3.75 h. To nie są czasy pełnego cyklu. Kwalifikować300 mAh przy rzeczywistym obciążeniu i najwolniejszym ładowaniu;500 mAh nie ma tu gwarancji zakończenia.

[TI safety timer](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-F91448CC-01A7-4312-A893-4B2E9FC88D89) rozróżnia precharge i fast charge; precharge ma25% tMAXCHG. /CE lub ponowne podanie wejścia kasuje licznik. Zewnętrzne okno temperatury operujące przez /CE może więc rozpocząć nowy cykl po przerwie; nie traktować360 min jako nieprzekraczalnego łącznego czasu podłączenia. Firmware nie może stosować okresowych restartów w celu obchodzenia błędu timeout. Wartość min/max tolerancji czasu nie została dopisana z domysłu.

Pakiet musi mieć własne PCM z potwierdzonymi progami OV/UV/OCP/short, dozwolonym prądem i temperaturą. NTC ma być fizycznie na ogniwie, z izolacją i odciążeniem, oraz mierzony względem PACK− zgodnie z projektem wiązki. Sprawdzić z dostawcą także stan PCM-off i brak obejścia jego zabezpieczeń przez przewód NTC. Nie wybrano gotowego MPN pakietu i nie przyznano bezpieczeństwa nieokreślonemu „protected LiPo”. Próby ładowania realnego ogniwa i użycie na nodze wymagają zamknięcia tego punktu; samą płytkę można wcześniej badać z kontrolowanym źródłem/symulatorem.

## Sprzętowe okno i granice jego dowodu — PWR-A1-04

R18/R19=100k/10k, R20/R21=27.4k/10k, tolerancja początkowa0.1%; model przyjmuje łączny niezależny rozrzut±0.5% każdego rezystora. U7 to open-drain TLV7042, nie push-pull TLV7032. OUTA/OUTB i U8 /RESET są zwarte z ALLOW_H. Q1 zwiera /CE tylko przy zezwoleniu; MCU może przez Q2 jedynie ściągnąć ALLOW_H i zabronić ładowania.

Ponownie uruchomiony `scripts/check_charge_temperature.py` daje identyczny wynik jak [zapisany raport](../reports/charge_temperature_corners.json):

| Zakres +3V0 | Próg HOT w modelu | Próg COLD w modelu |
|---|---:|---:|
|2.955–3.045 V|29.11–39.27°C|3.55–10.02°C|
|2.5872–3.045 V, przed progiem U8|29.11–43.60°C|3.55–13.16°C|

To rozrzut granic, nie obietnica ładowania w całym0–45°C. Wspólny przedział zezwolenia dla wszystkich analizowanych narożników jest dużo węższy: około13.2–29.1°C przy pełnym zakresie napięcia modelu. Jest to konserwatywny kompromis, który może ograniczać ładowanie ciepłego modułu.

Warunki odbioru pakietu pozostają **R(0°C)≥24 kΩ i R(45°C)≤5.20 kΩ**, łącznie z przewodami/tolerancjami/starzeniem oraz monotonicznym R(T). Model wymaga odpowiednio >23.073 kΩ i <5.344 kΩ. Przy wartościach odbiorczych marginesy elektryczne wynoszą około33.85 mV dla0°C i5.67 mV dla45°C, przed błędami niewłączonymi do założeń modelu. Temperatura NTC nie zastępuje temperatury wnętrza ogniwa ani opóźnienia termicznego.

[Semitec103AT-2](https://www.semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf) jest rzeczywistym kandydatem10 kΩ±1%, B25/85=3435 K±1%; producent podaje R(0°C)=27.28 kΩ i czas termiczny około15 s w powietrzu. Nie jest to zatwierdzenie konkretnego pakietu. Stałe B25/85 nie jest pełną charakterystyką R(T) w całym zakresie. R(45°C), montaż i dynamikę ma potwierdzić dostawca albo kwalifikacja.

Istotne ograniczenie: [TI TLV7042 §5.9](https://www.ti.com/document-viewer/TLV7042/datasheet/GUID-31582E48-6F8E-4432-8EF5-9EFAE30D7199) daje max offset±8 mV i histerezę3–25 mV w podanych punktach VCM=VS/2; CMRR, PSRR, IB i upływ wyjścia mają wartości typowe. Przyjęte22 mV obejmuje8+12.5+1.5 mV; ostatnie1.5 mV nie jest odczytanym gwarantowanym limitem TI. Nie zmieniać warunkowego modelu w bezwarunkową gwarancję. Przed takim twierdzeniem potrzebne są dodatkowe granice producenta albo kwalifikacja rzeczywistych progów i dryftu.

U8 TLV803EA26DBZR ma próg2.64 V±2% i zwalnia reset po130–270 ms. [TI TLV803E](https://www.ti.com/lit/ds/symlink/tlv803e.pdf) określa stan wyjścia od0.7 V przy wskazanym obciążeniu; poniżej nie gwarantuje stanu. Reakcja na zapad ma skończone opóźnienie. [TLV7042 POR](https://www.ti.com/document-viewer/TLV7042/datasheet/GUID-987AA8A0-D53D-4B15-96AF-A4749EB95734) sam pozostawia wyjścia HiZ; dlatego nie usuwać U8. Nowy pull-up Q2 poprawia domyślną blokadę przy sprawnej szynie, lecz nie stanowi dowodu dla dowolnego zapadu lub częściowo uszkodzonego zasilania poniżej0.7 V. Te próby pozostają otwarte.

TS może mieć dodatnie napięcie przy wyłączonym +3V0. [TI opisuje wejścia TLV7042 jako fault-tolerant do 7 V niezależnie od VCC](https://www.ti.com/document-viewer/TLV7042/datasheet/GUID-79EBF0A6-996E-4792-AB63-E6B2C0DD1E08); nie ma tu standardowego złącza diodowego do VCC, które wymuszałoby zasilanie szyny przez TS. Nie zastępuje to próby całego układu z VIN obecnym, rozładowanym pakietem i wolnym narastaniem szyn.

## USB i przyjęta korekta R24 — PWR-A1-02

W bazowym b548 R24 jest100k do GND: reset/HiZ pozostawia Q2 OFF i może pozwolić na ładowanie bez aktualnej decyzji USB. Przyjęta korekta podłącza R24 do +3V0: **HIGH/HiZ/reset=inhibit; wyłącznie LOW=release**, nadal pod warunkiem U7/U8. GPIO i pull-up mają tę samą szynę. LOW odprowadza około30 µA; [AO3400A](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf) ma parametry przewodzenia określone przy VGS=2.5 V, poniżej poprawnej szyny3 V. Nie zmienia się funkcja pinu MCU ani interfejs IMU/Flash.

Świadomy koszt: brak ładowania przy nieuruchomionym lub niesprawnym firmware. USB nadal dostarcza SYS, więc można uruchomić/programować moduł bez naładowanej baterii. W zamian utrata sterowania GPIO nie zwalnia inhibit. To poprawka stanu domyślnego, a nie samodzielne wdrożenie USB suspend.

Budżet musi dotyczyć prądu na złączu: **Iport=prąd na BQ.IN + bezpośrednia gałąź VBUS modułu + pozostałe odbiory przed IN**, wraz z przejściami. System i ładowanie za BQ nie mogą zostać policzone drugi raz. [Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html) potwierdza regulator USB zasilany z VBUS;170 µA jest tylko typowym prądem spoczynkowym regulatora po włączeniu USBD, nie maksimum całej gałęzi podczas transferu. Nie ma dowodu, że98 mA BQ plus wszystkie pozostałe odbiory spełniają każdy limit portu przy pełnym zakresie napięcia i stanach przejściowych.

C1+C11 to6.9 µF nominalnie na VBUS, do7.59 µF z początkową tolerancją+10%. Zasilanie SYS/3V oraz układy modułu dodają obciążenia podczas startu. Nominały nie stanowią testu inrush. Nie dopisano prądu impulsowego ani gwarantowanego czasu rozruchu.

Wymagania firmware/kwalifikacji:

1. Start po VBUS z inhibit HIGH/HiZ; obsłużyć USBDETECTED, USBPWRRDY, usunięcie VBUS i sekwencję USBD producenta. LOW dopiero w dozwolonym stanie i z potwierdzonym budżetem całego portu.
2. Suspend, reset, watchdog, aktualizacja i utrata stanu hosta mają prowadzić do inhibit. Ograniczyć obciążenie SYS; /CE nie odłącza systemu ani regulatora VBUS modułu.
3. [USB-IF](https://compliance.usb.org/index.asp?UpdateFile=Electrical) określa limit suspend2.5 mA dla tego typu urządzeń; [powered-state test](https://compliance.usb.org/index.asp?Format=Standard&UpdateFile=Interoperability) obejmuje stan przed bus reset. Wyjątków dead-battery nie przyjęto bez osobnego dowodu.
4. Brak enumeracji/timeout nie oznacza DCP. Obecny PCB nie ma detekcji BC1.2 ani odczytu Rp. Automatyczna polityka host/wall adapter pozostaje otwarta. Profil adapter-only wymaga jawnie zweryfikowanego źródła i budżetu; nie wolno z samego VBUS wnioskować wyższego prądu. Przy bezpiecznym inhibit dla nieznanego źródła adapter bez danych może nie rozpocząć ładowania — jest to funkcjonalna kwestia do rozwiązania, nie ukryty tryb szybkiego ładowania.

## Pobór, termika i zaniki

**PWR-A1-07.** Nominalne odniesienia pobierają107.49 µA. Po przyjętym pull-up R24:

| Stan przy3 V | Prąd rezystorów i typowych U7/U8, bez reszty urządzenia |
|---|---:|
|HIGH/HiZ, inhibit; ALLOW LOW|około138.37 µA|
|LOW release, okno poprawne; z R3 przy SYS4.5 V|około186.09 µA|
|LOW release, ale alarm U7/U8|około168.37 µA|

LOW powoduje30 µA przez nowy R24; HIGH/HiZ usuwa ten prąd, ale ALLOW LOW nadal obciąża R22. Wartości nie są maksimami produkcyjnymi. Oczekiwane138 µA to około3.32 mAh/dobę, idealnie około90 dni dla samego bloku i300 mAh. BQ, LDO, dzielnik VBAT, MCU/IMU/Flash, upływy i samorozładowanie skracają ten czas. Kompromis jest uzasadniony dla A1 ochroną niezależną od firmware; nie jest to projekt z poborem standby pojedynczych µA. Dalszą redukcję można rozważać tylko po zachowaniu wszystkich blokad i sekwencji zasilania.

**PWR-A1-06.** C1/C3 2.2 µF/25 V, SYS10 µF oraz LDO2.2/10 µF są rzeczywistymi wyborami. Nie zatwierdzono pełnego minimum Ceff po bias, temperaturze i starzeniu; wcześniejsze typowe dane nie zastępują gwarantowanego minimum. BQ EP jest uziemiony przez dwa zewnętrzne via i0.30 mm F.Cu do In1. Brak lokalnego F.GND pour jest jawnym ograniczeniem termicznym. Próg termiczny samego BQ nie kontroluje bezpośrednio ogniwa; temperatury BQ/LDO/pakietu trzeba zmierzyć w obudowie. Nie zastosowano RθJA płytki JEDEC jako wyniku tego PCB.

**PWR-A1-08.** W [BQ pushbutton function, §6.3.8](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-326346F3-CE8C-4ED3-AD2D-0C7FDEBDEDB6) TS/MR LOW przy VIN uzbraja factory mode po typowych10 s. Zwarcie NTC może zatem po odłączeniu USB wyłączyć SYS; wyjście z tego stanu wymaga VIN. SW1 jest osobnym GPIO i nie wybudzi BQ z factory mode. Sprawdzić ten scenariusz wraz z bezpiecznym odzyskaniem sesji, bez obchodzenia alarmu NTC.

**PWR-A1-09.** U8 /RESET jest połączony z ALLOW_H, a nie resetem MCU/Flash. Minimalny próg2.5872 V leży poniżej2.7 V wymaganego przez W25Q01JV. Także nRF POF nominalnie2.8 V z tolerancją±5% może zareagować przy2.66 V. Potrzebne są wcześniejsze zakończenie zapisu według VBAT z marginesem, pomiary pod obciążeniem i dziennik odporny na nagłe odłączenie. Nie deklarować możliwości opróżnienia RAM dzięki kondensatorom. Źródła: [Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html), [Winbond W25Q01JV Rev.E §7.2, kopia dokumentu producenta w Mouser](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf) i [audyt Flash A1](flash_compatibility_A1.md).

## Warunki odbioru

Przed ładowaniem/eksploatacją rzeczywistego pakietu zamknąć specyfikację PCM/NTC i testy progów oraz prądu/napięcia ładowania. Prototyp zbadać dla przerwy/zwarcia NTC, krańców rezystancji24k/5.2k, MCU HIGH/LOW/HiZ, braku baterii, resetu w suspend, wolnych i szybkich ramp/zapadów +3V0 oraz odłączania w trakcie programowania Flash. Rejestrować jednocześnie VSYS, +3V0, TS, ALLOW_H, /CE i prądy BAT/całego USB. Osobno pełen cykl ładowania, thermal soak i standby. Wynik DRC i obliczenia statyczne nie zamykają żadnej z tych prób.
