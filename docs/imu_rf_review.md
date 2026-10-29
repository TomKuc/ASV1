# IMU i moduł radiowy — aktualny przegląd A1

Aktualizacja: **2026-10-29**. Połączenia niżej uzgodniono ze świeżym natywnym eksportem schematu i aktualnym PCB A1, SHA-256 `38545441d19c70f355dd06a2539d2aa0937b113d92569c9b4798a1a04e08c45b`. To dokumentacja połączeń i ograniczeń, nie potwierdzenie fizycznego działania. Kompletny aktualny przydział: [pin_assignment_A1.md](pin_assignment_A1.md); szczegółowy audyt USB/RF: [usb_raytac_audit_A1.md](usb_raytac_audit_A1.md).

## LSM6DSV32XTR

Źródło: [ST DS13511 Rev 2, luty 2024](https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf), §3, §4.4, §6, §9.43. [Oficjalna strona produktu](https://www.st.com/en/mems-and-sensors/lsm6dsv32x.html) potwierdza aktywny wariant TR, LGA-14 i zakresy ±4/8/16/32 g oraz ±125/250/500/1000/2000/4000 °/s. TR oznacza taśmę/szpulę. Obudowa 2.5 × 3.0 mm; nie zastępować footprintem LSM6DSO bez kontroli rysunku mechanicznego.

Pinout dla SPI 4-przewodowego, mode 1 połączeń:

| Pin | Nazwa | Połączenie projektowe |
|---|---|---|
| 1 | SDO/SA0 | MISO |
| 2 | SDx/AH1/Qvar1 | GND |
| 3 | SCx/AH2/Qvar2 | GND |
| 4 | INT1 | IMU_INT1 → U3.27 = P0.11 / GPIOTE |
| 5 | VDD_IO | 3V0, 100 nF |
| 6,7 | GND | GND |
| 8 | VDD | 3V0, 100 nF |
| 9 | INT2/DEN | IMU_INT2 → U3.29 = P0.12; wejście MCU, wyjście tylko po świadomym wyborze DEN |
| 10 | OCS_Aux | Aktualnie +3V0; ST dopuszcza też NC w mode 1 |
| 11 | SDO_Aux | Aktualnie NC; pole lutowane do PCB zgodnie z ST |
| 12 | CS | CS_N, pull-up |
| 13 | SCL/SPC | SCK |
| 14 | SDA/SDI | MOSI |

SPI: tryb 0/3, maks. 10 MHz; propozycja startowa 8 MHz. VDD 1.71–3.6 V; VDD_IO 1.08–3.6 V. Timestamp: **32 bity, 21.75 µs/LSB typowo**, nie 25 µs. ±4000 °/s wymaga wyłączonego OIS żyroskopu. Wymagane ODR 120/240/480/960/1920 Hz są dostępne w high-performance. HAODR wprowadza osobne zestawy częstotliwości (§6.5); zmiana trybu HAODR w power-down.

Propozycja firmware: INT1 obsługuje watermark FIFO, INT2 służy do eksperymentów synchronizacji. GPIOTE/PPI przechwytuje czas zbocza do TIMER bez opóźnienia ISR. Rejestrować natywne tagi FIFO, timestamp, zdarzenia overrun, liczniki bloków i pełny zestaw rejestrów konfiguracyjnych w nagłówku sesji. Nie deklarować dokładnej liczby utraconych próbek na podstawie samej flagi przepełnienia. Temperaturę zapisywać wolniej niż ruch. Trzeba wyznaczyć doświadczalnie zależność zegara IMU od zegara MCU i temperatury.

ST tabela 2 i §7.1 wyraźnie dopuszcza GND na pinach 2/3 przy wyłączonych analog hub i Qvar w mode 1. Dwa ostrzeżenia ERC bidirectional-to-power dotyczą tych dwóch pinów i pozostają jawne. Nie są dowodem błędu tego połączenia. Nie wolno bez ponownej analizy sprzętu włączać alternatywnych trybów wykorzystujących piny 2/3. Piny 6/7 są przyłączone do GND i lutowane.

## Mechanika IMU

[ST TN1383 Rev 1](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf) zaleca symetryczne połączenia padów, brak ścieżek/vias na TOP pod korpusem, odsunięcie od źródeł ciepła i co najmniej 10 mm od źródła siły, np. przycisku. Mocowanie powinno ograniczać ugięcie PCB i rezonanse. [TN0018 Rev 8](https://www.st.com/resource/en/technical_note/tn0018-handling-mounting-and-soldering-guidelines-for-mems-devices-stmicroelectronics.pdf) wymaga uwzględnienia montażu MEMS, geometrii pasty i ostrożnego obchodzenia się z elementem.

Decyzja projektowa: nie tworzyć sprężystej wyspy ani nacięć wokół IMU bez analizy mechanicznej. Na podudziu mogłyby one wprowadzić rezonans do badanego sygnału. Unikać docisku obudowy i baterii bezpośrednio do IMU. Weryfikacja końcowa obejmuje kalibrację po reflow i po skręceniu obudowy.

## MDBT50Q-P1MV2

[Oficjalna strona Raytac](https://www.raytac.com/product/ins.php?index_id=47) wskazuje dokument **Ver. L** oraz pakiet **Footprint/Design Guide 230606**. Moduł ma antenę drukowaną, wymiary 10.5 × 15.5 × 2.0 mm i nRF52840 revision 2. Podczas aktualizacji ponownie odczytano **[oficjalny PDF Ver. L, 2023/05/24](https://www.raytac.com/download/index.php?index_id=43)**. Ograniczenie dostępu do obrazów schematów §8.3 opisano w audycie; nie deklarowano ich wizualnego odczytu.

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

[Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html) definiuje normal voltage mode przez wspólne zasilanie VDD i VDDH; zakres 1.7–3.6 V, poziomy GPIO odnoszą się do VDD, a REG0 jest automatycznie wyłączony. W aktualnym A1 U3.28=U3.30=+3V0, U3.31 DCCH=NC, U3.32=VBUS z USB-C. **NC na DCCH przy nieużywanym REG0 potwierdza [wsparcie Nordic](https://devzone.nordicsemi.com/f/nordic-q-a/108362/vdd-vddh-and-dcch-mistake).** Pełne porównanie rysunku Raytac §8.3 i pojemności pozostaje otwarte z powodu niedostępnych obrazów. Aktualne hostowe C9/C10 to 4.7µF/100nF na +3V0, C11=4.7µF na VBUS; wymagają oceny pojemności efektywnej. VBUS dla USB wymaga 4.35–5.5 V. SWD ma VTref=3V0, GND, SWDIO51 i SWDCLK53; reset jest konfigurowalną funkcją P0.18/pad40.

**Aktualny przydział A1:** QSPI SCK=P0.19, IO0=P0.20, IO1=P0.21, IO2=P0.22, IO3=P0.23, CS=P0.17; P0.18 pozostaje resetem. IMU: SCK=P0.13, MOSI=P0.14, MISO=P0.15, CS=P0.16, **INT1=P0.11, INT2=P0.12**. P0.24/P0.25 są NC. Wcześniejsza propozycja INT na P0.24/P0.25 nie opisuje poprowadzonej płytki. Pełną tabelę GPIO i sygnałów pomocniczych zapisano w [pin_assignment_A1.md](pin_assignment_A1.md).

Nie ma obowiązku dodawania zewnętrznych rezystorów szeregowych USB D+/D−: [Nordic potwierdza ich obecność wewnątrz USB PHY nRF52840](https://devzone.nordicsemi.com/f/nordic-q-a/94955/resistors-for-d-and-d-). Nie dodano rezystorów bez uzasadnienia. Otwarta pozostaje kwalifikacja impedancji i całej geometrii USB oraz ochrony ESD.

Raytac §2.6 ogranicza do standard-drive i ≤10 kHz: P0.02/03/09/10/28/29/30/31 oraz P1.01/02/03/04/05/06/07/10/11/12/13/14/15. Nie przydzielać im SPI, QSPI, UART ani szybkiego PWM.

## RF i sprawy otwarte

Raytac §2.3 wymaga keepout anteny na **każdej warstwie** i umieszczenia modułu przy krawędzi. Aktualny footprint ma 61 padów, także wewnętrzne 56–61; projektowy keepout x=57.8…70.2mm, y=49.8…55.0mm dochodzi poza krawędź PCB. Nowy natywny odczyt potwierdził brak przecięć z miedzią ścieżek, padów, vias i wypełnień. Jest to kontrola zadeklarowanej strefy projektu; wymiarowany rysunek RF producenta i docelowy montaż nadal wymagają osobnego zatwierdzenia.

Decyzje projektowe: bateria, metal, śruby i przewody poza obszarem anteny; testy zasięgu wykonywać w docelowej obudowie na nodze. Preferowany kwarc 32.768 kHz ze względu na stabilność zegara BLE/synchronizacji; wartości kondensatorów wynikają z CL wybranego kwarcu i pojemności pasożytniczych. Sam kryształ nie synchronizuje dwóch niezależnych modułów. Potrzebny protokół wymiany znaczników, estymacja offsetu/dryftu i pomiar niepewności synchronizacji.

Nierozwiązane: wizualne porównanie pełnego rysunku §8.3/pojemności, wybór rzeczywistego stackupu 4L/1.0mm i kwalifikacja USB, rozmieszczenie/kwalifikacja ESD, dokładny STEP wariantu P1MV2, montaż baterii/obudowy i testy naprężeń/RF. Biblioteczny STEP U3 jest generyczny; model USB J1 nadal jest brakujący. Dostępność PCBA dokładnego P1MV2 wymaga osobnego potwierdzenia; dostępność dystrybutora nie jest dowodem zasobów JLCPCB. Firmware nie zostało jeszcze napisane.

Nowsza, jednoznaczna przesłanka dla DCCH: [odpowiedź wsparcia Nordic](https://devzone.nordicsemi.com/f/nordic-q-a/108362/vdd-vddh-and-dcch-mistake) opisuje pin jako niepodłączony przy wyłączonym REG0. Nie oparto decyzji na starszym, niejednoznacznym wątku zawierającym sprzeczne wzmianki DCCH/GND.
