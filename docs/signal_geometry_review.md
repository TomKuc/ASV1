# Przegląd geometrii QSPI, SPI, LFXO i odniesienia GND

Stan odczytu: **2026-10-28T14:41:32.784683+00:00**, KiCad 10.0.7. Plik: `hardware/Ankle_Sensor_V1.kicad_pcb`, SHA256:

`b5487d09753bbf0490bf91bda6c803934609b778283ef87c044309bc1514f678`

Raport opisuje geometrię prototypu. **QSPI 32 MHz, SPI IMU 8 MHz oraz LFXO wymagają fizycznej kwalifikacji.** Z samej długości ścieżek i wyniku DRC nie wyznaczono maksymalnej działającej częstotliwości. Przegląd wykonano bez zmiany PCB. Szczegółowe współrzędne, dane przelotek i próbkowania są w [raporcie JSON](../reports/signal_geometry_review.json).

## Długości i przelotki

Długość oznacza sumę natywnego `GetLength()` wszystkich odcinków danej sieci. Uwzględnia gałęzie do rezystorów podciągających i pól testowych. Obejmuje także fragmenty ścieżek nachodzące na pady; geometria padów nie dodaje osobnej długości. Nie dolicza połączeń w pakietach/modułach ani długości beczek przelotek. Do obliczenia opóźnienia i skew potrzebne są odrębne ścieżki MCU–układ i dane elektryczne pakietów. Wszystkie poniższe sieci mają pady w jednym natywnym komponencie łączności.

| Sieć | Razem [mm] | F.Cu [mm] | B.Cu [mm] | In2.Cu [mm] | Przelotki |
|---|---:|---:|---:|---:|---:|
| FLASH_CS_N | 22.34 | 8.50 | 13.84 | — | 3 |
| IMU_CS_N | 18.12 | 6.87 | 11.25 | — | 2 |
| IMU_INT1 | 20.41 | 4.99 | 15.42 | — | 4 |
| IMU_INT2 | 29.24 | 3.32 | 25.92 | — | 2 |
| IMU_MISO | 21.39 | 1.24 | 20.15 | — | 2 |
| IMU_MOSI | 17.77 | 1.94 | 15.83 | — | 2 |
| IMU_SCK | 22.03 | 5.03 | — | 17.00 | 2 |
| LF_XL1 | 5.08 | 5.08 | — | — | 0 |
| LF_XL2 | 4.95 | 4.95 | — | — | 0 |
| QSPI_CLK_FLASH | 14.53 | 14.53 | — | — | 0 |
| QSPI_IO0 | 18.28 | 18.28 | — | — | 0 |
| QSPI_IO1 | 16.06 | 12.56 | 3.50 | — | 2 |
| QSPI_IO2 | 28.03 | 16.62 | 11.41 | — | 2 |
| QSPI_IO3 | 25.24 | 4.26 | 6.45 | 14.53 | 3 |
| QSPI_SCK | 3.92 | 2.40 | 1.53 | — | 2 |

## QSPI i SPI — ocena ograniczeń

Zegar QSPI ma łącznie **18,45 mm** ścieżek: od wyprowadzenia modułu do R11 **3,92 mm i dwie przelotki**, od R11 do Flash **14,53 mm na F.Cu, bez przelotek**. R11=22 Ω jest elementem do strojenia tłumienia; jego skuteczności nie zmierzono. Odcinek przed R11 oraz wewnętrzna trasa modułu pozostają częścią obwodu sterownika.

IO0 biegnie w całości na F.Cu. IO1/IO2 korzystają również z B.Cu, a IO3 z F.Cu/B.Cu/In2.Cu i trzech przelotek. Gałęzie pull-up są zawarte w tabeli. Taka geometria wymaga oceny odbić, obciążenia i czasów przy odczycie; różnica sum długości sieci nie jest obliczonym skew magistrali. Brak szczegółowego stosu dielektryków, modelu wyjść/wejść i analizy czasowej ogranicza wnioski dotyczące szybkości.

Nordic podaje konfigurowalny zegar QSPI do **32 MHz** i wymóg właściwej konfiguracji pinów/high-drive. Wartość katalogowa dotyczy interfejsu układu; kwalifikacja tej PCB musi objąć pamięć, połączenia i warunki zasilania/temperatury. Przy 32 MHz okres wynosi 31,25 ns, a użyteczne okno danych zależy od czasów wyjścia Flash, setup/hold odbiornika, opóźnień i zboczy. Nie wykonano pełnego budżetu czasowego. [Nordic — QSPI](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/qspi.html), [Winbond W25Q01JV Rev E](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf).

IMU_SCK ma **22,03 mm i dwie przelotki**, głównie na In2.Cu. MISO ma **21,39 mm**, z czego 20,15 mm na B.Cu; MOSI 17,77 mm z 15,83 mm na B.Cu. Katalog LSM6DSV32X ogranicza SPI do **10 MHz**; planowane 8 MHz pozostaje nastawą do prób. Pomiary powinny potwierdzić czasy CS, duty cycle, setup/hold i odczyt SDO w wymaganych warunkach. [ST — DS13511 Rev 2, tabela 7](https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf).

## Płaszczyzna GND i drogi powrotne

