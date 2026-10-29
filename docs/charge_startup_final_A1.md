# Ładowanie i rozruch A1 — niezależny przegląd P1/P4

Stan: **29.10.2026**, HEAD `28d88f22a6a9c0c0e1feb639546009518a6b5f8e`, PCB `cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`. Bieżący odczyt KiCad 10.0.7 porównał 19 referencji z eksportem netlisty: 0 rozbieżności i 0 opens. Nie edytowano PCB/schematu ani dokumentów współdzielonych; nie wykonano prób sprzętowych. Szczegóły i hashe: [charge_startup_final_A1.json](../reports/charge_startup_final_A1.json).

Po końcowym poszerzeniu 18 istniejących odcinków USB na In2 ponowiono ten 19-elementowy odczyt padów/netów. R24/Q2/Q1/CE i ścieżka rozruchu są niezmienione; poniższa tabela oraz decyzja P1/P4 pozostają aktualne. Nie jest to nowy test dynamicznego rozruchu.

**Decyzja dla 3–5 prototypowych PCBA:** nie wykryto błędu polaryzacji ani sprzętowego deadlocku wymagającego zmiany PCB przed zamówieniem. R24 już blokuje ładowanie w stanie HiZ. MCU może wystartować z USB przy wyłączonym ładowaniu. Trzeba doprecyzować firmware dla zawieszenia z LOW i wybudzenia z System OFF. Działanie dynamiczne, USB oraz konkretny pakiet wymagają uruchomienia i kwalifikacji; nie są tutaj uznane za sprawdzone.

## Rzeczywisty tor sterowania — CS-01

Odczytano następujące połączenia w PCB i netliście:

| Element | Połączenie |
|---|---|
| R24, 100 kΩ | CHG_INHIBIT → **+3V0**, bez pull-down do GND |
| Q2 AO3400A | gate1=CHG_INHIBIT, source2=GND, drain3=CHG_ALLOW_H |
| U7 TLV7042DGKR | wyjścia open-drain 1/7=CHG_ALLOW_H; wejścia TS/ref HOT/ref COLD, VCC8=+3V0 |
| U8 TLV803EA26DBZR | /RESET2=CHG_ALLOW_H; nadzoruje +3V0, nie resetuje MCU |
| R22/R23 | 100 kΩ z +3V0 do ALLOW; 1 MΩ z ALLOW do GND |
| Q1 AO3400A | gate1=CHG_ALLOW_H, source2=GND, drain3=CHG_CE_N |
| R3, 100 kΩ | **VSYS → CHG_CE_N** |
| BQ25185 | /CE4=CHG_CE_N; IN10=VBUS; SYS1=VSYS; BAT2=VBAT |
| TPS7A2030 | IN1 i EN3=VSYS; OUT5=+3V0 |
| MCU | U3.7=P1.14/CHG_INHIBIT; VDD28/VDDH30=+3V0 |

Przy poprawnym +3V0 HIGH lub HiZ włącza Q2, ściąga ALLOW, wyłącza Q1 i pozostawia /CE wysokie przez R3. LOW wyłącza Q2, ale U7 i U8 nadal mogą ściągać ALLOW. Dopiero zgodność wszystkich warunków pozwala Q1 obniżyć /CE. MCU nie ma przewodu wymuszającego zezwolenie wbrew oknu. AO3400A ma parametry przewodzenia określone przy VGS=2.5 V; poprawna szyna 3 V daje właściwy poziom sterowania. Nie jest to dowód zachowania tranzystorów podczas dowolnej rampy poniżej poprawnego zasilania. [AOS AO3400A](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf)

Zarzut „HiZ zwalnia ładowanie” dotyczył starego pull-down i **nie opisuje aktualnego HEAD**. [firmware_contract.md](firmware_contract.md) już poprawnie opisuje HIGH/HiZ jako inhibit. Prowadzący projekt uzupełnił także bieżący kontrakt o hang LOW, retencję System OFF oraz ograniczenie restartów watchdog. Poniższe tabele podają te rozróżnienia; nie jest potrzebne odwracanie logiki pinu. Kontrakt pozostaje wymaganiem do przyszłego firmware, a nie jego implementacją.

