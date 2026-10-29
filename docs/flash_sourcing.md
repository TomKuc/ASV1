# Weryfikacja pamięci i zaopatrzenia — 2026-10-27

Status: przegląd dokumentacji i publicznych katalogów; nie jest rezerwacją części ani potwierdzeniem wyceny PCBA. Liczby magazynowe pochodzą z odpowiedzi serwisów dostępnych tego dnia; różne indeksowane wersje tej samej strony podają różne stany.

Aktualizacja wymagań: po prośbie o większą pojemność kandydatem do bieżącego schematu został **W25Q01JVZEIQ 128 MiB**. Poniższa część o W25Q512JV dokumentuje pierwotny wariant 64 MiB; aktualny dobór i ograniczenia dual-die opisuje [memory_upgrade.md](memory_upgrade.md).

## Pamięć

Pierwotny wariant: **W25Q512JVEIQ**, NOR 512 Mbit = 64 MiB, WSON-8, korpus 8 × 6 mm, raster 1,27 mm, 2,7–3,6 V. Warianty FIQ (SOIC-16) i BIQ (TFBGA-24) wymagają innych footprintów. IQ ma QE ustalone na 1; nie zastępować bez weryfikacji wariantem IM/DTR.

Pinout WSON8, widok z góry: **1 /CS, 2 IO1, 3 IO2, 4 GND, 5 IO0, 6 CLK, 7 IO3, 8 VCC**. Pad centralny nie ma połączenia wewnętrznego; dopuszczalne GND lub floating. Numer 9 dla EP jest konwencją biblioteki projektu, nie numerem producenta. Źródło: Winbond, W25Q512JV Rev G, §3.2, §9.2.

Parametry do budżetu: programowanie/kasowanie 25 mA max; odczyt 35 mA max przy 50 MHz. Strona 256 B; programowanie 3,5 ms max, kasowanie 4 KiB 400 ms max, 64 KiB 2 s max. Standby 10 µA typ / 60 µA max przy 85°C; deep power-down 1 µA typ / 20 µA max. Źródło: ten sam dokument, §9.4, §9.7.

Ważna rozbieżność rysunków: Rev B 2019 podaje EP nominalnie 4,65 × 5,20 mm, Rev G 2022 3,40 × 4,30 mm. Mały EP w bibliotece należy zweryfikować z aktualnym rysunkiem partii dostarczanej przez JLCPCB. Producent zaleca brak odkrytych przelotek pod EP. Nie uznawać footprintu za zwolniony do produkcji przed tym porównaniem.

Źródła producenta:

