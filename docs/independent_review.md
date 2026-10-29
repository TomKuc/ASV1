# Niezależny przegląd schematu A0

Data: 2026-10-27. Końcowy przegląd obejmuje zregenerowany `hardware/design.json` z **71 elementami**, `docs/architecture.md`, definicje symboli i połączeń w `scripts/build_design.py` oraz obliczenia `scripts/check_charge_temperature.py`. Nie edytowano generatora. To przegląd elektryczny danych projektu, **nie KiCad ERC/DRC, SPICE ani próba sprzętowa**.

## Wynik

Przypisania pinów MCU/IMU nie wykazują konfliktu funkcji. Okno NTC ma poprawną polaryzację statyczną. W końcowym drafcie zweryfikowano dodanie U8, Q2 i R24 oraz zmianę R22 i R18: usuwają wykryte bezpośrednie wymuszenie przez GPIO i dodają sprzętowy warunek poprawnego zasilania. Rozruch, brownout i działanie rzeczywistego pakietu nadal wymagają pomiarów. Pobór toru NTC w battery-only pozostaje istotnym ograniczeniem.

| ID | Znaczenie | Ustalenie w sprawdzonym wariancie | Status |
|---|---|---|---|
| IR-01 | Rozruch i brownout | U8 TLV803EA26DBZR, /RESET→ALLOW_H, dodany i zweryfikowany w JSON | Korekta połączeń sprawdzona; próby dynamiczne otwarte |
| IR-02 | Niezależność od stanu GPIO | Q2 odseparowuje GPIO MCU od ALLOW_H; HIGH wyłącznie blokuje | Zamknięty w przeglądzie połączeń; test stanów MCU otwarty |
| IR-03 | Istotne dla czasu pracy | R22=100k zmniejsza prąd; aktualny tor NTC około138 µA w battery-only | Udokumentowane ograniczenie; pomiar otwarty |
| IR-04 | Dokumentacja produkcyjna | Brak zweryfikowanej geometrii padów/keepout Raytac | Otwarty |
| IR-05 | Dokumentacja referencyjna | DCCH31 NC ma potwierdzenie wsparcia Nordic; nadal brak oględzin Raytac §8.3 | Częściowo zamknięty |
| IR-06 | USB | Suspend/inrush i CC/VBUS ESD pozostają bez ukończonej implementacji/oceny | Otwarty, już zgłoszony w dokumentacji |

## IR-01: rozruch i brownout okna NTC

