# Przegląd geometrii QSPI, SPI, LFXO i odniesienia GND

Stan odczytu: **2026-10-29T16:55:12.700093+00:00**, KiCad 10.0.7. Plik: `hardware/Ankle_Sensor_V1.kicad_pcb`, SHA256:

`cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`

Raport przeliczono z rzeczywistych obiektów i zapisanych wypełnień PCB, bez zmiany pliku ani ponownego fill. **QSPI 32 MHz, SPI IMU 8 MHz i LFXO wymagają fizycznej kwalifikacji.** Z geometrii ani DRC nie wyznaczono maksymalnej działającej częstotliwości.

Audytor: [review_signal_geometry.py](../scripts/review_signal_geometry.py), metoda v2, SHA256 `6ede0e3c1082661ab2b4b88c667a4e244738f1bdf7172d5464146f1b7a26d1b3`. Szczegóły i fingerprints: [JSON](../reports/signal_geometry_review.json).

## Długości i przelotki

Długości są sumami natywnego `GetLength()` wszystkich ścieżek sieci, z gałęziami i częściami nachodzącymi na pady. Geometria padów nie dodaje osobnej długości. Pominięto połączenia wewnątrz modułów/pakietów i beczki przelotek. To nie pomiar drogi MCU–układ ani obliczenie skew.

| Sieć | Razem [mm] | F.Cu | B.Cu | In2.Cu | Przelotki | Pady w jednym komponencie |
|---|---:|---:|---:|---:|---:|---|
| FLASH_CS_N | 22.335 | 8.500 | 13.835 | — | 3 | tak |
| IMU_CS_N | 18.195 | 6.871 | 11.324 | — | 2 | tak |
| IMU_INT1 | 20.415 | 4.994 | 15.421 | — | 4 | tak |
| IMU_INT2 | 29.239 | 3.315 | 25.923 | — | 2 | tak |
| IMU_MISO | 21.389 | 1.243 | 20.146 | — | 2 | tak |
| IMU_MOSI | 17.907 | 1.938 | 15.970 | — | 2 | tak |
| IMU_SCK | 22.033 | 5.030 | — | 17.003 | 2 | tak |
| LF_XL1 | 5.075 | 5.075 | — | — | 0 | tak |
| LF_XL2 | 4.951 | 4.951 | — | — | 0 | tak |
| QSPI_CLK_FLASH | 14.529 | 14.529 | — | — | 0 | tak |
| QSPI_IO0 | 18.283 | 18.283 | — | — | 0 | tak |
| QSPI_IO1 | 16.064 | 12.560 | 3.504 | — | 2 | tak |
| QSPI_IO2 | 28.034 | 16.622 | 11.412 | — | 2 | tak |
| QSPI_IO3 | 25.340 | 4.398 | 6.450 | 14.492 | 3 | tak |
| QSPI_SCK | 3.923 | 2.396 | 1.528 | — | 2 | tak |

## QSPI i SPI

Zegar QSPI ma łącznie **18.453 mm**: moduł→R11 3.923 mm / 2 przelotek; R11→Flash 14.529 mm / 0 przelotek. R11=22 Ω pozostaje wartością do strojenia, bez pomiaru skuteczności. Trasa wewnętrzna modułu nie jest znana z PCB.

Zmiany warstw, gałęzie i obciążenia wymagają oceny odbić oraz marginesów czasowych. Różnice sum długości sieci nie są obliczonym skew. Brakuje kwalifikowanego stosu dielektryków i pełnego budżetu czasowego pakiet–PCB–odbiornik. Nordic dopuszcza do 32 MHz i wymaga właściwej konfiguracji pinów/high-drive; nie kwalifikuje to automatycznie tej płytki. [Nordic QSPI](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/qspi.html), [Winbond W25Q01JV Rev E](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf).

IMU_SCK: **22.033 mm / 2 przelotek**; MISO 21.389 mm, MOSI 17.907 mm. Planowane 8 MHz wymaga prób CS, duty cycle, setup/hold i integralności odczytów pod obciążeniem. Użyty limit katalogowy IMU: 10 MHz. [ST LSM6DSV32X, tabela SPI](https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf).

## GND i drogi powrotne

In1.Cu: 1 stref GND, 1 zapisanych obrysów fill, pole **1352.639 mm²**, 0 ścieżek na In1 i **52 przelotek przelotowych GND**. Liczba obrysów/pole nie opisują impedancji drogi powrotnej.

Próbkowano środki prostych ścieżek co najwyżej 0.050 mm. Sprawdzono zapisany fill In1 i miedź GND padów/przelotek z wyłączeniem wnętrz otworów. Odległość ≤0.6 mm od otworu jest tylko klasyfikacją pomocniczą. Arc projection jest jawnie pomijane/flagowane, jeśli występuje. To kontrola rzutu, bez symulacji pól/prądu powrotnego.

