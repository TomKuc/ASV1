# Plan prób Flash A1 — W25Q01JVZEIQ, 128 MiB

Data: **2026-10-29**. **Wszystkie próby mają status `NOT_RUN`.** To plan dla przyszłego firmware i prototypów; nie wykonano testów sprzętu, nie zmierzono przepustowości ani odporności na zanik zasilania. Podstawy i otwarte pytania: [audyt zgodności](flash_compatibility_A1.md), dane maszynowe: [JSON](../reports/flash_compatibility_A1.json).

## Warunki i ślad dowodowy

Przed próbami przypiąć SHA aplikacji, bootloadera, SDK/Zephyr/nrfx i konfigurację kompilacji. Potwierdzić oznaczenie IQ oraz dokumentację dostawy. Pozyskać AN0000035 lub równoważne wyjaśnienie producenta; test eksperymentalny C2 nie zastępuje brakującego kontraktu. Używać prototypów i wydzielonego obrazu testowego bez danych badawczych.

Log każdej próby: numer PCB i układu/lot, napięcie i temperatura, zegar QSPI, JEDEC, surowe SFDP, UID obu dies, SR1/2/3 obu dies, adres/długość/opcode, czas polecenia i końca BUSY, wynik API, oczekiwany i odczytany CRC. Zapisać zrzuty logiczne CS/SCK/IO0–3, przebieg VCC przy fault injection oraz surowe obrazy referencyjne na hoście. Pliki wynikowe otrzymują hash i powiązanie z identyfikatorem próby. Wynik `PASS` wymaga sprawdzenia danych, nie wyłącznie braku błędu API.

Do fault injection potrzebne jest kontrolowane źródło zasilania/odcięcie oraz oscyloskop; reset MCU i odcięcie zasilania Flash to różne bodźce. Zasilania USB, baterii i sondy SWD nie mogą niezamierzenie podtrzymywać szyny ani backpowerować przez IO. Zmierzyć napięcie na samym układzie. Nie stosować progów POR innego modelu Winbond.

## Wzorce i adresy

Wypełnienie musi zależeć od **pełnego adresu**, numeru przebiegu i deterministycznego ziarna; samo `00`, `FF` lub powtarzany bufor nie wykryje aliasowania. Zapisać generator i złoty obraz po stronie hosta. Dla bloków stosować CRC32C z jednoznacznymi parametrami: reflected polynomial `0x82F63B78`, init/xorout `0xFFFFFFFF`, odbicie wejścia/wyjścia zgodne z implementacją reflected; wektor `123456789` → `E3069283`. CRC obrazu liczy również niezależny program hosta. Sposób zapisu wartości CRC w pliku zdefiniować jako little endian.

| Granica | Adres B | Znaczenie |
|---|---|---|
| 16 MiB | `01000000` | ujawnia błąd pozostania w 24-bitowym adresowaniu |
| 32 MiB | `02000000` | ujawnia błędy wyższych bitów / niewłaściwej konfiguracji |
| 64 MiB | `04000000` | przejście die 0 → die 1 |
| 128 MiB | `08000000` | koniec wyłączny; adres B nie jest poprawnym adresem danych |

Dla każdej granicy użyć poprawnych adresów spośród `B−1000h`, `B−100h`, `B−4`, `B`, `B+4`, `B+100h`, z odczytem obejmującym obie strony, gdzie to dozwolone. Ostatnie poprawne 4 B to `07FFFFFC–07FFFFFF`. Pozostawić sentinele w odpowiadających sobie offsetach pozostałych regionów i sprawdzać je po każdym zapisie/kasowaniu. Granicę 128 MiB sprawdzać również negatywnie, bez wysyłania niedozwolonych operacji na magistralę.

## Macierz prób

