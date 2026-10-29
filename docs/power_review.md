# Weryfikacja zasilania — 27.10.2026

Status: dane do schematu; **dodatkowy sprzętowy komparator temperatury i nadzór napięcia wdrożono w roboczym schemacie**. Dobór pakietu i próby są wymagane przed zwolnieniem do produkcji. Nie przeprowadzono prób sprzętowych.

## Ładowarka

Źródło: [TI BQ25185, SLUSF65B, sierpień 2026](https://www.ti.com/lit/ds/symlink/bq25185.pdf), tabela 4-1, 6-1 i sekcje 6.1.1.4, 6.3.9, 7.2.2.

Sprawdzony pinout BQ25185DLHR, WSON-DLH 2.2 × 2.0 mm:

| Pad | Sygnał |
|---|---|
| 1 | SYS |
| 2 | BAT |
| 3 | STAT2 |
| 4 | /CE |
| 5 | GND |
| 6 | TS/MR |
| 7 | ILIM/VSET |
| 8 | ISET |
| 9 | STAT1 |
| 10 | IN |
| 11, exposed pad | GND |

Dane: 24 kΩ ustawia 4.2 V/100 mA; 18 kΩ: 4.2 V/500 mA. ICHG = 300 AΩ / RISET. Propozycja RISET=2.00 kΩ 1%: 150 mA nominalnie, ograniczane dostępnym prądem wejścia. CIN≥1 µF efektywnie, CSYS nominalnie10 µF, CBAT≥1 µF. SYS≈4.5 V przy USB. STAT1/2: open-drain, pullup1–20 kΩ. Timer ładowania360 min. TS:38 µA typ,36.5–39.5 µA; HOT0.105–0.125 V, COLD0.9575–1.0575 V. Factory mode: powrót przez VIN.

Proponowane połączenia: USB5V→IN; BAT→chroniony pakiet1S; SYS→LDO3V; kondensatory przy pinach; EP bezpośrednio do GND i płaszczyzny przez przelotki. /CE powinno umożliwiać firmware wyłączenie ładowania. Nie łączyć przycisku użytkownika z TS/MR — oddzielny GPIO pozwala wybudzać bez USB.

## Regulator3V

Źródło: [TI TPS7A20, SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), strony4–7. Wybrany wariant **TPS7A2030PDBVR**, SOT23-5:1IN,2GND,3EN,4NC,5OUT. ZakresIN1.6–6.0 V;300 mA; IQ6.5 µA typ; dropout145 mV max przy300 mA dla DBV; szum7 µVrms w podanych warunkach TI. CIN nominal1 µF, eff≥0.47 µF; COUT1–200 µF, eff≥0.47 µF; ESR≤100 mΩ. EN high≥0.9 V. Wyjście rozładowuje się po disable.

Aktualny draft: CIN2.2 µF/16V X5R przy IN; COUT10 µF/10V X5R przy OUT; EN do SYS dla pracy ciągłej. Dodatkowe100 nF przy każdym układzie i osobne4.7 µF przy Flash. Wszystkie dobrane MLCC muszą zachować wymaganą pojemność po DC-bias, temperaturze i starzeniu. Ładowarkowy CSYS10 µF nie zastępuje lokalnego CIN LDO, jeśli ścieżka nie jest krótka.

[TPS7A02](https://www.ti.com/lit/ds/symlink/tps7a02.pdf) jest poprawnym alternatywnym LDO200 mA o25 nA IQ, lecz nie jest preferowany do wymagania niskiego szumu:130 µVrms w podanych warunkach TI. TPS7A20 daje większy zapas prądu i lepsze parametry szumowe kosztem prądu spoczynkowego.

Wniosek projektowy: próg zatrzymania zapisu powinien leżeć nad spadkiem zasilania Flash (jego minimalne napięcie2.7 V musi uwzględniać tolerancje i impulsy zapisu). Odczyt baterii przez dzielnik z filtrem i firmware POF/BOR są potrzebne, ale nie zastępują dziennika odpornego na nagłe odłączenie.

## Temperatura — wykryty problem

Nie wolno opisać bezpośredniego NTC10 kΩ/B3435 jako ochrony0–45°C. Własne obliczenie z prądu i progów podanych wyżej, przy modelu beta:

`R(T)=R25*exp(B*(1/(T+273.15)-1/298.15))`

| NTC, bez tolerancji samego NTC | Typ cold-stop | Typ hot-stop | Najniższy cold-stop z tolerancji IC | Najwyższy hot-stop z tolerancji IC |
|---|---:|---:|---:|---:|
|10 kΩ/B3435|1.7°C|59.5°C|−0.2°C|63.7°C|
|6.8 kΩ/B4250|−1.0°C|43.0°C|−2.5°C|46.0°C|

Corner cold: VCOLDmax/ITSMRmin. Corner hot: VHOTmin/ITSMRmax. Następnie trzeba dodać tolerancje R25, B, rzeczywistą tabelęR(T), przewody i gradient termiczny. Dane w tabeli nie są gwarancją zakresu.

[TI SPVA059, projektowanie sieci TS](https://www.ti.com/lit/an/spva059/spva059.pdf) opisuje dobór rezystorów kompensacyjnych. Dla powyższego okna zwykła dodatnia rezystancja szeregowa/równoległa z NTC nie zawęzi zakresu do0–45°C: wymagany stosunek rezystancji progów jest większy niż stosunekNTC(0°C)/NTC(45°C).

Rozwiązanie przyjęte w A0: dodatkowy niezależny komparator okienkowy opisany poniżej, z uwzględnieniem tolerancji i nadzoru napięcia. Sam TS ładowarki pozostaje ochroną dodatkową. Konkretny pakiet z PCM, dopuszczalnym prądem i potwierdzoną charakterystyką NTC nadal wymaga wyboru i kwalifikacji.

## USB-C i ograniczenie prądu

Źródła: [Renesas: USB Type-C i role](https://www.renesas.com/en/support/engineer-school/usb-power-delivery-03), [USB-IF: testy Type-C](https://www.usb.org/sites/default/files/USB%20Type%20C%20Functional%20Test%20Specification%202021%2005%2020.pdf), [TI: ESD portu USB-C](https://www.ti.com/document-viewer/lit/html/SSZTAL6).

SinkUSB2: osobne5.1 kΩ1% z CC1 i CC2 do GND; nie zwierać CC. Połączyć zdublowane D+ i D− przy złączu. Wszystkie VBUS razem; wszystkie GND do płaszczyzny. SBU pozostają NC. Ochrona ESD blisko złącza. Rd nie negocjująUSB-PD ani nie przyznają automatycznie500 mA. UrządzenieUSB2 przed konfiguracją ma domyślny budżet100 mA.

WybórILIM100 mA jest świadomie zachowawczy dla źródeł domyślnych. Prąd ładowania będzie niższy od150 mA i zmienny z obciążeniem. Dla500 mAh może zabraknąć czasu do upływu timera360 min; wymagane próby. Aby zagwarantować szybsze ładowanie, potrzebna detekcjaRp/BC1.2 lub konfiguracjaUSB i sprzętowe przełączanieILIM z zachowaniem4.2 V. ObsługaUSB suspend również wymaga dopracowania sprzętu/firmware — samo /CE blokuje ładowanie, a nie obciążenieSYS.

## Próby fizyczne

- Przejścia USB↔bateria z zapisem Flash, pomiar minimów3V oscyloskopem.
- Cały cykl CC/CV i timeout dla500 mAh przyILIM100 mA; test bez baterii.
- Wstrzykiwanie rezystancjiTS: hot,cold,przerwa,zwarcie; powtórzenie na granicach tolerancji.
- Temperatura obudowy, baterii, LDO i ładowarki w zamkniętej obudowie. Wstępnie przy5V,VBAT3V i faktycznymIBAT80 mA strata ładowarki jest rzędu0.16 W plus torSYS. Wynik zależy odPCB i nie stanowi pomiaru.
- Pomiary poboru w USB-suspend, system-off, rejestracji i transferzeBLE.
- Odłączenie baterii/zasilania podczas programowania i kasowaniaFlash; weryfikacja odzyskania sesji.

StatusJLC dlaTPS7A2030PDBVR/C963429 przekazał agent główny; nie był niezależnie potwierdzany w tym przeglądzie. Nie wpisywać tej adnotacji jako dowodu aktualnego magazynu.

## Ostateczny obwód temperatury A0 i wynik przeglądu

Sprawdzono aktualne `hardware/design.json`: U7, U8, Q1, Q2, R3 i R18–R24 mają opisane poniżej połączenia. Topologia odcina możliwość nadpisania ochrony przez wyjście MCU. Nie przeprowadzono prób sprzętowych ani symulacji rozruchu.

### Komparatory i odniesienia

**U7: TLV7042DGKR**, VSSOP-8, dwa wyjścia open-drain. [Oficjalna dokumentacja TI, SLVSE13J](https://www.ti.com/lit/gpn/TLV7042), tabela 4-2 i 5.9. Pinout: 1 OUTA, 2 INA−, 3 INA+, 4 GND, 5 INB+, 6 INB−, 7 OUTB, 8 VCC. Zasilanie +3V0, lokalne C18 100 nF. Offset ±8 mV, histereza 3–25 mV. TLV7032 ma wyjścia push-pull i nie jest zamiennikiem w tym połączeniu. [LCSC C2760466](https://www.lcsc.com/product-detail/comparators_texas-instruments-tlv7042dgkr_C2760466.html) potwierdza oznaczenie; zakup i magazyn JLC pozostają do potwierdzenia.

| Funkcja | Połączenie |
|---|---|
| HOT | INA+ = NTC_TS; INA− = NTC_REF_HOT |
| COLD | INB+ = NTC_REF_COLD; INB− = NTC_TS |
| NTC_REF_HOT | +3V0 → R18 100 kΩ 0.1% → REF → R19 10.0 kΩ 0.1% → GND; nominalnie 0.27273 V |
| NTC_REF_COLD | +3V0 → R20 27.4 kΩ 0.1% → REF → R21 10.0 kΩ 0.1% → GND; nominalnie 0.80214 V |
| CHG_ALLOW_H | OUTA + OUTB + /RESET U8 + dren Q2; R22 100 kΩ do +3V0 i R23 1 MΩ do GND |
| Q1 | bramka CHG_ALLOW_H, źródło GND, dren CHG_CE_N; R3 100 kΩ z CHG_CE_N do VSYS |
| Q2 | bramka CHG_INHIBIT z MCU, R24 100 kΩ z bramki do GND; źródło GND, dren CHG_ALLOW_H |

Q1 i Q2: **AO3400A**, [dokumentacja AOS](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf), SOT-23: 1 G, 2 S, 3 D. RDS(on) ≤48 mΩ przy VGS = 2.5 V. [LCSC C20917](https://lcsc.com/product-detail/MOSFET_Alpha-Omega-Semicon_AO3400A_Alpha-Omega-Semicon-AOS-AO3400A_C20917.html). Prąd drenu Q1 jest rzędu 45 µA przy VSYS = 4.5 V; Q2 odprowadza około 30 µA.

**CHG_INHIBIT jest aktywny HIGH:** MCU HIGH włącza Q2 i blokuje ładowanie. MCU LOW albo HiZ pozwala działać sprzętowemu oknu. HIGH MCU nie może wymusić HIGH na CHG_ALLOW_H, gdy U7 lub U8 wymusza LOW. Nie zastosowano diody Schottky do ściągania bramki, ponieważ suma maksymalnego VOL MCU i VF diody dawała zbyt mały zapas wyłączenia Q1.

### Nadzór napięcia i opóźnienie zezwolenia

**U8: TLV803EA26DBZR**, [dokumentacja TI SLVSES2J](https://www.ti.com/lit/ds/symlink/tlv803e.pdf), **1 GND, 2 /RESET, 3 VDD**. To wariant bez dodatkowego oznaczenia pinoutu „R” przed DBZ; końcowe R oznacza taśmę. /RESET łączy się bezpośrednio z CHG_ALLOW_H; VDD z +3V0, C19 100 nF do GND. [JLC C1852119](https://jlcpcb.com/partdetail/TexasInstruments-TLV803EA26DBZR/C1852119) potwierdza właściwy układ i montaż SMT.

Dane TI: próg 2.64 V ±2% maksymalnie, czyli 2.5872–2.6928 V; histereza 0.9–1.5%; czas zwolnienia resetu 130–270 ms, nominalnie 200 ms; stan LOW określony od VDD = 0.7 V przy podanym obciążeniu. Opóźnienie reakcji na spadek pod próg do 50 µs w warunkach TI. Maksymalny próg ponownego zwolnienia jest niższy od minimalnej poprawnej szyny 2.955 V.

U8 utrzymuje blokadę w czasie POR komparatorów: TLV704x sam ma wtedy wyjścia HiZ. R18 zmieniono z 115 kΩ na 100 kΩ, ponieważ odniesienie HOT musi pozostawać bezpieczne także przy spadku +3V0 do najniższego progu U8, a nie tylko w tolerancji regulacji LDO. Testy szybkiego zapadu i napięcia poniżej 0.7 V pozostają wymagane; nie deklarujemy idealnej reakcji bez opóźnienia.

### NTC i obliczenia narożników

Kandydat pakietu: **Semitec 103AT-2**, 10 kΩ ±1%, B25/85 = 3435 K ±1%, [oficjalna dokumentacja Semitec](https://www.semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf). NTC ma być termicznie sprzężony z ogniwem, zaizolowany i odciążony mechanicznie. Nie wolno zastępować go stałym rezystorem ani dodawać równoległego rezystora 10 kΩ.

Odtwarzalne obliczenia: `python3 scripts/check_charge_temperature.py`. Skrypt przyjmuje niezależne ±0.5% dla każdego rezystora odniesienia: początkowe 0.1% + TCR do 50 ppm/K ×65 K =0.425%, zaokrąglone z zapasem. Wymagane są części o TCR ≤50 ppm/K i początkowej tolerancji 0.1%; nie zastępować ich dowolnym rezystorem 0.5%. Uwzględnia także I_TS 36.5–39.5 µA, ±8 mV offsetu, ±12.5 mV połowy maksymalnej histerezy oraz dodatkowe ±1.5 mV. Model NTC konserwatywnie zmienia zarówno R25, jak i B o ±3%.

| Zakres odniesienia | HOT — granice progu modelu beta | COLD — granice progu modelu beta |
|---|---:|---:|
| Poprawna szyna 2.955–3.045 V | 29.11–39.27°C | 3.55–10.02°C |
| Cały zakres przed zadziałaniem U8: 2.5872–3.045 V | 29.11–43.60°C | 3.55–13.16°C |

To granice między egzemplarzami i kierunkami zmian, nie gwarantowana dokładność pomiaru temperatury. Model beta nie zastępuje tabeli R(T). Przy odbiorze pakietu wymagamy monotonicznej charakterystyki oraz **R(0°C) ≥24.0 kΩ i R(45°C) ≤5.20 kΩ**, łącznie z tolerancjami, przewodami i starzeniem. Z obliczeń elektrycznych potrzeba odpowiednio >23.073 kΩ i <5.344 kΩ. Te warunki pozwalają sprawdzić blokadę w 0°C i 45°C bez idealnego modelu beta. Semitec podaje nominalne R(0°C) =27.28 kΩ; R(45°C) i cały budżet tolerancji musi potwierdzić dostawca/pomiar.

Przy R22 100 kΩ i R23 1 MΩ minimalny CHG_ALLOW_H wynosi około 2.68 V przed uwzględnieniem upływów. Łączny upływ U7, U8, Q1, Q2 i PCB musi zachować zapas do 2.5 V; obliczeniowy budżet prądu upływu do GND wynosi około 1.5 µA. TI podaje dla U8 do 350 nA. Prądy upływu tranzystorów i zabrudzeń PCB przy wysokiej temperaturze wymagają sprawdzenia. Za mały poziom HIGH spowodowałby brak zezwolenia na ładowanie; nie należy traktować typowych upływów jako gwarantowanych maksimów.

### Stany ustalone, back-power i pobór

| Stan | Wynik |
|---|---|
| USB, poprawne napięcie, NTC w oknie, CHG_INHIBIT LOW/HiZ | U7 i U8 HiZ, Q2 off; CHG_ALLOW_H wysoki; Q1 on; /CE niski |
| HOT/COLD, zwarcie/przerwa NTC | Co najmniej jedno wyjście U7 niskie; Q1 off; /CE wysoki |
| CHG_INHIBIT HIGH | Q2 on; CHG_ALLOW_H niski; /CE wysoki niezależnie od okna |
| Rozruch/spadek napięcia w zakresie działania U8 | U8 wymusza LOW i blokuje zezwolenie |
| Brak +3V0, obecne VSYS | R23 sprowadza bramkę Q1 do GND, R3 ustawia /CE wysoko |
| Battery-only | Pomiar TS w BQ nieaktywny; z podłączonym NTC oczekiwany TS blisko 0 V; HOT output LOW. Blokada /CE nie przerywa BAT→SYS |

[BQ25185, tabela 6.4](https://www.ti.com/lit/ds/symlink/bq25185.pdf) potwierdza wyłączenie pomiaru TS w battery-only i factory mode. Dokładny prąd upływu nieaktywnego TS nie jest podany, więc jego stan należy zmierzyć. [TLV7042, sekcja 6.4.1](https://www.ti.com/lit/gpn/TLV7042) potwierdza izolację VCC od wejść również przy VCC =0; dodatni TS nie powinien zasilać +3V0 przez wejście U7. Aktualny TS nie jest połączony z ADC MCU.

Dzielniki R18/R19 i R20/R21 pobierają nominalnie 27.27 +80.21 ≈107.5 µA. Jeśli U7 blokuje ładowanie w battery-only, R22 dodaje około 30 µA. Aktualny blok ma więc **około 138 µA** stałego poboru, plus małe prądy U7/U8. Poprzednie przybliżenie 134 µA dotyczyło wcześniejszego R18 =115 kΩ. Dla 300 mAh i samego tego bloku idealny czas wynosi około 90 dni; pełne urządzenie będzie miało krótszy czas. To budżet obliczeniowy, nie pomiar ani deklaracja żywotności baterii.

### Pozostałe próby przed zwolnieniem projektu

- USB z baterią podłączoną i odłączoną; wolne i szybkie narastanie +3V0 oraz gwałtowny zapad poniżej progu U8.
- Równoczesny pomiar VSYS, +3V0, TS, CHG_ALLOW_H, /CE i prądu BAT dla HOT/COLD, przerwy i zwarcia NTC.
- Sprawdzenie poniżej 0.7 V, w czasie maksymalnego opóźnienia U8 i dla gorącego PCB. Limity statyczne nie obejmują dowolnie szybkiego zapadu.
- MCU reset/HiZ, LOW i HIGH; potwierdzenie, że żaden stan MCU nie nadpisuje U7/U8. Pomiar minimalnego HIGH na CHG_ALLOW_H i upływów.
- Pobór battery-only oraz factory mode; rozruch USB po fabrycznym odłączeniu SYS. Firmware nie może używać factory mode, jeśli wymagane jest budzenie samym przyciskiem.
- Kwalifikacja rzeczywistego pakietu, jego R(T), opóźnienia termicznego, prądu i pełnego cyklu ładowania.

Nie uznajemy cyklicznego resetowania timera za rozwiązanie ograniczenia 500 mAh/ILIM 100 mA. Przejście na 500 mA wymaga wcześniej potwierdzonego uprawnienia źródła i odpowiedniego sterowania ILIM; sama obecność VBUS lub odbiór dowolnej ramki USB tego nie przyznaje.

**Wynik:** aktualne połączenia realizują niezależne sprzętowe zezwolenie temperaturowe, blokadę podczas niepoprawnego zasilania i odseparowany inhibit MCU. Obliczenia statyczne przechodzą przy opisanej specyfikacji NTC. Weryfikacja dynamiczna, cieplna i pomiary pozostają otwarte; przegląd nie jest zatwierdzeniem do produkcji.