In1.Cu ma **jeden wypełniony obszar GND, około 1355,17 mm²**, bez ścieżek sygnałowych. Na płytce są **53 przelotki GND**. Spójność obszaru nie opisuje impedancji lokalnej drogi powrotnej ani wpływu skupisk antypadów.

Sprawdzono rzut środka ścieżki na rzeczywistą wypełnioną In1.Cu, z próbkami oddalonymi o najwyżej 0,05 mm i z uwzględnieniem miedzi padów/przelotek GND. LFXO, QSPI_IO0 i odcinek zegara R11→Flash mają **100% pokrycia próbek**. Dla pozostałych sieci wykryte braki pokrycia występowały wyłącznie w pobliżu otworów, według pomocniczej klasyfikacji odległości ≤0,6 mm od kształtu otworu. Najdłuższy ciąg takich próbek w jednym prostym odcinku wynosi około **0,422 mm**. To kontrola projekcji geometrii; nie symuluje przepływu prądu wokół antypadów i nie potwierdza impedancji.

**Odcinki B.Cu wymagają szczególnej uwagi:** bezpośrednio sąsiaduje z nimi mieszana warstwa In2.Cu z +3V0 i sygnałami. In1 GND znajduje się dalej. Przykładowo około **7,03 mm** przebiegu IMU_MISO na B.Cu nie ma w swoim rzucie miedzi +3V0 na In2.Cu. Nie oznacza to przerwania elektrycznego GND; wskazuje zmianę najbliższego odniesienia i potrzebę oceny drogi powrotnej przy rzeczywistym stosie warstw. TI opisuje wpływ szczelin odniesienia na indukcyjność pętli i emisję. [TI — High-Speed Layout Guidelines, SCAA082A](https://www.ti.com/lit/an/scaa082a/scaa082a.pdf).

Najbliższa przelotka GND przy niektórych przelotkach QSPI jest oddalona o kilka milimetrów, maksymalnie około **4,79 mm dla IO3**. Współrzędne są w JSON. Sama odległość do najbliższej przelotki nie dowodzi poprawności ani błędu powrotu; istotne są warstwy odniesienia i połączenia zasilanie–GND. W kolejnej optymalizacji warto preferować F.Cu/In2.Cu nad GND i ocenić lokalne połączenia odniesienia przy zmianach na B.Cu.

PCB deklaruje cztery warstwy i nominalnie **1.0 mm** grubości, lecz nie zawiera szczegółowego bloku stackup dielektryków. Grubości izolacji, epsilon, rzeczywista miedź i impedancje muszą zostać uzgodnione z fabryką. Nie wyliczono kontrolowanej impedancji ani opóźnień ze stałych domyślnych KiCad.

## LFXO po korekcie

Y1 obrócono o 180° bez przesuwania środka, dzięki czemu XL1 i XL2 nie wymagają krzyżowania. LF_XL1 ma **5,075 mm**, LF_XL2 **4,951 mm**, wliczając gałęzie do C7/C8. Obie sieci są wyłącznie na F.Cu i mają **zero przelotek**. Odległości proste pad MCU→pad Y1 wynoszą około **2,57/2,44 mm**, a Y1→kondensator około **2,14/2,17 mm**. Pady masy C7/C8 mają najbliższe przelotki GND w odległości **0,62 mm**. Obie sieci mają pełne pokrycie próbek projekcji GND.

To poprawia geometrię oscylatora względem wcześniejszego LF_XL2 o długości 48,69 mm z pięcioma przelotkami. C7/C8=10 pF pozostają wartościami początkowymi: CL obejmuje pojemność pinów i PCB według równania Nordic. ABS07 w opcji „7” jest kryształem CL=7 pF; ESR, drive level, rozruch i częstotliwość trzeba potwierdzić dla rzeczywistej partii i temperatury. Próbkowanie LFCLK przez buforowany sygnał pozwala oceniać częstotliwość bez obciążania węzłów kwarcu sondą. [Nordic — CLOCK/LFXO](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/clock.html), [Abracon — ABS07](https://abracon.com/Resonators/ABS07.pdf).

## Zakres kwalifikacji prototypu

Wymagane przed deklaracją parametrów użytkowych:

- QSPI: pomiar SCK/IO przy układach, przeregulowań, dzwonienia i marginesów czasowych; próby niższych częstotliwości oraz docelowych 32 MHz, strojenie R11/drive z zachowaniem specyfikacji Nordic/Winbond.
- Pamięć: długie testy wzorców i CRC przy zapisie/odczycie obu matryc, zmianach napięcia/temperatury, resetach i power-cycle; test granic adresowania zgodnie z kontraktem firmware.
- IMU: odczyty przy planowanym 8 MHz, kontrola FIFO/overrun i integralności surowych próbek, pomiary przy aktywnym BLE i zapisie Flash.
- LFXO: start i dokładność zegara w temperaturze, ocena CL/ESR/drive oraz dryftu dwóch modułów; sam poprawny routing nie synchronizuje zegarów nóg.

Natywny [DRC końcowy](../reports/drc_final.json) dla odczytanego stanu ma **0 naruszeń, 0 niepołączonych elementów i 0 problemów parity** w zakresie aktywnych kontroli. DRC nie jest wynikiem pomiaru SI, kwalifikacją 32 MHz ani potwierdzeniem dokładności oscylatora.