[TI TLV7042, SLVSE13J §6.4 i §5.10](https://www.ti.com/lit/gpn/TLV7042) określa HiZ wyjść podczas POR i czas ustalenia po osiągnięciu minimalnego zasilania. Bez dodatkowego nadzoru pull-up może podnieść bramkę Q1 przed uzyskaniem wiarygodnego wyniku porównania. Sam R23=1M zapewnia rozładowanie przy rzeczywistym braku szyny3V; nie wymusza blokady całego przedziału narastania/opadania szyny.

Korekta wdrożona: U8 **TLV803EA26DBZR** ma 1GND,2/RESET→CHG_ALLOW_H,3VDD→+3V0 oraz C19. [TI SLVSES2J](https://www.ti.com/lit/ds/symlink/tlv803e.pdf) potwierdza wariant open-drain active-low; dokładne oznaczenie ma właściwy pinout DBZ. U8 nadzoruje próg2.64V i zwalnia zezwolenie po opóźnieniu. Zakres dokładności/reakcji opisuje `docs/power_review.md`; poniżej0.7V i przy szybkich zapadach nie deklarujemy gwarancji nieobejmowanej dokumentacją.

Połączenia usuwają brak sprzętowego warunku rozruchu w zakresie działania U8. Próby wolnego/szybkiego startu i brownout pozostają otwarte. Zmieniony R18=100k zapewnia zachowawcze odniesienie HOT również dla2.5872V, przed najniższym progiem U8; uwzględniono to w obliczeniach narożników.

## IR-02: wymuszenie przez GPIO

W końcowym JSON U3 pin7/P1.14 łączy się z **CHG_INHIBIT**, bramką Q2; R24=100k doGND. Q2 AO3400A ma1G=CHG_INHIBIT,2S=GND,3D=CHG_ALLOW_H. MCU HIGH włączaQ2 i blokuje; LOW/HiZ wyłączaQ2 i pozostawia decyzję U7/U8. Nie ma już przewodu umożliwiającego MCU wymuszenieHIGH naALLOW_H.

Zweryfikowano połączeniaQ2 i brak zamianyS/D. Nie zastosowano diody Schottky. Należy fizycznie potwierdzićLOW/HIGH/HiZ MCU oraz poziomyALLOW_H i/CE; obecny przegląd zamyka błąd topologii, nie zastępuje tych prób.

## IR-03: pobór w battery-only

[TI BQ25185, SLUSF65B §6.4](https://www.ti.com/lit/ds/symlink/bq25185.pdf) oznacza pomiar TS jako nieaktywny w battery-only. Przy fizycznym NTC do GND, bez innego źródła polaryzacji, oczekiwany TS pozostaje blisko0V. U7 kanałHOT trzymaALLOW_H nisko, więc aktualnyR22=100k pobiera około30µA. Dokładny stan i upływ nieaktywnegoTS wymagają pomiaru. Dzielniki odniesienia są stale zasilane.

Własne obliczenia dla3V, bez prądów układów i bez reszty PCB:

| Stan | Wzór | Prąd |
|---|---|---:|
| Okno poprawne, U7/U8 HiZ, Q2 off |3/110k +3/37.4k +3/1.1M |110.21 µA|
| Battery-only, HOT LOW, aktualne R18=100k/R22=100k |3/110k +3/37.4k +3/100k |137.49 µA|

Są to wartości nominalne samych rezystorów, bezprądówIC iresztyPCB; po dodaniuU7/U8 budżet toru temperatury wynosiokoło138µA. Nie używać wcześniejszych106/134/404µA jako danych aktualnej rewizji. Docelowe zasilanie toru tylko podczas USB może zmniejszyć pobór, ale wymaga ponownego przeglądu sekwencji zasilania.

## Kontrola statyczna NTC

W JSON poprawne są: INA+=TS, INA−=REF_HOT, INB+=REF_COLD, INB−=TS; open-drain OUTA/OUTB zwarte; Q1:1G,2S→GND,3D→/CE; R3=/CE→SYS. Nie wykryto odwrócenia komparatorów ani S/D Q1. Aktualne VREFHOT=0.27273V, VREFCOLD=0.80214V.

Niezależnie policzono nominalny model beta10k/B3435: przy0°C TS≈1.0908V→blokada,25°C0.3800V→zezwolenie,45°C0.1842V→blokada. Nie jest to sprawdzenie fizycznego pakietu. Rozpoznanie przerwy/zwarcia NTC jest logicznie poprawne w stanie ustalonym i z ważnym zasilaniem.

TI §6.4.1 dopuszcza wejścia komparatora przy wyłączonym VCC bez zasilania wstecznego. §6.4.2, rys.6-1 przedstawia histerezę jako ±VHYST/2, co uzasadnia ten składnik obecnego budżetu błędów. Należy nadal egzekwować tolerancje rezystorów0.1%, warunki odbioru rzeczywistego NTC i błędy termiczne/przewodów. Skrypt obliczeniowy nie obejmuje rozruchu, stanów GPIO i dynamiki termicznej.

Uruchomiono końcowy `scripts/check_charge_temperature.py`: wszystkie warunki graniczne przeszły. Model z pełnym zakresem nadzorowanej szyny2.5872–3.045V i budżetem rezystorów±0.5% daje HOT29.11–43.60°C i COLD3.55–13.16°C. Odbiór pakietuR0≥24k/R45≤5.20k zachowuje margines wobec obliczonych granic23.073k/5.344k. Są to wyniki modelu statycznego, nie certyfikacja pakietu.

## Pinmap MCU i IMU

Porównanie z tabelą Raytac Ver.L i ST DS13511 nie wykazało zamiany numerów w generatorze:

| Funkcja | Raytac fizyczny pin / GPIO | Ocena |
|---|---|---|
| QSPI SCK |42/P0.19|Szybki pin, prawidłowy|
| IO0/IO1/IO2/IO3 |44/P0.20,43/P0.21,46/P0.22,45/P0.23|Prawidłowa kolejność|
| Flash CS |41/P0.17|Niezależny od resetu|
| IMU SCK/MOSI/MISO/CS |37/P0.13,36/P0.14,39/P0.15,38/P0.16|Szybkie GPIO|
| IMU INT1/INT2 |27/P0.11,29/P0.12|Odpowiednie dla GPIOTE/PPI i INT2/DEN|
| Reset |40/P0.18|Zarezerwowany, wymaga UICR/PSELRESET|
| LFXO |17/P0.00,18/P0.01|Właściwe wyprowadzenia|
| SWDIO/SWCLK |51/53|Prawidłowe|
| LED/przycisk/status/inhibit |3..7/P1.10..14|Wolne funkcje, zgodne z ograniczeniem RF|
| VBAT_ADC |11/P0.02/AIN0|Prawidłowy ADC; bez pull-up/pull-down|
| Zasilanie |28VDD=30VDDH=3V;32VBUS=USB5V|Prawidłowy podział szyn|

LSM6DSV32X:1MISO,2/3GND,4INT1,5VDDIO,6/7GND,8VDD,9INT2,10/11VDDIO,12CS,13SCK,14MOSI — odpowiada DS13511 dla głównego SPI. Oba kondensatory100nF są przewidziane. Nie ma konfliktu SPI i QSPI. Flash pin9/EP oraz układ wielomatrycowy wymagają osobnego zatwierdzenia zgodnie z raportem pamięci.

Nie badano firmware. Warunki do implementacji: przy resecie Flash/IMU CS pozostająHIGH przez pull-up; ustawienie przerwań nie może tworzyć konfliktu INT2 wyjścieIMU↔wyjścieMCU; SystemOFF ma wybudzanieGPIOsense. PinP0.18 nie może jednocześnie zostać aktywowany jakoQSPI CS.

## Raytac CAD i DCCH

Znaleziono działający **oficjalny** [PDF Ver.L,2023/05/24](https://www.raytac.com/tw/download/index.php?index_id=24),73strony. [Oficjalny katalog CAD](https://www.raytac.com/document/index.php?index_m_id=12) wymienia pakiet Footprint_Design Guide230606. Nie uzyskano rozpakowanego CAD ani wiarygodnego odczytu geometrii rastrów, dlatego nie przepisano rozstawu padów ani granic keepout z domysłów.

[Inżynier Nordic akceptuje NC dla nieużywanego DCCH nRF52840](https://devzone.nordicsemi.com/f/nordic-q-a/104586/nrf52840-pcb-antenna-design/451494). Daje to uzasadnienie dla prowizorycznego DCCH31NC w normal mode. Dalsza kontrola powinna obejmować Raytac §8.3, ponieważ moduł ma już wbudowany obwód REG1. Nie włączać REG0DC/DC bez przewidzianego obwodu zewnętrznego; wbudowany induktor REG1 jest osobną sprawą.

Zregenerowany JSON po poprawkach sprawdzono. Pozostają odczyt netlisty przez KiCad, ERC i osobna weryfikacja symbol↔footprint↔MPN oraz wymienione próby fizyczne. Niniejszy raport nie zwalnia projektu do produkcji.