| Sieć | Brak In1 w rzucie [mm] | Z tego dalej od otworów [mm] | Najdłuższy ciąg w jednym odcinku [mm] | Brak In2 +3V pod B.Cu [mm] |
|---|---:|---:|---:|---:|
| FLASH_CS_N | 2.787 | 0.000 | 0.400 | 4.746 |
| IMU_CS_N | 1.629 | 0.000 | 0.400 | 0.783 |
| IMU_INT1 | 3.194 | 0.000 | 0.400 | 1.636 |
| IMU_INT2 | 1.633 | 0.000 | 0.400 | 3.960 |
| IMU_MISO | 1.619 | 0.000 | 0.400 | 7.033 |
| IMU_MOSI | 1.585 | 0.000 | 0.400 | 1.439 |
| IMU_SCK | 1.639 | 0.000 | 0.421 | 0.000 |
| LF_XL1 | 0.000 | 0.000 | 0.000 | 0.000 |
| LF_XL2 | 0.000 | 0.000 | 0.000 | 0.000 |
| QSPI_CLK_FLASH | 0.000 | 0.000 | 0.000 | 0.000 |
| QSPI_IO0 | 0.000 | 0.000 | 0.000 | 0.000 |
| QSPI_IO1 | 1.707 | 0.000 | 0.400 | 1.333 |
| QSPI_IO2 | 1.621 | 0.000 | 0.397 | 2.281 |
| QSPI_IO3 | 2.810 | 0.000 | 0.400 | 0.800 |
| QSPI_SCK | 1.647 | 0.000 | 0.394 | 0.812 |

Największa odległość od przelotki QSPI do najbliższej przelotki GND: **4.785 mm (QSPI_IO3)**. Nie jest to samodzielne kryterium zaliczenia drogi powrotnej.

B.Cu sąsiaduje z mieszaną In2 (+3V0 i sygnały); In1 GND leży dalej. Pokrycie rzutu In1 nie dowodzi ciągłego najbliższego odniesienia na In2. Należy ocenić połączenia odniesienia przy przejściach warstw i wpływ antypadów według rzeczywistego stosu. [TI SCAA082A](https://www.ti.com/lit/an/scaa082a/scaa082a.pdf).

Nominalna grubość PCB: 1.000 mm. Szczegółowy blok dielektryków w pliku: **brak**. Parametry fabryczne, Er i impedancje nie zostały zakwalifikowane; skrypt nie wyznacza impedancji ze stałych domyślnych KiCad.

## LFXO

LF_XL1: **5.075 mm / 0 przelotek**, warstwy F.Cu; odległość prosta MCU→Y1 2.574 mm, Y1→C 2.144 mm; najbliższa przelotka GND od pada kondensatora: 0.620 mm.

LF_XL2: **4.951 mm / 0 przelotek**, warstwy F.Cu; odległość prosta MCU→Y1 2.438 mm, Y1→C 2.166 mm; najbliższa przelotka GND od pada kondensatora: 0.620 mm.

C7/C8=10 pF to wartości początkowe. Kryształ ABS07 w wybranej opcji ma CL=7 pF; pojemności pinów/PCB, ESR, drive, start i temperaturę należy ocenić fizycznie. Nie obciążać węzłów kwarcu zwykłą sondą podczas oceny częstotliwości; użyć buforowanego sygnału LFCLK. [Nordic CLOCK](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/clock.html), [Abracon ABS07](https://abracon.com/Resonators/ABS07.pdf).

## Porównanie z bazą

Bazowy PCB SHA256: `b5487d09753bbf0490bf91bda6c803934609b778283ef87c044309bc1514f678`. Zmienione metryki sieci: **IMU_CS_N, IMU_MOSI, QSPI_IO3**. Wszystkie wartości bieżące przeliczono ponownie; nie podmieniono jedynie hasha.

Pełna identyczność geometrii według fingerprints: **nie**.

Bazową PCB i bieżącą PCB odczytano natywnie tym samym audytorem; porównano geometrie wszystkich badanych ścieżek, przelotek i padów. Nie korzystano wyłącznie z historycznych sum długości.

Metoda v2 dodatkowo usuwa wnętrza otworów z kształtów miedzi padów/przelotek; może to zmienić wyniki projekcji względem historycznej metody v1.

## Kontrole i kwalifikacja

Dostarczony [DRC](../reports/drc_final.json) (`2302169c712377678652945ecb0fae17b8ff5bb997d69eba0bc678dcf7d1a629`): **0 naruszeń / 0 niepołączonych / 0 parity**, 0 ignorowanych kontroli. Skrypt nie uruchamia DRC i nie potwierdza niezależnie związania tego JSON z hashem PCB; źródło DRC musi wskazać prowadzący audyt.

Wymagane pozostają pomiary QSPI/SPI, strojenie zboczy i R11, testy CRC pełnych 128 MiB i obu dies po resetach/zanikach oraz kwalifikacja LFXO. [Plan prób Flash A1](flash_firmware_test_plan_A1.md). Poprawny DRC i długości ścieżek nie są certyfikacją SI ani dokładności/synchronizacji zegarów.