| ID | Próba i wymagany wynik | Status |
|---|---|---|
| F01 | Zimny start: identyfikacja, rozmiar, oba zestawy SR/UID/SFDP; potwierdzenie IQ/QE i trybu adresu przed zapisem. Log obejmuje rzeczywisty start VCC i CS. Niezgodny układ/config blokuje rejestrację. | NOT_RUN |
| F02 | Test C2 na obu dies, najpierw idle. Zrzut ramki `C2 + die byte`, brak adresu/dummy; porównać z AN i implementacją. Po adresowanej operacji sprawdzić zmianę kontekstu. Nie przyjmować samego JEDEC jako dowodu wyboru die. | NOT_RUN |
| F03 | Pełny obraz 128 MiB z unikalnym wzorcem adresowym: programowanie, niezależny readback i CRC per blok oraz całość. Zero aliasów i rozbieżności. Wzorce `00/FF/AA/55` jako dodatkowe przebiegi, po właściwym erase. | NOT_RUN |
| F04 | Osobne próby granic 16/32/64 MiB i końca 128 MiB według tabeli; każdorazowo sprawdzić wszystkie sentinele. Porównać transfery z podziałem i ciągły odczyt przez 64 MiB. Odczyt ciągły włączyć w produkcyjnym API dopiero po udokumentowanym wyniku. | NOT_RUN |
| F05 | Granice strony: długości 1, 2, 3, 4, 255, 256, 257 oraz start na końcu strony. Warstwa dzieli programowanie bez zawinięcia w stronie; żaden sentinel nie zmienia się poza zakresem. Testować też stronę przed granicą die. | NOT_RUN |
| F06 | Wyrównanie: offsety modulo 4 = 0/1/2/3, długości modulo 4, bufory RAM wyrównane i niewyrównane. Oczekiwany jawny błąd albo poprawny bounce buffer; bez cichej zmiany adresu i bez odczytu poza końcem pamięci. | NOT_RUN |
| F07 | Bounds API: `08000000,1`, ostatni bajt z długością 2, zbyt duża długość i przepełnienie `offset+length` oraz długość zero. Odrzucić przed wywołaniem kontrolera; zrzut potwierdza brak nieprawidłowych zapisów/erase. | NOT_RUN |
| F08 | EN4B i ADS: z obu dozwolonych stanów początkowych kontrolera/pamięci, potwierdzić ADS obu dies oraz odczyty powyżej 16/64 MiB. Zmierzyć ramkę i liczbę bajtów adresu. Bez trwałego programowania ADP w normalnym teście. | NOT_RUN |
| F09 | WEL/BUSY/SUS obu dies: migawki przed/po WREN, programowaniu die0, programowaniu die1, WRDI i zapisach statusu w kontrolowanym teście. Oczekiwania szczegółowe ustalić z AN, nie z pojedynczego SR ani analogii do innego modelu. | NOT_RUN |
| F10 | Erase 4/32/64 KiB w każdym die, na skrajach i przy granicy 64 MiB: zawartość FF w celu, nienaruszone sąsiednie sentinele i drugi die. Jeśli driver nie udostępnia 32 KiB, test diagnostycznym poleceniem albo jawnie odnotowane nieobsługiwane API. | NOT_RUN |
| F11 | Chip erase: uprzednio wzorzec w obu dies; sprawdzanie gotowości każdego die i końcowy readback całych 128 MiB = FF. READY/callback rozpoczęcia nie kończy próby. Przewidzieć do 1000 s z tabeli W1 plus zdefiniowany narzut kontroli, bez krótkiego timeoutu wspólnego z PP. | NOT_RUN |
| F12 | Rozbieżność czasów dies: obserwować globalny zapis statusu lub chip erase i sprawdzić, czy pierwszy zakończony die nie zwalnia blokady przed drugim. Jeśli nie wystąpi naturalnie, test oprogramowania ze sztuczną sekwencją SR uzupełnia, ale nie zastępuje próby sprzętowej. | NOT_RUN |
| F13 | Reset MCU przy Flash idle w ADS=1, podczas PP/erase każdego die i podczas DPD. Firmware rozpoznaje stan, nie wysyła bezmyślnie resetu/kolejnego erase i odzyskuje tylko zatwierdzone dane. Zmierzyć, czy VCC Flash nie zanikło. | NOT_RUN |
| F14 | Software reset przy obu dies idle: `66`, `99`, odstęp i czas recovery; odczyt obu SR po resecie, ponowna inicjalizacja i brak aliasowania. Negatywny test resetu podczas BUSY/SUS wyłącznie na danych testowych: oczekiwane możliwe uszkodzenie operacji, nigdy deklaracja jej powodzenia. | NOT_RUN |
| F15 | DPD/wake: wejście tylko po idle obu dies, `B9`, `AB`, wymagane opóźnienia; odczyt obu SR i danych po wake oraz po resecie MCU w DPD. Potwierdzić zachowanie ADS/statusu z FAQ i ustalić kontekst C2. Próba wysłania niedozwolonej operacji podczas DPD nie może zostać uznana za wykonany zapis. | NOT_RUN |
| F16 | Niepełny POR/brownout: kontrolowane zaniki różnej głębokości i długości, pomiar VCC/CS. Po stanie niepewnym driver zgłasza błąd albo przechodzi zweryfikowane odzyskiwanie; nigdy nie zakłada POR tylko dlatego, że MCU się zresetował. | NOT_RUN |
| F17 | Utrata zasilania przy danych strony, zatwierdzeniu bloku, każdej kopii metadanych i erase, osobno w die0 i die1 oraz przy granicy. Losować momenty i odtwarzać zapisane przypadki. Po restarcie brak fałszywie zatwierdzonych bloków, poprawny CRC każdej odzyskanej sesji i rozpoznane uszkodzone/niepełne obszary. | NOT_RUN |
| F18 | Pełna pamięć, błąd/timeout kontrolera i przerwany transfer: brak nadpisania wcześniejszych sesji, jednoznaczny błąd, wznowienie eksportu z offsetem i CRC; hash hosta zgodny z obrazem urządzenia. | NOT_RUN |
| F19 | Długi zapis i odczyt z aktywnym BLE i maksymalnym profilem IMU: pomiar czasu każdej strony, maksimum kolejek RAM/FIFO, liczby luk i throughput. Przestrzeń skasowana przed sesją; brak erase na ścieżce krytycznej. Powtarzać przez dolny i górny die. | NOT_RUN |
| F20 | Kwalifikacja elektryczna: zegary 2/4/8/16/32 MHz jako plan przemiatania, napięcia i temperatury w zadeklarowanym zakresie produktu oraz stany USB/baterii. CRC całego obrazu, timing, ringingi i poziomy napięć na układzie. Zatwierdzić wyłącznie rzeczywiście sprawdzone prędkości i marginesy; 32 MHz nie jest jeszcze kwalifikowane. | NOT_RUN |

