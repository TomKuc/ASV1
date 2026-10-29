# W25Q01JVZEIQ — audyt zgodności A1

Stan przeglądu: **2026-10-29**, repozytorium [TomKuc/ASV1](https://github.com/TomKuc/ASV1), baza `c3536966d15fab3ada32515650615b947dce1349`. Zachowano wybór **128 MiB W25Q01JVZEIQ**. Nie zmieniano schematu ani PCB. Nie istnieje jeszcze przypięty do projektu, uruchomiony firmware; nie przeprowadzono prób sprzętowych.

**Wniosek: istnieją zgodne mechanizmy transmisji, lecz obsługa całych 128 MiB pozostaje warunkiem kwalifikacji firmware.** Należy wdrożyć i sprawdzić warstwę obsługującą dwa dies. Samo `address-size-32` oraz pozytywny DRC nie potwierdzają jej działania. Brakuje pełnej noty AN0000035 i wyników planu [prób A1](flash_firmware_test_plan_A1.md). Tabela maszynowa rozdziela fakty, otwarte pytania i odrzucone założenia: [JSON](../reports/flash_compatibility_A1.json).

## Dokumenty i granice dowodu

| ID | Źródło pierwotne i zakres odczytu |
|---|---|
| W1 | [Winbond W25Q01JV, Rev E, 2024-03-04; dokument producenta udostępniony przez Mouser](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf): część non-DTR, oznaczenie IQ. Rozdziały podano według nagłówków treści, gdyż spis treści ma inne numery; strony według numeracji drukowanej. Nie potwierdzono, że jest to najnowsza rewizja dla przyszłej dostawy. |
| W2 | [Oficjalny katalog not Winbond](https://www.winbond.com/hq/support/documentation/?__locale=fr&category=%2F.categories%2Fresources%2Fapplication-note%2F&family=%2Fproduct%2Fcode-storage-flash-memory%2Fserial-nor-flash%2Findex.html&line=%2Fproduct%2Fcode-storage-flash-memory%2Findex.html&pno=W25Q01JV): AN0000035, *W25Q01JV SpiFlash Stacked Die Usage v1.0*, 2023-08-03, format `contact us`. |
| W3 | [Oficjalny punkt pobierania AN0000035](https://www.winbond.com/hq/support/documentation/downloadV2022.jsp?__locale=en&xmlPath=/support/resources/.content/item/DA01-AN0000035.html&level=4): uzyskano stronę HTML, bez treści noty. **Nie przeczytano AN0000035.** |
| W4 | [Winbond Technical FAQ](https://www.winbond.com/hq/support/faq/technical/index.html): pytania o Two Die Stack Operations, status po `ABh`, zapis statusu przez `50h` i reset po niepełnym zaniku zasilania. Informacje ogólne o Serial NOR nie zamykają wszystkich szczegółów tego stosu dies. |
| N1 | [Nordic nRF52840 Product Specification — QSPI](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/qspi.html): *Configuring peripheral*, *Erase operation*, *Instruction set*, `IFCONFIG0`, `ADDRCONF`, `STATUS`, `CINSTRCONF`, *Long frame mode*, `DPMDUR`. |
| Z1 | [Zephyr `drivers/flash/nrf_qspi_nor.c`, `main`](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/drivers/flash/nrf_qspi_nor.c): odczyt kodu 2026-10-29; 1401 linii w odczytanej reprezentacji. To ruchoma gałąź, bez ustalonego SHA i bez wyboru jej jako SDK projektu. |
| Z2 | [Binding `nordic,qspi-nor.yaml`, `main`](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/dts/bindings/mtd/nordic,qspi-nor.yaml) i [binding wspólny](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/dts/bindings/mtd/jedec,spi-nor-common.yaml): właściwości konfiguracji, bez gwarancji obsługi każdego pola przez każdy driver. |
| Z4 | [Zephyr `jedec,jesd216.yaml`, `main`](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/dts/bindings/mtd/jedec,jesd216.yaml): odziedziczone `size` oznacza pojemność w bitach. Nie utożsamiać go z liczbą bajtów API. |
| N2 | [Nordic nrfx `drivers/src/nrfx_qspi.c`, `master`](https://raw.githubusercontent.com/NordicSemiconductor/nrfx/master/drivers/src/nrfx_qspi.c): odczyt 2026-10-29, 944 linie; gałąź ruchoma, nieprzypięta do projektu. |
| L1 | [Linux **v6.17**, `drivers/mtd/spi-nor/winbond.c`](https://raw.githubusercontent.com/torvalds/linux/v6.17/drivers/mtd/spi-nor/winbond.c): `WINBOND_NOR_SELDIE_OP`, `winbond_nor_select_die`, `winbond_nor_multi_die_ready`, wpis JEDEC `ef 40 21`. Jest to dowód implementacji innego kontrolera, nie test nRF52840. |

Nie zastępowano dokumentacji IQ dokumentem DTR/IM ani opisem W25M, W25Q02JV, W25Q512JV lub NAND.

## Fakty adresowe i polecenia

Poniższe dane liczbowe pochodzą z W1 §1, §6.1, §6.3.1–5, §6.4.6–7 i §7.6. Mapa bajtowa wynika z podanej organizacji pamięci.

| Parametr | Wartość |
|---|---|
| Pojemność / organizacja | 134217728 B = 128 MiB; 2 × 64 MiB |
| Dolny / górny die | `00000000–03FFFFFF` / `04000000–07FFFFFF` |
| Pierwszy adres niedozwolony | `08000000` |
| JEDEC IQ | `EF 40 21` |
| Strona / kasowanie | 256 B / 4, 32, 64 KiB; chip erase |
| Rejestry SR1 / SR2 / SR3 | `05` / `35` / `15` |
| EN4B / EX4B | `B7` / `E9` |
| WREN / WRDI | `06` / `04` |
| DPD / wake / reset | `B9` / `AB` / `66`, potem `99` |
| Software Die Select | `C2`, jeden bajt Die ID; pełne zasady → AN0000035 |
| Tryb czterobajtowy, kandydat nRF | `6B` read, `32` program, `20` 4 KiB erase, `D8` 64 KiB erase |
| Dedykowane opcodes 4B | `6C` / `34` / `21` / `DC`; inny mechanizm niż EN4B |
| IQ QE / ADS / ADP | QE=1 ustalone; ADS=bieżący tryb adresu; ADP=nieulotny tryb po POR/reset, domyślnie 0 |
| Odczyt, W1 §7.6 przypis 6 | adres startowy wyrównany do 4 B |
| Zasilanie, W1 §7.2, s.74 | 2,7–3,6 V; wymagane również podczas programowania i erase |

W1 §6.3.2–3, s.23, rozróżnia status/UID/SFDP podążające za kontekstem die oraz polecenia bez adresu przyjmowane przez oba dies. §6.1, s.13, uzależnia wspólny zapis rejestrów od braku zajętości obu dies. BUSY i SUS są niezależne; dokładny kontrakt WEL i przełączania kontekstu pozostaje niepełny bez AN.

**Nie wynika z tego konieczność `C2` przed każdym liniowym odczytem lub zapisem.** Problemem jest kontrola stanu, zwłaszcza po poleceniach wspólnych. L1 jawnie wysyła `C2 + 00` i `C2 + 01`, bez adresu i dummy bytes, następnie sprawdza SR każdego die; dla `EF4021` instaluje taką funkcję gotowości. Nie wysyła WREN w samej funkcji wyboru die. To wiarygodny punkt wyjścia implementacji, ale nie pełna specyfikacja dopuszczalności C2 podczas BUSY/SUS. [Linux v6.17, funkcje L1](https://raw.githubusercontent.com/torvalds/linux/v6.17/drivers/mtd/spi-nor/winbond.c).

W1 §6.4.8, s.32, dopuszcza sekwencyjny dostęp do całej pamięci. W odczytanej rewizji nie znaleziono jawnego nakazu kończenia każdego odczytu na 64 MiB. Dzielenie odczytów na tej granicy można przyjąć jako ostrożną politykę pierwszego sterownika; nie przedstawiać jej jako potwierdzonego ograniczenia układu. Odczyt ciągły przez granicę wymaga próby porównawczej. Programowanie należy dzielić na granicach stron; duży transfer kontrolera nie usuwa potrzeby poprawnej kontroli stanów.

## Co zapewnia nRF52840 i czego nie zapewnia driver

Nordic udostępnia 24/32-bitowe adresowanie, zgodne `6B`/`32` i custom instructions, w tym długie ramki. `ADDRCONF` może wysłać instrukcję wejścia w 4B: opcode resetowo `B7`, ale tryb resetowo `NoInstr`; osobne pola kontrolują WREN i WIPWAIT. Zatem EN4B nie musi być oddzielnym wywołaniem custom instruction, lecz konfiguracja i stan zewnętrznej pamięci muszą się zgadzać. Sprzętowy zestaw opcodes nie daje swobodnej podmiany `6B` na `6C`. `READY` po rozpoczęciu erase nie oznacza ukończonego kasowania. `STATUS.SREG` jest jednym odczytem statusu, bez gwarancji agregacji dwóch dies. [N1, *Instruction set*, *Erase operation*, `ADDRCONF`, `STATUS`](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/qspi.html).

Przegląd Z1: linie 173–178 i 667–680 obsługują EN4B, a 1381–1383 wybierają 32-bitowe adresy. `qspi_wait_while_writing()` (467–485) czyta SR1 bez pętli po dies. `configure_chip()` (611–683) operuje na pojedynczym kontekście statusu; w odczytanym pliku nie znaleziono C2 ani obsługi die. **Nie jest to dowód gotowej obsługi stosu W25Q01JV.** [Kod Z1](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/drivers/flash/nrf_qspi_nor.c).

Binding Z2 domyślnie ustawia `S1B6` jako wymaganie QE. Tego ustawienia nie wolno odziedziczyć bez analizy IQ. Kandydat to jawne `NONE` dla automatycznej modyfikacji QE oraz osobne potwierdzenie SR2.QE obu dies; IQ ma QE ustalone. Alternatywna ścieżka SR2 musi odpowiadać sprawdzonemu SFDP i wybranej wersji drivera. Rozmiar widziany przez API to **134217728 bajtów**. W odczytanym bindingu **`nordic,qspi-nor`** należy wybrać dokładnie jedno pole: `size = <1073741824>` **w bitach** albo `size-in-bytes = <134217728>` **w bajtach**, jeżeli przypięta wersja je obsługuje. Nie wpisywać liczby bajtów do `size`. Z1 linie 65–76 przeliczają `size/8` i zabraniają podania obu pól. [Binding Z2, linie 19–26](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/dts/bindings/mtd/nordic,qspi-nor.yaml).

Dla transportu **`jedec,spi-nor`** odziedziczone `size` jest także wyrażone w bitach; nie przenosić automatycznie rozszerzenia `size-in-bytes` z bindingu Nordic. Odczytany binding wspólny Z4 go nie deklaruje. W każdym przypadku sprawdzić schemat i kod **wybranej, przypiętej wersji SDK**. Pozostałe warunki nRF QSPI to `address-size-32`, EN4B, `read4o`, `pp4o` i strona 256 B. To **lista warunków konfiguracji**, nie gotowy, przetestowany devicetree. Sama obecność odziedziczonego `use-4b-addr-opcodes` nie zapewnia, że nRF QSPI go obsłuży. [Binding wspólny Z4, linie 22–24](https://raw.githubusercontent.com/zephyrproject-rtos/zephyr/main/dts/bindings/mtd/jedec,jesd216.yaml).

N2 `nrfx_qspi_mem_busy_check()` (643–669) wykonuje jeden `05` i sprawdza jeden WIP; funkcje read/write przyjmują adres `uint32_t` (716–735). Transport custom instruction umożliwia ramkę C2 z bajtem die. Trzeba dodać politykę wyboru, odczytu i interpretacji obu statusów. Ograniczenia DMA/wyrównania oraz zachowanie callbacków sprawdzić w **przypiętym** SDK, wraz z obejściami errata właściwego SoC. Nie utożsamiać zakończenia DMA, końca BUSY i trwałego zatwierdzenia sesji. [Kod N2](https://raw.githubusercontent.com/NordicSemiconductor/nrfx/master/drivers/src/nrfx_qspi.c).

## Reset, zasilanie i wybudzenie

| Zdarzenie | Wymagana polityka projektu — do implementacji i próby |
|---|---|
| Pełny POR Flash | Potwierdzić prawidłowy ramp/CS, odczekać rozruch, odczytać identyfikację i oba SR; zestawić ADS z ADP oraz ustawieniami kontrolera. |
| Reset samego MCU | Traktować Flash jako urządzenie o zastanym stanie: może nadal pracować, mieć ADS=1 albo być w DPD. Reset MCU nie jest dowodem POR Flash. |
| `66`, następnie `99` | Nie stosować automatycznie w każdej ścieżce boot. Najpierw ustalić BUSY/SUS obu dies; reset w trakcie operacji może uszkodzić jej dane. Po resecie odtworzyć konfigurację i potwierdzić oba statusy. |
| `B9` / `AB` | Wchodzić w DPD wyłącznie po wyciszeniu obu dies i zakończeniu operacji kontrolera. Po wybudzeniu sprawdzić statusy oraz zgodność trybu; nie traktować AB jako POR. |
| Brownout / krótki zanik | Zatrzymać nowe zapisy, odzyskiwać dziennik bez zapisu w niepewnym napięciu. Jeśli nie da się wiarygodnie ustalić stanu, zgłosić błąd i zachować dane; nie udawać skutecznego resetu zasilania. |

Źródła: W1 §6.4.34–35, s.58–59; §6.4.50, s.73; §7.3, s.75; W4 pytania o AB i POR. WSON8 IQ nie udostępnia dedykowanej linii RESET. FAQ deklaruje zachowanie rejestrów statusu po AB; szczegóły kontekstu C2 i obu dies należy nadal potwierdzić. Pomiary rampy, CS i spadków napięcia są konieczne na prototypie. Nie przenosić parametrów POR innego modelu z FAQ na ten układ.

Nominalna szyna 3,0 V ani próg resetu MCU poniżej 2,7 V nie gwarantują poprawnego zapisu Flash. Strategia zatrzymania zapisu i zachowanie dziennika muszą uwzględniać rzeczywiste napięcie na pamięci, zapas dla operacji już rozpoczętej oraz możliwość nagłego odcięcia. Wewnętrzny próg write-inhibit VWI nie zastępuje dolnej granicy pracy z §7.2.

Punkty odniesienia czasowego z W1 §7.3/§7.6: `tVSL=20 µs`, `tPUW=5 ms`, `tDP=3 µs`, `tRES1=3 µs`, `tRES2=1,8 µs`, `tRST=30 µs`; maksima PP 3,5 ms, erase 4 KiB 400 ms, 32 KiB 1,6 s, 64 KiB 2 s, chip erase 1000 s. Przed kodowaniem ponownie sprawdzić tabelę dla rzeczywistej rewizji dostawy. Timeout interfejsu i limit całej operacji to oddzielne mechanizmy; nie przyjmować jednego krótkiego timeoutu dla wszystkich erase.

## Proponowana własna warstwa Flash

Jeden właściciel kontrolera i jedna blokada obejmują pełne polecenie, wybór die oraz polling. Sterownik rodzajowy i własny kod C2 nie mogą równolegle zmieniać kontekstu. Rejestracja nie korzysta z XIP tej pamięci. Na początku wyłączyć automatyczny DPD oraz suspend/resume; włączyć je dopiero po osobnej kwalifikacji.

Interfejs warstwy powinien zawierać `probe`, `read`, `program_page`, `erase`, `wait_all_idle`, `read_die_status`, `sleep`, `wake` i diagnostyczny `recover`. Każda operacja zwraca stan końcowy albo jawny błąd wraz z die, adresem, SR1/2/3 i etapem. Granice sprawdzać jako `offset <= capacity && length <= capacity-offset`, przed zwężeniem typów; zdefiniować długość zero. Czytanie niewyrównane realizować przez wyrównany bufor pomocniczy albo jawnie odrzucać zgodnie z kontraktem API.

Pierwsza wersja powinna serializować operacje i sprawdzać oba dies przed poleceniami wspólnymi oraz po ich zakończeniu. Dla najprostszej polityki można wymagać obu dies idle także między pojedynczymi zapisami stron. Nie używać samego `WIPWAIT` kontrolera jako zamiennika `wait_all_idle`. Sposób wykonania C2 podczas BUSY oraz ustawienia WIPWAIT dla samego selektora pozostają warunkiem AN/prototypu — niewłaściwe automatyczne oczekiwanie może zablokować sondowanie drugiego die.

Nie programować nieulotnego ADP tylko po to, aby ominąć inicjalizację B7. Bootloader, aplikacja i odzyskiwanie muszą uzgodnić ten sam kontrakt; po każdym resecie sprawdzać zastany ADS obu dies. Nie pisać rejestrów ochrony „na ślepo”. UID i SFDP archiwizować jako surowe odczyty z identyfikacją wybranego die i ramki SPI; parsowanie SFDP nie zastępuje wiedzy o stosie.

Nad sterownikiem umieścić dziennik append-only z wersją formatu, numerem sekwencji i CRC, osobnym zatwierdzeniem po danych oraz dwiema kopiami metadanych. Projekt musi zdefiniować ograniczenia ponownego programowania strony; nie zakładać dowolnej liczby dopisków w tę samą stronę. Zakończenie BUSY nie jest rekordem zatwierdzenia sesji, a CRC nie naprawia przerwanego erase. Kasować zapas przestrzeni przed treningiem; szybkość zapisu stron i budżet buforów sprawdzić pomiarem.

## Pytania blokujące zamknięcie zgodności

Do AN0000035 albo równoważnego, pisemnego wyjaśnienia Winbond należy odnieść następujące punkty:

1. C2: wartości Die ID, dopuszczalność podczas BUSY/SUS, czas od CS do następnego polecenia i trwałość wyboru po adresowanej operacji, DPD, resetach oraz POR.
2. WEL: stan i zerowanie każdego die po wspólnym WREN/WRDI, zapisie do jednego die oraz operacji status/globalnej; co dzieje się, gdy tylko jeden die jest zajęty.
3. ADS/QE/status: zakres rozsyłania i warunki przyjęcia poleceń wspólnych, odczyt obu dies i możliwe rozbieżności przejściowe; kompletna sekwencja bezpiecznego resetu i wake.
4. UID/SFDP: dokładne ramki oraz kontekst; tabelę UID i opis instrukcji porównać z rysunkiem oryginalnego PDF i potwierdzić na analizatorze. Nie rozstrzygnięto różnicy liczby pól dummy w ekstrakcji tekstu tabeli.
5. Niezależnie od AN: przypiąć wersje SDK/drivera/bootloadera, przejrzeć ich kod i errata, uruchomić pełny plan A1. Zaliczenie próby kilku pierwszych MiB nie kwalifikuje 128 MiB.

**Status końcowy: dokumentacja i plan testów gotowe; zgodność kompletnego firmware oraz sprzętu niepotwierdzona.** Nie stwierdzono udokumentowanej przeszkody wymagającej wymiany W25Q01JVZEIQ, ale pozostają otwarte warunki jego poprawnego użycia.