## Tabela stanów przy poprawnych szynach — CS-02

Wiersze opisują stany ustalone. Nie oznaczają zmierzonego braku impulsów ładowania podczas startu lub zapadu.

| MCU / źródło / czujnik | Q2 i /CE | Skutek |
|---|---|---|
| VBUS ważny, MCU HiZ, reset z zerowaniem GPIO albo brak sterującego firmware | Q2 on, /CE HIGH | Ładowanie zablokowane; IN→SYS pozostaje dostępne |
| MCU HIGH | Q2 on, /CE HIGH | Inhibit, niezależnie od poprawnego okna |
| MCU LOW, U7/U8 zwolnione | Q2 off, Q1 on, /CE LOW | Ładowanie dozwolone według BQ, z ograniczeniami prądu i stanów źródła |
| MCU LOW, alarm HOT/COLD lub reset U8 | ALLOW LOW, Q1 off, /CE HIGH | Sprzętowa blokada; LOW MCU jej nie nadpisuje |
| Program zawieszony, GPIO pozostaje HIGH | Inhibit pozostaje | Sam hang nie zmienia kierunku ani rejestru wyjściowego |
| **Program zawieszony, GPIO pozostaje LOW**, okno poprawne | Zezwolenie pozostaje | Ładowanie może trwać do rzeczywistego resetu/zmiany warunków; brak sprzętowego detektora życia MCU |
| System OFF po uprzednim ustawieniu inhibit | Q2 on | Prawidłowa sekwencja; nie zakładać samoczynnego wyzerowania GPIO |
| **System OFF / wakeup z zachowanym LOW** | LOW może pozostać do wykonania kodu | Wybudzenie jest resetem CPU, ale GPIO są zachowane; nie jest to równoważne HiZ |
| Ważne VBUS, brak baterii i NTC | Otwarte TS wywołuje blokadę | SYS może zasilać MCU; nie ma baterii do ładowania |
| Ważne VBUS, PCM odłączone, NTC poprawnie odniesiony do PACK− | Domyślnie inhibit; LOW dopiero według polityki | MCU może się uruchomić; odzyskanie pakietu zależy od specyfikacji PCM |
| VBUS usunięte, sprawna bateria powyżej BUVLO | Stan /CE nie odłącza zwykłego zasilania z baterii | BQ przechodzi do battery-only; nie ma ładowania |
| Brak VBUS oraz rozładowana/odłączona bateria lub factory mode | Brak użytecznego SYS | MCU nie startuje; potrzebne ważne zasilanie IN |

Nordic podaje PIN_CNF resetowo jako wejście bez pull, lecz tabela resetów rozróżnia źródła: power-on, brownout, pin, watchdog, soft reset i reset CPU lockup zerują GPIO; **wakeup z System OFF ich nie zeruje**. Zwykła pętla programu z LOW nie jest automatycznie CPU lockup resetem. W trybie debug także nie wolno zakładać identycznej obsługi awarii. [Nordic GPIO](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/gpio.html), [Nordic POWER, Reset behavior](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html)

### USB × bateria × MCU

USB „tak” oznacza ważne IN zdolne zasilić obciążenie. W wierszach LOW zakłada się zwolnione U7/U8; alarm sprzętowy zawsze zabrania ładowania. „Reset” w grupie HIGH/HiZ oznacza reset zerujący GPIO, po uzyskaniu poprawnych szyn. Wakeup System OFF z zachowanym LOW oraz hang LOW podlegają wierszom LOW do chwili jawnego inhibit.