- [Winbond — katalog dokumentacji W25Q512JV](https://www.winbond.com.tw/hq/support/documentation/?__locale=en&line=/product/code-storage-flash/index.html&family=/product/code-storage-flash/qspi-nor/index.html&category=/.categories/resources/datasheet/&pno=W25Q512JV). Katalog wymienia nowszą wersję z 2026-05-25, ale formularz pobierania nie udostępnił jej treści narzędziu.
- [Winbond W25Q512JV Rev G, 2022-01-12 — kopia dokumentu producenta u Mouser](https://www.mouser.com/datasheet/2/949/Winbond_W25Q512JV_Datasheet-3240039.pdf).
- [Winbond W25Q512JV Rev B, 2019-06-25 — kopia dokumentu producenta w LCSC](https://datasheet.lcsc.com/datasheet/pdf/078cdcdfe6f9b094c504cb43fbd40979.pdf?productCode=C2986165).
- [Oficjalny Winbond selection guide 2025](https://www.winbond.com/export/sites/winbond/product-selection-guide/file/2025-Product-Selection-Guide-Winbond-Code-Storage-Flash-Memory.pdf).

## nRF52840 QSPI i adresowanie

nRF52840 obsługuje 24- i 32-bitowe adresy, konfigurowane IFCONFIG0.ADDRMODE. Instrukcję wejścia w tryb adresowy można przekazać przez ADDRCONF/custom instruction. Zestaw stałych instrukcji obejmuje 0x6B odczyt quad output i 0x32 quad page program; nie zakładać możliwości dowolnego zastąpienia ich dedykowanymi instrukcjami czterobajtowymi 0x6C/0x34. Producent zaleca high-drive GPIO oraz wybór pinów z reference circuitry. Maksymalny SCK kontrolera wynosi 32 MHz. [Nordic — QSPI nRF52840](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/qspi.html?contentId=SMu_w_g~A4Mqfus~XHl4fQ), [Nordic nrfx QSPI HAL](https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrfx/html/group__nrf__qspi__hal.html).

Zalecana sekwencja projektu: odczytać JEDEC/SFDP i statusy, poczekać na koniec BUSY, wysłać EN4B **0xB7**, potwierdzić ADS, uruchomić kontroler w ADDRMODE32 z 0x6B/0x32. Po każdym resecie MCU lub flash ponawiać inicjalizację z obsługą obu zastanych stanów. W25Q512JV domyślnie startuje w trybie 3-bajtowym; odczyt ADS i ADP jest opisany w Rev G §7.1.10–11, EN4B w §8.2.8. Zmiana ADP w pamięci nieulotnej nie jest wymagana w tym projekcie.

Test odbiorczy powinien pisać różne wzorce w pobliżu 0x00FFFF00 / 0x01000000, 0x01FFFF00 / 0x02000000 i 0x03FFFF00; odczytać po resecie MCU, pełnym power-cycle i wybudzeniu z deep power-down. Są to testy przeciw aliasowaniu adresów, nie dowód uzyskany w obecnym przeglądzie.

Nie używać XIP dla rejestratora, jeśli nie jest potrzebne. Uwzględnić erratę właściwej rewizji krzemu i aktualny nrfx. Przykład: anomaly 215 dotyczy dostępu do części rejestrów po XIP; wymagany ACTIVATE i READY przed takim dostępem. [Nordic — anomaly 215](https://docs.nordicsemi.com/r/bundle/errata_nrf52840_rev3/page/err/nrf52840/rev3/latest/anomaly_840_215.html).

## Katalog JLCPCB / LCSC

Wszystkie poniższe numery są odczytane z katalogów, nie wymyślone. „Montaż potwierdzony” oznacza obecność deklaracji SMT Assembly na publicznej stronie. Dostępność do konkretnego zamówienia trzeba sprawdzić w aktualnym BOM Tool i koszyku; LCSC i magazyn PCBA JLCPCB nie są tym samym.

| Element | Numer | Katalog i montaż | Stan widoczny w źródle |
|---|---|---|---|
| Raytac MDBT50Q-P1MV2, SMD-61P | C5119772 | [JLCPCB](https://jlcpcb.com/partdetail/RAYTAC-MDBT50QP1MV2/C5119772), SMT, Economic and Standard, X-ray required | [LCSC](https://www.lcsc.com/product-detail/Bluetooth-Modules_RAYTAC-MDBT50Q-P1MV2_C5119772.html) Out of Stock; blokada zaopatrzenia przed PCBA |
| ST LSM6DSV32XTR, LGA14 2,5 × 3 | C22461202 | [JLCPCB](https://jlcpcb.com/partdetail/STMicroelectronics-LSM6DSV32XTR/C22461202), **Standard Only**, MSL3, X-ray required | [LCSC](https://www.lcsc.com/product-detail/accelerometers_stmicroelectronics-lsm6dsv32xtr_C22461202.html) pokazał 4537, starsza wersja strony Out of Stock; brak rezerwacji |
| TI BQ25185DLHR, WSON10 2,2 × 2 | C19725033 | [JLCPCB](https://jlcpcb.com/partdetail/TexasInstruments-BQ25185DLHR/C19725033), Economic and Standard, MSL3 | [LCSC](https://www.lcsc.com/product-detail/C19725033.html) 262 w odczytanej wersji; stara strona Out of Stock |
| Winbond W25Q512JVEIQ, WSON8 | C2986165 | [JLCPCB](https://jlcpcb.com/partdetail/WinbondElec-W25Q512JVEIQ/C2986165), Economic and Standard, MSL3 | [LCSC](https://lcsc.com/product-detail/NAND-FLASH_Winbond-Elec-W25Q512JVEIQ_C2986165.html) Out of Stock |
| Ten sam W25Q512JVEIQ, inny rekord dostawy | C7389628 | [LCSC](https://www.lcsc.com/product-detail/C7389628.html); montaż tego rekordu JLC niepotwierdzony | Wersje strony podają 3254 albo 9051; nie uznawać za pewną liczbę |
| Winbond W25Q512JVFIQ, SOIC16 — alternatywa wymagająca zmiany PCB | C2962011 | [JLCPCB](https://jlcpcb.com/partdetail/W25Q512JVFIQ/C2962011), Economic and Standard, MSL3 | Ilość do zamówienia niezweryfikowana |
| TI TPS7A2030PDBVR, 3,0 V 300 mA, SOT23-5 | C963429 | [JLCPCB](https://jlcpcb.com/partdetail/TexasInstruments-TPS7A2030PDBVR/C963429), Economic and Standard, MSL1 | [LCSC](https://www.lcsc.com/product-detail/Linear-Voltage-Regulators-LDO_Texas-Instruments-TPS7A2030PDBVR_C963429.html) 6830 w odczytanej wersji |
| Korean Hroparts TYPE-C-31-M-12 | C165948 | [JLCPCB](https://jlcpcb.com/partdetail/C165948), Economic and Standard, MSL1 | Publiczna strona pokazała 275527, available order qty 266583; zmienne |
| **ST** USBLC6-2SC6, SOT23-6L | C7519 | [JLCPCB](https://jlcpcb.com/partdetail/C7519), Economic and Standard, MSL1 | Bieżący zapas PCBA niepotwierdzony |

Nie stosować automatycznego zamieniania części na podstawie nazw podobnych w katalogu. Przykładowo USBLC6-2SC6 występuje u wielu producentów pod innymi numerami C. Powyższy numer C7519 odpowiada ST.

USB-C pinout producenta: A1/A12/B1/B12 GND; A4/A9/B4/B9 VBUS; A5 CC1, B5 CC2; A6/B6 D+, A7/B7 D−; A8/B8 SBU1/2. [Rysunek Korean Hroparts przez LCSC](https://datasheet.lcsc.com/lcsc/1903211732_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf). Footprint wymaga porównania z tym rysunkiem, w tym otworów mocujących i łączonych padów zasilania.

USBLC6-2SC6 ST: 1 i 6 to I/O1, 3 i 4 I/O2, 2 GND, 5 VBUS. Poprowadzić parę przez odpowiadające sobie pady i krótko do masy przy złączu. [ST DS4260 Rev7](https://www.st.com/resource/en/datasheet/usblc6-2.pdf).

## Wnioski projektowe dla rejestratora — propozycja, nie gotowy firmware

Przy 6 kanałach int16 surowe próbki zajmują 12 B bez znaczników czasu. Przy 1920 Hz to 23040 B/s: 64 MiB pomieści około 48,5 min takiego minimum. Przy zachowaniu dwóch rekordów FIFO po 7 B na próbkę akcelerometr+żyroskop będzie około 41,6 min przed narzutem temperatury, timestampów, metadanych i dziennika. Nie obiecywać godzin zapisu przy 1920 Hz.

Zarezerwować RAM na obsługę flash oraz DMA. Przy maksymalnym 2-sekundowym kasowaniu bloku dopływ danych 1920 Hz to co najmniej 46080 B; FIFO IMU nie wystarczy. Zalecam kasowanie wolnej przestrzeni przed sesją i brak kasowania w krytycznej ścieżce próbkowania. Dodatkowe bufory muszą pomieścić opóźnienia BLE, harmonogramu i zapisu stron. Nie rozpoczynać nowej sesji bez jawnego sprawdzenia dostępnej uprzednio skasowanej przestrzeni.

Zapisywać sesje jako append-only: nagłówek wersji formatu, UID modułu, konfiguracja IMU i filtrów, następnie bloki o stałym rozmiarze z licznikiem sekwencji, liczbą próbek, czasem MCU, czasem IMU i CRC32C. Najpierw dane, potem osobny rekord zatwierdzenia. Dwa naprzemienne obszary metadanych z numerem generacji i CRC umożliwią odzyskiwanie ostatniego poprawnego stanu bez modyfikacji poprzednich sesji. Nagłe odcięcie zasilania może utracić ostatni bufor RAM i aktualnie programowaną stronę; bez podtrzymania nie deklarować utraty dokładnie zero próbek. Wymagane fault-injection testy odcinania zasilania.

Transfer: UUID sesji, offset, długość i CRC każdego bloku; klient potwierdza trwały zapis, a ponowne połączenie kontynuuje od ostatniego potwierdzonego offsetu. Usuwanie sesji tylko jako jawna operacja po weryfikacji pełnego pliku. Synchronizacja obu nóg wymaga oszacowania offsetu i dryftu zegarów z serii wymian czasowych; wspólny BLE START nie jest dokładnym sprzętowym zsynchronizowaniem próbek. Zapisywać kotwice czasowe, identyfikator wspólnej sesji i niepewność dopasowania. Dokładność zmierzyć na stole wspólnym mechanicznym impulsem przed badaniami.

Otwarte przed zwolnieniem produkcyjnym: zaopatrzenie Raytac, aktualna rewizja rysunku EP flash, rzeczywisty BOM Tool JLCPCB dla całego montażu Standard, weryfikacja footprintów i rotacji PnP, power-cycle/adresowanie pełnych 64 MiB, pomiary poboru i czasów kasowania, odporność na zaniki napięcia, realny czas transferu i dokładność synchronizacji.
