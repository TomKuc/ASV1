# IMU i moduł radiowy — przegląd do schematu

Data weryfikacji: 2026-10-27. Status: dane wejściowe do projektu; nie jest to raport ERC/DRC.

## LSM6DSV32XTR

Źródło: [ST DS13511 Rev 2, luty 2024](https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf), §3, §4.4, §6, §9.43. [Oficjalna strona produktu](https://www.st.com/en/mems-and-sensors/lsm6dsv32x.html) potwierdza aktywny wariant TR, LGA-14 i zakresy ±4/8/16/32 g oraz ±125/250/500/1000/2000/4000 °/s. TR oznacza taśmę/szpulę. Obudowa 2.5 × 3.0 mm; nie zastępować footprintem LSM6DSO bez kontroli rysunku mechanicznego.

Pinout dla SPI 4-przewodowego, mode 1 połączeń:

| Pin | Nazwa | Połączenie projektowe |
|---|---|---|
| 1 | SDO/SA0 | MISO |
| 2 | SDx/AH1/Qvar1 | GND |
| 3 | SCx/AH2/Qvar2 | GND |
| 4 | INT1 | GPIO/GPIOTE |
| 5 | VDD_IO | 3V0, 100 nF |
| 6,7 | GND | GND |
| 8 | VDD | 3V0, 100 nF |
| 9 | INT2/DEN | GPIO/GPIOTE; możliwe wyjście MCU |
| 10 | OCS_Aux | 3V0 lub NC |
| 11 | SDO_Aux | 3V0 lub NC |
| 12 | CS | CS_N, pull-up |
| 13 | SCL/SPC | SCK |
| 14 | SDA/SDI | MOSI |

SPI: tryb 0/3, maks. 10 MHz; propozycja startowa 8 MHz. VDD 1.71–3.6 V; VDD_IO 1.08–3.6 V. Timestamp: **32 bity, 21.75 µs/LSB typowo**, nie 25 µs. ±4000 °/s wymaga wyłączonego OIS żyroskopu. Wymagane ODR 120/240/480/960/1920 Hz są dostępne w high-performance. HAODR wprowadza osobne zestawy częstotliwości (§6.5); zmiana trybu HAODR w power-down.

Propozycja firmware: INT1 obsługuje watermark FIFO, INT2 służy do eksperymentów synchronizacji. GPIOTE/PPI przechwytuje czas zbocza do TIMER bez opóźnienia ISR. Rejestrować natywne tagi FIFO, timestamp, zdarzenia overrun, liczniki bloków i pełny zestaw rejestrów konfiguracyjnych w nagłówku sesji. Nie deklarować dokładnej liczby utraconych próbek na podstawie samej flagi przepełnienia. Temperaturę zapisywać wolniej niż ruch. Trzeba wyznaczyć doświadczalnie zależność zegara IMU od zegara MCU i temperatury.

## Mechanika IMU

[ST TN1383 Rev 1](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf) zaleca symetryczne połączenia padów, brak ścieżek/vias na TOP pod korpusem, odsunięcie od źródeł ciepła i co najmniej 10 mm od źródła siły, np. przycisku. Mocowanie powinno ograniczać ugięcie PCB i rezonanse. [TN0018 Rev 8](https://www.st.com/resource/en/technical_note/tn0018-handling-mounting-and-soldering-guidelines-for-mems-devices-stmicroelectronics.pdf) wymaga uwzględnienia montażu MEMS, geometrii pasty i ostrożnego obchodzenia się z elementem.

Decyzja projektowa: nie tworzyć sprężystej wyspy ani nacięć wokół IMU bez analizy mechanicznej. Na podudziu mogłyby one wprowadzić rezonans do badanego sygnału. Unikać docisku obudowy i baterii bezpośrednio do IMU. Weryfikacja końcowa obejmuje kalibrację po reflow i po skręceniu obudowy.

## MDBT50Q-P1MV2

[Oficjalna strona Raytac](https://www.raytac.com/product/ins.php?index_id=47) wskazuje dokument **Ver. L** oraz pakiet **Footprint/Design Guide 230606**. Moduł ma antenę drukowaną, wymiary 10.5 × 15.5 × 2.0 mm i nRF52840 revision 2. Dokument producenta Ver. L odczytano początkowo z kopii dystrybutora, następnie odnaleziono działający **[oficjalny PDF Ver. L,2023/05/24](https://www.raytac.com/tw/download/index.php?index_id=24)**. Nie zarchiwizowano lokalnego PDF.

Tabela poniżej pochodzi z §2.5 Ver. L. **Nie używać tabeli z Ver. B: część numerów dolnej krawędzi różni się.**

| Pin | Nazwa | Pin | Nazwa | Pin | Nazwa |
|---|---|---|---|---|---|
| 1 | GND | 22 | P0.06 | 43 | P0.21 |
| 2 | GND | 23 | P0.07 | 44 | P0.20 |
| 3 | P1.10 | 24 | P0.08 | 45 | P0.23 |
| 4 | P1.11 | 25 | P1.08 | 46 | P0.22 |
| 5 | P1.12 | 26 | P1.09 | 47 | P1.00 |
| 6 | P1.13 | 27 | P0.11 | 48 | P0.24 |
| 7 | P1.14 | 28 | VDD | 49 | P0.25 |
| 8 | P1.15 | 29 | P0.12 | 50 | P1.02 |
| 9 | P0.03 | 30 | VDDH | 51 | SWDIO |
| 10 | P0.29 | 31 | DCCH | 52 | P0.09/NFC1 |
| 11 | P0.02 | 32 | VBUS | 53 | SWDCLK |
| 12 | P0.31 | 33 | GND | 54 | P0.10/NFC2 |
| 13 | P0.28 | 34 | D− | 55 | GND |
| 14 | P0.30 | 35 | D+ | 56 | P1.04 |
| 15 | GND | 36 | P0.14 | 57 | P1.06 |
| 16 | P0.27 | 37 | P0.13 | 58 | P1.07 |
| 17 | P0.00/XL1 | 38 | P0.16 | 59 | P1.05 |
| 18 | P0.01/XL2 | 39 | P0.15 | 60 | P1.03 |
| 19 | P0.26 | 40 | P0.18/nRESET | 61 | P1.01 |
| 20 | P0.04 | 41 | P0.17 | | |
| 21 | P0.05 | 42 | P0.19 | | |

## Zasilanie i przydział sygnałów

[Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html) definiuje normal voltage mode przez wspólne zasilanie VDD i VDDH; zakres 1.7–3.6 V, poziomy GPIO odnoszą się do VDD. Dla 3V0 użyć kompletnej konfiguracji normal voltage z Raytac §8.3. **Połączenie DCCH oraz lokalne pojemności należy potwierdzić wizualnie na schemacie referencyjnym przed zatwierdzeniem schematu**: warstwa tekstowa PDF nie oddaje przewodów. Nie interpretować DCCH jako zwykłego wyjścia 3V0. VBUS dla USB wymaga 4.35–5.5 V; D+/D− nie są GPIO. SWD wymaga VTref=3V0, GND, SWDIO i SWDCLK; reset jest konfigurowalną funkcją P0.18.

Propozycja przydziału (do pogodzenia z routingiem): QSPI SCK=P0.19, IO0=P0.20, IO1=P0.21, IO2=P0.22, IO3=P0.23, CS=P0.17; P0.18 pozostaje resetem. IMU: SCK=P0.13, MOSI=P0.14, MISO=P0.15, CS=P0.16, INT1=P0.24, INT2=P0.25. Przycisk/LED i ADC mogą korzystać z wolniejszych GPIO.

Raytac §2.6 ogranicza do standard-drive i ≤10 kHz: P0.02/03/09/10/28/29/30/31 oraz P1.01/02/03/04/05/06/07/10/11/12/13/14/15. Nie przydzielać im SPI, QSPI, UART ani szybkiego PWM.

## RF i sprawy otwarte

Raytac §2.3 wymaga keepout anteny na **każdej warstwie** i umieszczenia modułu przy krawędzi. Dokładny wymiar i położenie granicy anteny należy odczytać z rysunku footprintu Ver. L/Design Guide, zanim powstanie PCB. Nie wpisano tu zgadywanej geometrii padów. Footprint musi obejmować także wewnętrzne pady 56–61 i mieć zweryfikowaną orientację TOP.

Decyzje projektowe: bateria, metal, śruby i przewody poza obszarem anteny; testy zasięgu wykonywać w docelowej obudowie na nodze. Preferowany kwarc 32.768 kHz ze względu na stabilność zegara BLE/synchronizacji; wartości kondensatorów wynikają z CL wybranego kwarcu i pojemności pasożytniczych. Sam kryształ nie synchronizuje dwóch niezależnych modułów. Potrzebny protokół wymiany znaczników, estymacja offsetu/dryftu i pomiar niepewności synchronizacji.

Nierozwiązane: dokładny zweryfikowany footprint i STEP Raytac, połączenie DCCH z §8.3, pojemności modułu i USB, dostępność PCBA dokładnego P1MV2. Dostępność katalogowa u dystrybutora nie jest dowodem dostępności JLCPCB.

Dodatkowa przesłanka do przeglądu DCCH: [odpowiedź inżyniera Nordic dla dokładnego MDBT50Q-1MV2](https://devzone.nordicsemi.com/f/nordic-q-a/62718/custom-pcb-with-nrf52840) zatwierdza rysunek przy deklaracji użytkownika DCCH/D+/D− unconnected oraz VDD=VDDH. Ten sam wpis zawiera jednak sprzeczną linijkę o DCCH=GND (możliwa literówka zamiast VBUS), dlatego tekst bez widoku rysunku nie zamyka weryfikacji.
