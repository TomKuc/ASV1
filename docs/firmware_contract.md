# Wymagania firmware i prób odbiorczych

To specyfikacja dla przyszłego firmware. Nie zaimplementowano ani nie uruchomiono kodu na sprzęcie.

## Akwizycja

Konfiguracja ODR120/240/480/960/1920Hz zgodnie z trybem IMU; niezależne FS i filtry zapisane wraz z surowymi rejestrami konfiguracji. Start po self-test/WHO_AM_I i sprawdzeniu FIFO; zmiana konfiguracji na granicy nowej sesji albo z jawnym rekordem zmiany. ±4000°/s wymaga właściwego trybu OIS. Znacznik32-bit ma typowy krok21.75µs; należy rozwinąć przepełnienia i kalibrować relację do czasu MCU. Temperatura IMU jest temperaturą układu, nie ogniwa.

Przechwytywać INT przez GPIOTE/PPI do TIMER, a nie czas wejścia do ISR. Używać FIFO watermark i SPI DMA. Przechowywać tagi FIFO, zgłoszenia overrun, numery bloków i licznik odebranych próbek. Flaga overrun potwierdza lukę, ale sama nie podaje dokładnej liczby utraconych próbek. Dodać rekord luki z informacją, co wiadomo i czego nie wiadomo. Wyłączyć nieużywane funkcje sensory-hub/Qvar/OIS zgodnie z połączeniami PCB.

## Flash

W25Q01JVZEIQ128 MiB ma dwa dies. Sam ADDRMODE32 nie wystarcza: potrzebny sprawdzony sterownik z obsługą stanów obu dies, EN4B i sekwencji resetowania. Pozyskać AN0000035 albo równoważne kompletne wyjaśnienie producenta. Sprawdzić QE/ADS, JEDEC/SFDP, BUSY/SUS/WEL oraz granice matryc. Obsługa deep power-down musi zachować spójność sterownika. Nie przełączać globalnych statusów w środku sesji.

Skasować wymaganą przestrzeń przed startem. Kasowanie bloków w ścieżce rejestracji może trwać sekundy i przekroczyć pojemność FIFO/RAM. Rejestrator musi odmówić rozpoczęcia sesji, jeśli nie ma wystarczającej wolnej skasowanej przestrzeni. RAM obejmuje oddzielne bufory DMA/FIFO i kolejkę stron Flash, a budżet musi uwzględniać BLE oraz najgorsze czasy zapisu z aktualnej dokumentacji128 MiB.

Sesja: wersjonowany nagłówek z UID, stroną ciała, konfiguracją, osią/montażem, kalibracją i identyfikatorem wspólnego treningu. Dane append-only w blokach z długością, numerem sekwencji, czasem MCU/IMU i CRC32C. Rekord zatwierdzenia programowany po danych, w osobnym miejscu z uwzględnieniem zasad programowania strony producenta. Dwa naprzemienne obszary metadanych z CRC i generacją. Nowa operacja nie nadpisuje jedynej kopii poprzedniej metadanej.

Po awarii odzyskiwać tylko zatwierdzone bloki; ostatni bufor RAM i programowana strona mogą zostać utracone. Testować przerwanie zasilania w każdym etapie programowania, aktualizacji metadanych i kasowania. CRC wykrywa uszkodzenie, ale go nie naprawia.

## Czas obu nóg i transfer

Wyznaczać offset, dryft i niepewność z wielu wymian czasowych; ponawiać kotwice przed/po sesji i w czasie, jeśli dostępne BLE. Jednoczesna komendaSTART nie gwarantuje jednoczesnej próbki. LFXO stabilizuje zegarMCU; IMU nadal ma osobny zegar. Dopasować oba zegary do wspólnej osi czasu i udostępniać jakość dopasowania w danych.

