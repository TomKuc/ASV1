# Przydział pinów Ankle Sensor V1 — A1

Odczyt aktualnego schematu i PCB: 29.10.2026. PCB SHA-256 `cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`. Świeży eksport natywnej netlisty porównano ze wszystkimi padami U3/U4/U6/J1: **zero rozbieżności nazw sieci**. Numery poniżej są numerami padów **modułu Raytac**, nie obudowy samego nRF52840.

Nazwy pinów: [Raytac Ver. L, §2.5](https://www.raytac.com/download/index.php?index_id=43); połączenia: bieżący projekt. **INT1=P0.11, INT2=P0.12**; wcześniejsza propozycja P0.24/P0.25 nie opisuje A1.

| Pad U3 | Funkcja / GPIO | Sieć A1 | Połączenia poza U3 |
|---:|---|---|---|
| 1 | GND | GND | Wspólna szyna; szczegóły w schemacie |
| 2 | GND | GND | Wspólna szyna; szczegóły w schemacie |
| 3 | P1.10 | LED_K | D1.1 |
| 4 | P1.11 | USER_BTN_N | C17.1, R16.2, SW1.1 |
| 5 | P1.12 | CHG_STAT1_N | R4.2, U1.9 |
| 6 | P1.13 | CHG_STAT2_N | R5.2, U1.3 |
| 7 | P1.14 | CHG_INHIBIT | Q2.1, R24.1 |
| 8 | P1.15 | NC — flaga schematu | — |
| 9 | P0.03 | NC — flaga schematu | — |
| 10 | P0.29 | NC — flaga schematu | — |
| 11 | P0.02 | VBAT_ADC | C6.1, R6.2, R7.1 |
| 12 | P0.31 | NC — flaga schematu | — |
| 13 | P0.28 | NC — flaga schematu | — |
| 14 | P0.30 | NC — flaga schematu | — |
| 15 | GND | GND | Wspólna szyna; szczegóły w schemacie |
| 16 | P0.27 | NC — flaga schematu | — |
| 17 | P0.00 / XL1 | LF_XL1 | C7.1, Y1.1 |
| 18 | P0.01 / XL2 | LF_XL2 | C8.1, Y1.2 |
| 19 | P0.26 | NC — flaga schematu | — |
| 20 | P0.04 | NC — flaga schematu | — |
| 21 | P0.05 | NC — flaga schematu | — |
| 22 | P0.06 | NC — flaga schematu | — |
| 23 | P0.07 | NC — flaga schematu | — |
| 24 | P0.08 | NC — flaga schematu | — |
| 25 | P1.08 | NC — flaga schematu | — |
| 26 | P1.09 | NC — flaga schematu | — |
| 27 | P0.11 | IMU_INT1 | TP6.1, U4.4 |
| 28 | VDD | +3V0 | Wspólna szyna; szczegóły w schemacie |
| 29 | P0.12 | IMU_INT2 | TP7.1, U4.9 |
| 30 | VDDH | +3V0 | Wspólna szyna; szczegóły w schemacie |
| 31 | DCCH | NC — flaga schematu | — |
| 32 | VBUS | VBUS | Wspólna szyna; szczegóły w schemacie |
| 33 | GND | GND | Wspólna szyna; szczegóły w schemacie |
| 34 | D- | USB_DN | U6.4 |
| 35 | D+ | USB_DP | U6.6 |
| 36 | P0.14 | IMU_MOSI | U4.14 |
| 37 | P0.13 | IMU_SCK | U4.13 |
| 38 | P0.16 | IMU_CS_N | R9.2, U4.12 |
| 39 | P0.15 | IMU_MISO | U4.1 |
| 40 | P0.18 / nRESET | RESET_N | J3.5, R8.2, TP5.1 |
| 41 | P0.17 | FLASH_CS_N | R10.2, U5.1 |
| 42 | P0.19 | QSPI_SCK | R11.1 |
| 43 | P0.21 | QSPI_IO1 | U5.2 |
| 44 | P0.20 | QSPI_IO0 | U5.5 |
| 45 | P0.23 | QSPI_IO3 | R13.2, U5.7 |
| 46 | P0.22 | QSPI_IO2 | R12.2, U5.3 |
| 47 | P1.00 | NC — flaga schematu | — |
| 48 | P0.24 | NC — flaga schematu | — |
| 49 | P0.25 | NC — flaga schematu | — |
| 50 | P1.02 | NC — flaga schematu | — |
| 51 | SWDIO | SWDIO | J3.2 |
| 52 | P0.09 / NFC1 | NC — flaga schematu | — |
| 53 | SWDCLK | SWCLK | J3.4 |
| 54 | P0.10 / NFC2 | NC — flaga schematu | — |
| 55 | GND | GND | Wspólna szyna; szczegóły w schemacie |
| 56 | P1.04 | NC — flaga schematu | — |
| 57 | P1.06 | NC — flaga schematu | — |
| 58 | P1.07 | NC — flaga schematu | — |
| 59 | P1.05 | NC — flaga schematu | — |
| 60 | P1.03 | NC — flaga schematu | — |
| 61 | P1.01 | NC — flaga schematu | — |

| Sygnał IMU | Pad U4 | Pad U3 | GPIO nRF52840 |
|---|---:|---:|---|
| SCK | 13 | 37 | P0.13 |
| MOSI | 14 | 36 | P0.14 |
| MISO | 1 | 39 | P0.15 |
| CS_N | 12 | 38 | P0.16 |
| INT1 | 4 | 27 | P0.11 |
| INT2 / DEN | 9 | 29 | P0.12 |

Firmware nie zostało jeszcze napisane. Dla IMU używać SPI 4-wire, mode 0/3, maksymalnie 10 MHz; początkowo 8 MHz jest decyzją testową, nie obowiązkiem układu. INT1/INT2 skonfigurować jako wejścia MCU; wyjście na INT2 jest dopuszczalne dopiero przy świadomym przełączeniu sensora w funkcję DEN. Qvar, analog hub i alternatywne tryby wykorzystujące piny 2/3 muszą pozostać wyłączone przy ich połączeniu z GND.

P0.18 jest zarezerwowany dla nRESET/SWD i wymaga właściwej konfiguracji UICR. P0.00/01 obsługują zamontowany kwarc 32.768 kHz; C7/C8=10 pF są robocze i wymagają kwalifikacji CL/pasożytów. P0.24/25 są aktualnie NC.

P1.10/11/12/13/14 oraz P0.02 należą do pinów ograniczonych przez Raytac do standard-drive i wolnych sygnałów (≤10 kHz). Aktualnie są użyte dla LED, przycisku, statusów ładowania, CHG_INHIBIT i ADC. Nie uruchamiać na nich szybkiego PWM ani magistral SPI/UART. CHG_INHIBIT=1 wymusza blokadę ładowania; P0.02/AIN0 mierzy dzielnik baterii, a nie samą szynę VBAT bezpośrednio.

Aktualny R24 podciąga CHG_INHIBIT do +3V0: domyślny stan wysoki blokuje ładowanie do świadomego zwolnienia przez firmware. Nie włączać TRACE na P0.11/P0.12 zajętych przez przerwania IMU; SWD korzysta z oddzielnych padów 51 i 53.

Pełny wynik audytu i źródła: [usb_raytac_audit_A1.md](usb_raytac_audit_A1.md), [JSON](../reports/usb_raytac_audit_A1.json).

Aktualizacja końcowa: netlista `reports/usb_audit_netlist_A1.xml` i raport USB potwierdzają tę samą pinmapę po zmianie wyłącznie18 szerokości USB. [Aktualny przekrój i wyniki modelu](usb_stackup_final_A1.md); nie zmieniono przerwań IMU.