| USB | BAT / PCM | MCU | SYS / +3V0 i ładowanie |
|---|---|---|---|
| Tak | Naładowana | LOW | SYS z IN; /CE LOW zezwala BQ, lecz nie wymusza stałego prądu. CV/termination i późniejszy recharge według warunków BQ. |
| Tak | Naładowana | HIGH / HiZ / reset | SYS może zasilać MCU; /CE HIGH blokuje ładowanie. |
| Tak | Niska, zgodna z dopuszczonym recovery pakietu | LOW | SYS z IN; BQ może ładować w odpowiedniej fazie, o ile wystarcza budżet i nie ma fault. |
| Tak | Niska | HIGH / HiZ / reset | **SYS może uruchomić MCU bez ładowania baterii**; nie czeka na wzrost VBAT. |
| Tak | PCM-open | LOW | SYS z IN. Możliwe charge-assisted recovery tylko dla zgodnego PCM/NTC; nie jest gwarantowane dla dowolnego pakietu. |
| Tak | PCM-open | HIGH / HiZ / reset | SYS z IN; MCU startuje bez konieczności odzyskania pakietu, ładowanie pozostaje zablokowane. |
| Nie | Naładowana, normalny tryb BQ | LOW / HIGH / HiZ / reset | SYS z BAT; brak ładowania dla każdego stanu MCU. Ważność +3V0 zależy od napięcia i obciążenia. |
| Nie | Niska, jeszcze powyżej BUVLO | LOW / HIGH / HiZ / reset | Możliwe SYS z BAT, ale poprawne +3V0 nie jest zapewnione przy granicy/dropout. Brak ładowania. Nie przypisywać Q2 stanu ON/OFF, jeśli szyna nie jest poprawna. |
| Nie | Za niska, poniżej BUVLO / pakiet odcięty | LOW / HIGH / HiZ / reset żądany | Brak gwarantowanego SYS i poprawnych poziomów logicznych; nie ma działającego MCU ani określonego stanu Q2. Potrzebne ważne IN. |
| Nie | PCM-open | LOW / HIGH / HiZ / reset żądany | Brak użytecznej drogi z BAT do SYS; MCU i jego żądany stan nie mają ważności bez zasilania. |

Tabela dotyczy normalnego trybu BQ. W factory mode SYS może być wyłączone także przy naładowanej baterii. Termination wymaga dominującej pętli CV i spełnienia pozostałych warunków; aktywne DPPM/VINDPM lub thermal regulation może je opóźniać. [TI §6.1.1.5](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-B926C400-1BF7-47AF-B78B-C33124DDFE3D)

## USB, pusta bateria i PCM — CS-03

TI opisuje zasilanie SYS z IN również przy pustej baterii; prąd systemu ma pierwszeństwo przed ładowaniem. /CE wyłącza ładowanie przez BATFET, podczas gdy supplement działa niezależnie. W połączeniu z EN LDO podłączonym na stałe do SYS daje to drogę **VBUS→BQ SYS→LDO→MCU bez wcześniejszego LOW na CHG_INHIBIT**. Nie ma cyklicznej zależności „ładowanie potrzebne do uruchomienia MCU, MCU potrzebne do ładowania”. Dla braku baterii lub otwartego toru PCM jest to wniosek z tej topologii, a nie wykonany test startu. [TI BQ25185 §6.1](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-F2E2312A-E20A-42CA-9CF8-12D968292ACC), [§6.1.1](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-700B7F6C-B49B-4E66-958F-2A03B14355EA)