Pobieranie: UUID sesji+offset+długość+CRC bloku, potwierdzenie trwałego zapisu klienta i wznowienie od ostatniego potwierdzonego offsetu. Końcowy hash całego pliku; kasowanie tylko osobną jawną komendą. Połączenie BLE i parowanie powinny chronić przypadkowe zdalne sterowanie/kasowanie. Pomierzyć przepustowość i czas pobrania całych128 MiB; nie wyliczać go z nominalnego2M PHY. USB data stanowi zapasową drogę transferu, wymagającą własnej implementacji i USB suspend.

## Zasilanie i temperatura

P1.14/CHG_INHIBIT: HIGH włącza Q2 i blokuje ładowanie; LOW albo HiZ umożliwia decyzję sprzętowemu oknu. GPIO steruje osobnym tranzystorem i nie może nadpisać alarmu U7/U8. Ochrona temperatury ma działać bez MCU; supervisor blokuje zezwolenie przed ustaleniem odniesień. Przy USB suspend firmware blokuje ładowanie i ogranicza obciążenie; zgodność wymaga także rozwiązania poboru samej ładowarki i systemu. Zatrzymanie zapisu przy niskim napięciu, watchdog i POF nie zastępują odpornego dziennika.

### USB: budżet całego portu

BQ25185 ogranicza prąd swojego wejścia IN. Ustawienie nominalne 100 mA nie obejmuje bezpośredniej gałęzi VBUS do modułu ani odbiorów przed IN. nRF52840 zasila z VBUS osobny regulator interfejsu sygnalizacyjnego USB; pozostała logika USBD korzysta z głównej szyny. Jest to rzeczywista gałąź poboru prądu, nie tylko bezprądowa detekcja kabla. [Nordic: POWER — USB supply](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html), [TI BQ25185 — power path i limit wejścia](https://www.ti.com/lit/ds/symlink/bq25185.pdf).

Wymagane są analiza i pomiar prądu **na złączu USB**, uwzględniające tolerancję limitu BQ, system i ładowanie za BQ, gałąź modułu VBUS, pozostałe obciążenia/upływy oraz ładowanie pojemności przy wpięciu. Firmware ma obsługiwać obecność/usunięcie VBUS, gotowość regulatora USB, enumerację, transfer, suspend i wznowienie. Ma stosować sekwencję uruchomienia producenta i dostosowywać aktywność oraz ładowanie do rzeczywiście uprawnionego budżetu źródła. Same Rd ani niezweryfikowana konfiguracja deskryptora nie potwierdzają uprawnienia do wyższego poboru.

Kwalifikacja obejmuje wpięcie i rozruch, stan przed konfiguracją, transfer z jednoczesnym obciążeniem/ładowaniem, suspend/resume, odłączenie i różne stany baterii. Zmierzyć prąd ustalony i impulsowy/inrush oraz napięcia. CHG_INHIBIT wyłącza ładowanie, ale nie odłącza SYS ani VBUS modułu. Jeśli obecny sprzęt nie spełni wymagań danego stanu USB, pozostaje to warunkiem sprzętowym; deklaracja firmware go nie zamyka. Nie przyjęto niezweryfikowanych wartości prądu suspend ani automatycznego przejścia do wyższego limitu źródła.

## Odbiór prototypu

1. Odczyt identyfikatorów, self-test IMU, wszystkie ODR/FS, temperatura i obciążenie FIFO.
2. QSPI wzorce wokół16/32/64MiB oraz końca128MiB; brak aliasowania po resetach i power-cycle.
3. Wielogodzinny soak test z maksymalnym ODR i jednoczesnym ruchem BLE; udokumentowany licznik luk.
4. Fault injection: odcięcia zasilania, resetMCU przy zajętej pamięci, pełna pamięć, przerwany transfer.
5. Synchronizacja dwóch płytek wspólnym impulsem mechanicznym; offset, dryft, jitter i niepewność po całej sesji.
6. Pomiar szumu i biasu po reflow, po zamknięciu obudowy oraz na nodze; test saturacji podczas biegu.
7. Pomiary energii, minimalnych napięć, ładowania, temperatur ogniwa i całego oknaNTC z przerwą/zwarciem.