## Kolejność i kryteria zakończenia

Najpierw zamknąć kontrakt producenta i przypiąć kod, następnie F01/F02/F06/F07/F08 przy niskim zegarze. Dopiero potem dopuszczać destrukcyjne F03–F17. Rejestrować także błędy i nieudane próby; powtórzenie po poprawce otrzymuje nowy identyfikator i wersję firmware.

Każdy odczyt, zapis oraz erase wymaga odróżnienia: zakończony transfer kontrolera, zakończona operacja każdego die, sprawdzone dane i zatwierdzona struktura sesji. Źródłem interpretacji READY jest [Nordic QSPI — Erase operation i STATUS](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/qspi.html), a źródłami kontraktu pamięci są W1 i docelowo AN0000035 wskazane w [audycie](flash_compatibility_A1.md).

Do zwolnienia firmware wymagane są: rozstrzygnięte pytania AN, wszystkie używane funkcje z udokumentowanym PASS, brak aliasów/niezgodności CRC, brak zapisu poza zakresem i brak fałszywego zatwierdzenia po przerwaniu zasilania. Nie muszą przetrwać niezatwierdzony bufor RAM ani właśnie programowana strona; straty muszą być wykryte i opisane. Każdy timeout pozostawia wynik operacji jako niepewny do weryfikacji, zamiast automatycznego powtórzenia zapisu w to samo miejsce.

Plan nie narzuca nieudowodnionej liczby powtórzeń ani poziomu niezawodności. Przed wykonaniem ustalić macierz liczby egzemplarzy/lotów, warunków i powtórzeń stosownie do celu badań. Liczba cykli i retencja wymagają osobnej kwalifikacji; kilka przebiegów całej pamięci nie dowodzi katalogowej trwałości.