Warunki: ważne IN, poprawne R1/R2, brak zwarcia SYS i obciążenie mieszczące się w rzeczywistym budżecie. Bateria odłączona nie uzupełni impulsu obciążenia. Nastawa ILIM100 ma 80/90/98 mA przy warunkach tabeli TI; dla startu bez baterii trzeba zmierzyć rampy, inrush i najgorszy pobór. Firmware ma zaczynać od małego obciążenia, bez oczekiwania na skasowanie Flash lub intensywnego BLE jako warunku uruchomienia obsługi ładowania. Zanik +3V0 i ponawiane restarty są możliwym wynikiem przeciążenia do rozstrzygnięcia podczas uruchomienia. [TI DPPM](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-DE20B6E0-9164-469A-B63E-10EDCEDAFC8D), [parametry elektryczne BQ25185](https://www.ti.com/lit/ds/symlink/bq25185.pdf)

Bez działającego kodu urządzenie może być zasilane i programowane przez SWD, ale nie obiecuje autonomicznego ładowania. „Brak firmware” oznacza brak kodu sterującego pinem; błędny program aktywnie wymuszający LOW należy analizować jak hang LOW.

0 V na zaciskach chronionego pakietu, niskie napięcie sprawnego ogniwa i uszkodzone ogniwo rozładowane do 0 V to różne przypadki. BQ ma tryby małego prądu dla niskiego VBAT, ale nie dopuszcza to regenerowania dowolnego uszkodzonego Li-Po. Recovery PCM wymaga danych jego producenta: czy i jak ponownie dopuszcza prąd po przyłożeniu ładowarki. NTC musi zachować poprawną rezystancję do **PACK−** również przy odłączonym PCM. Jeśli dostawca odnosi go do odłączonego wewnętrznego B−, okno może pozostać w alarmie i zablokować odzyskanie pakietu. To potencjalna niezgodność **pakietu/wiązki**, a nie dowiedziony błąd samej PCBA. Nie obchodzić PCM ani okna temperatury.

Firmware nie może czekać z pierwszym zezwoleniem na osiągnięcie „zdrowego” VBAT wyłącznie wskutek ładowania, które sam blokuje. Recovery ma być odrębną, dozwoloną przez producenta pakietu ścieżką, przy uprawnionym źródle i działającym sprzętowym oknie.

## NTC i factory mode — CS-04/05

Zwarcie TS blokuje ładowanie, lecz TS/MR pełni również funkcję wejścia factory mode: utrzymanie LOW przy IN uzbraja ten tryb po typowych 10 s, a następnie usunięcie IN może wyłączyć SYS. Ważne IN wybudza BQ; przycisk nie może go wybudzić. SW1 na tej PCB jest osobnym GPIO MCU. Po usunięciu zwarcia należy przywrócić zasilanie USB; firmware ani SW1 nie wybudzą pozbawionego zasilania MCU. Nie resetować okresowo /CE w celu obchodzenia alarmu lub timera. [TI §6.3.8](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-326346F3-CE8C-4ED3-AD2D-0C7FDEBDEDB6)

Przerwa NTC powoduje wzrost TS i blokadę COLD; zwarcie powoduje HOT/manual-reset. W adapter mode TS jest mierzone, w battery-only/factory nie jest aktywne. NTC_TS nie ma połączenia z ADC MCU. Obecny tor chroni ładowanie; **nie zapewnia pomiaru temperatury ogniwa w firmware ani termicznego odcięcia rozładowania na podstawie NTC**. Nie utożsamiać temperatury IMU z temperaturą ogniwa. [TI TS](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-280153BD-C63E-49AE-A394-DC5C2FF07171), [tryby BQ](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-0FDC3E18-D31F-471E-BD0C-B4C23AD9F27C)

Pakiet 1S 4.2 V, docelowo 300 mAh, wymaga własnego PCM, dozwolonego prądu ładowania, danych recovery i NTC zamocowanego na ogniwie. Kandydat Semitec 103AT-2 ma 10 kΩ±1%, B25/85=3435 K±1%; termiczny czas około 15 s dotyczy pomiaru w powietrzu. Nie stanowi specyfikacji gotowego pakietu. Przyjęte kryteria R(0°C)≥24 kΩ i R(45°C)≤5.20 kΩ obejmują cały montaż; potrzebne są dane R(T), dryftu i kontaktu termicznego. [Semitec AT](https://www.semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf)

Statyczny model progów, jego założony dodatkowy błąd komparatora i niezweryfikowane rampy pozostają warunkowe, zgodnie z [power_audit_A1.md, PWR-A1-04](power_audit_A1.md). BQ nie zastępuje PCM pakietu, a jego termika nie jest termiką ogniwa. Brak MPN pakietu jest brakującą pozycją BOM **zespołu końcowego**; nie dowodzi błędu połączeń lub footprintu PCBA. Na początku uruchamiać płytkę z ograniczonym źródłem i symulatorem baterii/NTC, przed podłączeniem rzeczywistego ogniwa.

## Minimalne doprecyzowanie firmware — CS-06

1. W najwcześniejszym kodzie aplikacji i bootloadera wymusić inhibit: najpierw ustawić latch wyjścia HIGH, potem skonfigurować pin; HiZ bez pull-down również pozostawia R24 aktywne. P1.14 nie może zostać przejęte przez inną funkcję.
2. **Przed każdym System OFF** jawnie HIGH/HiZ; po każdym wejściu w kod ponownie inhibit, bez zakładania resetu GPIO. LOW nie jest dozwolonym stanem oszczędzania energii.
3. Przed pierwszym LOW uruchomić WDT. Nie karmić go bezwarunkowo z przerwania, jeśli główna polityka USB/ładowania nie działa. Skonfigurować liczenie podczas wymaganych stanów snu/halt; WDT w System OFF nie zastępuje punktu 2. Timeout prowadzi do resetu GPIO, ale nie jest dowodem spełnienia wszystkich terminów USB suspend. [Nordic WDT](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/wdt.html)
4. LOW dopiero przy uprawnionym źródle i sprawdzonym budżecie całego portu; suspend, utrata stanu USB i procedury błędu mają wracać do inhibit. Sam VBUS, timeout enumeracji ani samo Rd nie identyfikują DCP. Zachować istniejący zakaz PWM /CE i okresowego restartowania timera.
5. Obsługę bezpiecznego ładowania/recovery odseparować od gotowości sterownika Flash i akwizycji IMU. Odczyty STAT nie są niezależnym pomiarem NTC ani pewnym detektorem obecności pakietu; zewnętrzny inhibit może wyglądać jak zwykłe charge-disabled.

6. Nie stosować automatycznej sekwencji „WDT reset → ponownie LOW → awaria → WDT reset” bez ograniczenia prób i oceny przyczyny. Powrót /CE HIGH po resecie i następny LOW może kasować safety timer; BQ nie ogranicza wtedy samodzielnie łącznego czasu wielu restartów. Po watchdog/brownout/restartach pozostawić inhibit, odczytać powód resetu i zastosować ograniczoną politykę odzyskiwania z zatrzaskiem błędu zamiast bezterminowego ponawiania ładowania. Nie używać restartów jako sposobu ładowania 500 mAh przy niskim ILIM. [TI safety timer](https://www.ti.com/document-viewer/BQ25185/datasheet/GUID-F91448CC-01A7-4312-A893-4B2E9FC88D89)

Są to wymagania do implementacji i fault-injection. W repozytorium nadal nie ma uruchomionego firmware potwierdzającego ich wykonanie.

## A/B/C i rozstrzygnięcie

| Klasa | Wynik dla tego przeglądu |
|---|---|
| **A — przed zamówieniem PCB** | Nie znaleziono nowego błędu R24/Q2/Q1/CE ani nieusuwalnego firmwarem deadlocku zasilania. Nie ma wskazania do przełączenia R24 z powrotem do GND lub obchodzenia U7/U8. Zachować wymóg chronionego pakietu i NTC. |
| **B — uruchomienie, obowiązkowo przed ładowaniem realnego ogniwa** | Zmierzyć start USB z baterią odłączoną, symulatorem niskiego VBAT i modelem PCM-open; rampy/CE/BAT current; inrush/cały USB; hang LOW, WDT, System OFF i wakeup; NTC przerwa/zwarcie oraz factory recovery. Zakwalifikować pakiet/wiązki, progi i dynamikę temperatury, pełny cykl/timer oraz termikę obudowy. Brak takich prób nie jest wynikiem PASS ani samodzielnym zakazem wykonania kontrolowanych prototypów. |
| **C — następna rewizja, o ile nowy wymóg to uzasadnia** | Redukcja około 138 µA, odczyt temperatury ogniwa przez MCU, ewentualne niezależne sprzętowe zezwolenie o ograniczonym czasie dla wymagania „każdy hang natychmiast zabrania ładowania”. Obecny układ nie ma takiego detektora życia. |

**Rozstrzygnięcie:** self-start z USB nie wymaga uprzedniego włączenia ładowania. Brak autonomicznego ładowania bez firmware jest świadomą funkcją obecnej polaryzacji, a nie sprzętowym deadlockiem. Hang LOW oraz zachowanie GPIO przy System OFF wymagają jawnej polityki i prób firmware. Niezgodny PCM/NTC może uniemożliwić odzyskanie konkretnego pakietu, dlatego dobór pakietu pozostaje bramką zespołu końcowego. Nie stwierdzono konieczności nowej rewizji PCB przed 3–5 kontrolowanymi prototypami w zakresie P1/P4; nie jest to zatwierdzenie gotowego urządzenia do użycia na ciele lub ładowania niezakwalifikowanego ogniwa.
