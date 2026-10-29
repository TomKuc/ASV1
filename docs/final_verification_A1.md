# Ankle Sensor V1 A1 — końcowa weryfikacja prototypów, 29.10.2026

**Decyzja: CONDITIONAL READY dla 3–5 prototypowych PCBA.** Nie wykryto pozostawionego błędu połączeń wymagającego przeprojektowania A1. Przed zamówieniem trzeba zamknąć cztery konkretne pozycje A poniżej. Testy wymagające gotowej płytki są klasą B, a nie warunkiem wykonania prototypów. Nie złożono zamówienia, rezerwacji ani zlecenia montażu.

Jedynym bieżącym źródłem jest katalog `hardware/` wraz z **Ankle_Sensor_V1.kicad_dru** i `manufacturing_profile_A1.json`. Indeks źródeł i eksportów: [current_A1_manifest.json](../reports/current_A1_manifest.json). Bieżący PCB SHA256: `cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`.

## Wyniki i rozstrzygnięcie uwag

| Uwaga / lokalizacja | Wynik, źródło i decyzja |
|---|---|
| HiZ / U3.7, R24, Q2, Q1, U1.4 | Zarzut jest nieaktualny dla wejściowego HEAD28d88f2. R24 już łączy gate Q2 z3V0 przez100k, a aktualny kontrakt mówił HiZ=inhibit. Zweryfikowano to z natywną netlistą i padami. Doprecyzowano kontrakt dla hang LOW oraz GPIO zachowanych przy System OFF. Brak zmiany hardware ładowarki. [Stanów i źródeł TI/Nordic](charge_startup_final_A1.md). |
| Martwa bateria / U1.SYS→U2.EN/IN→U3 | Według BQ25185 IN zasila SYS także z pustą baterią; /CE blokuje BAT charge, a nie tę drogę. Nie ma cyklicznego sprzętowego deadlocku „MCU musi najpierw naładować baterię, żeby wystartować”. Brak firmware blokuje ładowanie, ale nie zasilanie z USB i programowanie przez SWD. Ważne IN i limit prądu są konieczne; rozruch dynamiczny jest testem B. [TI §6.1 i tabela stanów](charge_startup_final_A1.md). |
| PCM-open / J2 | Odzyskanie zależy od specyfikacji pakietu. NTC musi wracać do PACK− także przy odłączonym PCM. Gotowy pakiet odniesiony do odłączanego raw B− może być niezgodny. Nie obchodzić PCM/NTC. Brak MPN baterii dotyczy zespołu końcowego, a nie automatycznego montażu PCB. |
| Sterowanie programowe / timer | HIGH/HiZ przed System OFF i najwcześniej w aplikacji/bootloaderze; OUT=HIGH przed DIR=OUTPUT. Watchdog przed LOW, bez bezwarunkowego karmienia w ISR. Po awarii fault latch i skończona procedura recovery, bez pętli restartów /CE zerującej timer. Hang LOW nie jest resetem; okno sprzętowe nadal ma pierwszeństwo. To wymagania przyszłego firmware, nie wykonany kod. |
| Dwa poprzednie hashe / repo | `b5487d09…` jest bazą c353696 sprzed audytu; `38545441…` jest audytowaną A1 z20dd2667, skopiowaną następnie do lokalnego28d88f2. Wszystkie ścieżki dawnego commita odpowiadały lokalnym plikom. Obecny `cdcbd234…` dodaje wyłącznie zmianę18 szerokości USB. Historyczne raporty/ZIP zachowano i oznaczono, zamiast podmieniać ich dawne wyniki. [Pochodzenie](../reports/provenance_final_A1.json). |
| GitHub | Lokalna gałąź i cache origin/master wskazują28d88f2; to nie jest bieżące potwierdzenie serwera. `git ls-remote` nie zadziałał z powodu DNS, publiczny widok był historyczny, a strony dokładnych commitów nie dały potwierdzenia. Nie deklarujemy synchronizacji ani obecności20dd2667 lub nowego commita na GitHubie. [Wynik próby](../reports/github_verification_final_A1.json), [import i weryfikacja](github_delivery_final_A1.md). |
| U3 VDD/VDDH/VBUS/DCCH | Wspólne3V0 na VDD/VDDH odpowiada normal voltage mode; DCCH pozostaje NC przy nieużywanym REG0, VBUS jest osobnym zasilaniem PHY. Potwierdzają Nordic POWER i oficjalne wsparcie. Nie zmieniono topologii. Literalny obraz Raytac§8.3 pozostaje pozycją A01. [Raport USB](usb_stackup_final_A1.md). |
| USB series R / U3 PHY | Oficjalne wsparcie Nordic potwierdza wewnętrzne elementy PHY; brak podstaw do dodania zewnętrznych22/27Ω. Nie dodano ich. |
| U6 / ESD | Zachowano wcześniejszą relokację. J1→U6: DP12.997mm, DN15.552mm. Pinmapa USBLC6-2SC6 odpowiada ST; GND pad→via0.938mm z połączeniem do In1. Pozostałe odcinki i pętle nie są idealne. Parametry samego ESD nie są wynikiem IEC całej PCB; test ESD jest B. [ST DS4260](https://www.st.com/resource/en/datasheet/usblc6-2.pdf). |
| Stack / USB In2 | Wybrano konkretny opublikowany **JLC7628 4L/1.0mm nominalnie, outer1oz/inner0.5oz**. pp0.2104/core0.400/pp0.2104mm, Cu0.035/0.0152/0.0152/0.035mm. Tabela i obecne Dk mają rozbieżności wymagające potwierdzenia zamówienia; nie zastąpiono ich zgadywanymi grubościami w KiCad. [Oficjalna tabela JLC](https://cart.jlcpcb.com/client/template/placeOrder/impedance.html), [obliczenia i ograniczenia](usb_stackup_final_A1.md). |
| Minimalna korekta USB | Model2D dla0.15/0.15 dawał101.79Ω względem In1. Poszerzono tylko18 odcinków wspólnego trunku In2 do0.17mm, bez ruchu środka; gap0.13mm. Wynik modelu:94.14Ω GND-only,87.16Ω przy idealnym warunkowym AC odniesieniu pobliskiej3V0. Nie przypisano tego drugiego wariantu całemu torowi. Nowa jawna reguła pary ma minclearance/diffgap0.125mm; reszta pozostaje0.15mm. To zmiana geometrii i jej reguły projektowej, nie wyłączenie kontroli. [Delta18 UUID](../reports/usb_width_correction_A1.json). |
| Odrzucona B.GND | Na kopii dodany lokalny pour pokrywał tylko69/73% osi pary ze względu na inne B-sygnały. Idealnego93Ω nie wolno było przypisać takiej płaszczyźnie. Wariant odrzucono; nie dodano go do PCB. |
| RF / IMU | Keepout wszystkich warstw zachowany; zapisane wypełnienia nie mają przecięć z zakazaną strefą. Wszystkie centra ścieżek/via, footprinty, pady i nety zachowano względem38545441. Obudowa i bateria muszą pozostać poza anteną; docisk/naprężenia i RF na nodze są testem B. |
| PCBA / BOM / footprinty |59 pozycji TOP,33 grupy,69 footprintów. Native MPN/C/pad-net readback jest spójny. J2 jest montowane; J3 i9TP to miedź, nie ręcznie lutowane brakujące części. Raytac U3 i IMU U4 wymagają X-ray; IMU narzuca Standard PCBA. Dla3 grup brak odczytanej oferty JLC mimo potwierdzenia MPN/C w LCSC: U7 C2760466, R1 C25769, R20 C852679. Potwierdzić procurement przy imporcie. [Macierz33 grup i footprinty](pcba_testability_final_A1.md). |
| Flash / diagnostyka | Zachowano W25Q01JVZEIQ128MiB, pinout, napięcie i planF01–F20. SWD/reset/3V0/GND są dostępne naJ3,9TP obsługują istotne stany. Brak dedykowanych QSPI TP wymaga mikrosond/tymczasowych przewodów na płytce testowej; odcięcie całej szyny możliwe po usunięciu USB/SWD backpower. Żaden test nie wymaga dodatkowego adresowego pinu ani zmiany PCB. [Dostęp i ograniczenia](pcba_testability_final_A1.md), [20NOT_RUN](flash_firmware_test_plan_A1.md). |

## A — warunki przed zamówieniem

| ID | Konkretny warunek zamknięcia | Dlaczego przed zamówieniem |
|---|---|---|
| **A01** | Projektant odczytuje oryginalny rysunek Raytac VerL§8.3 i porównuje połączenia oraz C9=4.7µF/C10=100nF/C11=4.7µF z wybranym wariantem. Akceptuje też wymiarowane rysunki footprintów Raytac, J1 USB-C i Y1 ABS07 wskazane w przeglądzie PCBA. Oficjalny PDF znaleziono, ale narzędzia nie przekazały jego obrazów do odczytu; nie udajemy wykonanego porównania. | Jest to niedomknięta kontrola dokumentacji sprzętowej, niezależna od testu fizycznego. Nie wykryto tu potwierdzonego błędu. |
| **A02** | JLC potwierdza aktualny przekrój JLC7628 4L1.0mm, definicję grubości/Dk/Cu, nominalną geometrię0.17/0.13 i sposób przyjęcia tolerancji. Pełny tor zawiera pady, via, ESD oraz0.15mm rozdzielone końcówki; nie zamawiać go jako udowodnionego jednorodnego90Ω na podstawie samego modelu trunku. Zmiany CAM miedzi wymagają ponownego przeglądu. | Trzeba zamówić rzeczywistą konstrukcję odpowiadającą analizie. Pomiar oka po montażu pozostaje B. |
| **A03** | Import BOM/CPL w JLC Standard: potwierdzone dokładne MPN wszystkich33 grup, zwłaszcza3 nieodczytanych kart; rotacje/pin1/przesunięcia zaakceptowane w podglądzie, X-ray U3/U4 uwzględnione. | Karta katalogowa i liczba magazynowa nie są akceptacją konkretnego PCBA. Nie wprowadzono niezweryfikowanych zamienników. |
| **A04** | JLC zatwierdza CAM/DFM: maska/pasta LGA/WSON, minimalne0.150mm otwór→Cu/pasta, tenting, panel/szyny/fiducjale i sposób oddzielenia bez naruszenia anteny/naprężeń IMU. | Pliki istnieją i są spójne; panel wykonawcy i tolerancje procesu nie wynikają z0DRC. |

Po zamknięciu A01–A04 można zwolnić **3–5 prototypów do uruchomienia laboratoryjnego**. To nie zwalnia firmware, pracy w opasce ani ładowania niezakwalifikowanego pakietu. Akceptacja użytkownika i zamówienie pozostają oddzielnym krokiem.

## B — uruchomienie prototypów

Nie blokować wykonania PCB samym brakiem tych wyników. Wszystkie mają obecnie status niewykonanych:

- F01–F20: oba dies Flash,32-bit/all128MiB,16/32/64MiB i koniec pamięci, CRC, BUSY/WEL, erase, MCU reset/DPD i power-cut. Pozyskać AN0000035 i przypiąć SDK przed kwalifikacją drivera.
- Najpierw bench supply z ograniczeniem i symulator baterii/NTC. Zmierzyć3V0/VBUS/SYS, rampy/inrush, start bez baterii, PCM-open i utratę zasilania. Nie backpowerować przez USB/SWD/analizator.
- Przed prawdziwym ładowaniem: dobrać chroniony pakiet1S4.2V/NTC z odniesieniem PACK−; potwierdzić recovery PCM, progi/rampy, NTC open/short/factory mode, watchdog/hang/System OFF, timer i pełny cykl termiczny. NTC nie jest ADC MCU i nie zapewnia sprzętowego termicznego cutoff rozładowania.
- Cały prąd USB, suspend/resume i transfer; test sygnału/ESD w pełnym torze. Model2D nie jest symulacją oka, kwalifikacją JLC ani testem USB.
- IMU ODR/FS/FIFO, szum/bias/temperatura, utracone próbki, synchronizacja obu nóg, BLE oraz wpływ baterii/obudowy i naprężeń.

## C — kolejna rewizja

Optymalizacja około138µA okna temperatury bez pogorszenia bezpieczeństwa, mniejszy obrys, ergonomia, dedykowane QSPI testpoints/odłączany rail Flash, odczyt temperatury ogniwa przez MCU i ewentualny hardware heartbeat. Żadna z tych funkcji nie jest wymagana do obecnego planu prób na kontrolowanych prototypach.

## Kontrole końcowe i aktualny pakiet

KiCad10.0.7: **ERC0 błędów/2 uzasadnione ostrzeżenia IMU; DRC0 naruszeń/ostrzeżeń,0opens,0schematic-parity,0ignorowanych klas**. Jawna reguła USB jest częścią projektu i musi podróżować razem z PCB. Rozpakowany projekt z lokalnymi bibliotekami i plikiem reguł ponownie załadowano do natywnych ERC/DRC: identyczny wynik, [raport przenośności](../reports/package_native_validation_A1.json). Po zmianie szerokości ponowiono natywne odczyty, wypełnienia i eksporty.

11 Gerberów, Excellon PTH/NPTH,59 pozycji BOM/CPL,164vias,4sloty PTH i2NPTH porównano z aktualnym PCB. Wspólny origin: (50,101.6)mm, X w prawo/Y w górę. Brak nominalnych przecięć otworów z255padami Cu i243aperturami pasty; globalne minimum0.150001mm. Plik `.gbrjob` z automatycznym ogólnym stosem KiCad przeniesiono do `manufacturing/review/reference/` i **wyłączono z ZIP do uploadu**; zamówienie określa wybrany profil, a nie ten plik referencyjny.

Aktualna paczka: **Ankle_Sensor_V1_A1_FINAL_REVIEW.zip**. Nie używać dawnych A0/A1/AUDIT ZIP jako obecnego pakietu zamówienia. [Manifest aktualnych plików](../reports/current_A1_manifest.json), [natywne wyniki](../reports/validation_status.json), [eksporty](../manufacturing/review/export_manifest.json), [porównanie współrzędnych](../reports/manufacturing_geometry_review.json), [zmienione pliki](../reports/final_changed_files_A1.txt).

STEP/PDF/render są odświeżone. STEP nadal nie ma bryły USB-C, Raytac jest ogólny, Flash modelem gabarytowym, IMU ma ograniczenie wysokości; nie używać go do ostatecznego pasowania obudowy. To nie uniemożliwia wykonania samej PCBA.

Rzeczywisty commit końcowy i bundle są wskazane w `reports/final_commit_delivery_A1.json`, dostarczanym po zapisaniu commita, poza jego własną zawartością. **Push nie został wykonany.** [Instrukcja](github_delivery_final_A1.md) zawiera import bez nadpisywania plików oraz niezależną kontrolę GitHub po wysłaniu. Do czasu pozytywnego wyniku tej kontroli GitHub nie jest potwierdzonym źródłem tej wersji.

**Odpowiedź końcowa: CONDITIONAL READY.** Płytka może posłużyć do3–5 prototypów po zamknięciu A01–A04; brak fizycznych testów z grupy B nie jest powodem dalszego blokowania samego wykonania. Nie oznaczamy jej READY FOR PROTOTYPE przed spełnieniem tych jawnych warunków.
