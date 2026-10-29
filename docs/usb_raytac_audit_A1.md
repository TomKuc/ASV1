# Audyt A1: Raytac, USB, IMU, RF i mechanika

Data: **29.10.2026**. Aktualne PCB: SHA-256 `38545441d19c70f355dd06a2539d2aa0937b113d92569c9b4798a1a04e08c45b`; schemat główny: `2da343b592b4ed98f85ab6a3ca2d0258b9378b2b7e69cf85c11982da26a46f8d`. Audyt nie zmienił PCB, schematu, wartości ani tras. Świeży natywny eksport netlisty porównano z rzeczywistymi padami U3/U4/U6/J1: **zero rozbieżności sieci**. Dane pomiarowe i źródła: [usb_raytac_audit_A1.json](../reports/usb_raytac_audit_A1.json). Aktualny przydział wszystkich 61 padów modułu: [pin_assignment_A1.md](pin_assignment_A1.md).

## Zasilanie modułu i Raytac §8.3

| Pad U3 | Aktualny schemat i PCB | Ocena |
|---|---|---|
| 28 VDD | +3V0 | Zasilanie główne 3,0 V |
| 30 VDDH | Ta sama +3V0 | Poprawny normal voltage mode |
| 31 DCCH | NC, bez przyłączonej ścieżki | Zgodne z nieużywanym REG0 |
| 32 VBUS | VBUS z USB-C | Osobne wejście zasilania USB, nominalnie 5 V |
| 1, 2, 15, 33, 55 | GND | Wszystkie masy modułu przyłączone |

[Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html) definiuje normal voltage mode przez wspólne VDD i VDDH oraz automatyczne wyłączenie REG0. Zakres VDD wynosi 1,7–3,6 V. [Wsparcie Nordic](https://devzone.nordicsemi.com/f/nordic-q-a/108362/vdd-vddh-and-dcch-mistake) potwierdza pozostawienie DCCH w stanie niepodłączonym przy nieużywanej przetwornicy REG0. REG1 jest osobnym stopniem; [Raytac Ver. L, §3 i §8](https://www.raytac.com/download/index.php?index_id=43) podaje, że jego dławik i kwarc 32 MHz są już w module. Nie ma uzasadnienia do łączenia DCCH z GND ani do dodawania dławika REG0 do obecnego układu 3,0 V.

Aktualne zewnętrzne odsprzęganie przy module to C9=4,7 µF/10 V X5R i C10=100 nF/16 V X7R na +3V0 oraz C11=4,7 µF/10 V X5R na VBUS. C5=10 µF jest kondensatorem wyjścia LDO. Nominalne wartości nie potwierdzają pojemności efektywnej MLCC pod napięciem. Parametr Nordic C_DECUSB odnosi się do węzła DECUSB wewnątrz SoC; moduł nie wyprowadza go na pady hosta. Nie jest to kryterium wartości C11 na wejściu VBUS.

**Granica weryfikacji:** oficjalny [Raytac Ver. L, §8.3, drukowane strony 40–41](https://www.raytac.com/download/index.php?index_id=43) został odnaleziony ponownie. Narzędzie udostępniło tekst, ale nie przekazało do odczytu obrazów schematów referencyjnych. Nie deklaruję wizualnego sprawdzenia ich przewodów ani kompletu wartości kondensatorów. Zgodność podstawowej topologii zasilania potwierdzają powyższe źródła Nordic; pełne porównanie rysunku Raytac i pojemności pozostaje jawnie otwarte. Nie wprowadzono zastępczych wartości na podstawie domysłu.

## USB: poprawna topologia, otwarta kwalifikacja prowadzenia

Aktualne połączenia odpowiadają pinoutowi [ST USBLC6-2, DS4260 Rev. 7](https://www.st.com/resource/en/datasheet/usblc6-2.pdf):

| Linia | Połączenie |
|---|---|
| D+ | J1.A6 i B6 → U6.1 ↔ U6.6 → U3.35 |
| D− | J1.A7 i B7 → U6.3 ↔ U6.4 → U3.34 |
| Odniesienia ESD | U6.2 → GND; U6.5 → VBUS |
| USB-C sink | Oddzielne R14 i R15 po 5,1 kΩ z CC1/CC2 do GND |

Kanały nie są zamienione. USBLC6-2SC6 jest ochroną odpowiednią dla USB full speed; maksymalna katalogowa pojemność I/O–GND wynosi 3,5 pF. VBUS modułu wymaga 4,35–5,5 V oraz równoczesnego prawidłowego zasilania głównego. Użycie właściwej sekwencji inicjalizacji USBD pozostaje zadaniem firmware.

**Brak zewnętrznych rezystorów szeregowych D+/D− nie jest wykrytym błędem.** [Oficjalna, zweryfikowana odpowiedź Nordic dla nRF52840](https://devzone.nordicsemi.com/f/nordic-q-a/94955/resistors-for-d-and-d-) potwierdza ich integrację w USB PHY i brak wymogu dodawania zewnętrznych. Nie zalecono automatycznego dodania 22 Ω, 27 Ω ani innej wartości. Rezystory pokazywane w ogólnych aplikacjach USB innych układów nie ustanawiają takiego wymogu dla nRF52840.

**USB02 — poprawiono, kwalifikacja ESD pozostaje otwarta:** U6 przesunięto do (71,6; 93,3) mm, a R25 do (74,8; 92,2) mm. U6 jest teraz oddalony od J1 o **9,500 mm** między środkami. Aktualne sumy odcinków danych J1–U6 wynoszą **12,996638 mm** dla D+ i **15,552121 mm** dla D−, wobec wcześniejszych 18,717/20,563 mm przed korektą. [ST §2.3](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) zaleca ochronę blisko złącza i krótkie połączenia I/O, VBUS oraz GND, bez sztywnego limitu milimetrów. Korekta skraca odcinki przed ochroną, lecz nie stanowi testu odporności całego urządzenia.

Najbliższy kondensator VBUS, C1, jest teraz około **7,67 mm** od U6.5 w linii prostej między padami; C11 około **25,79 mm**. Najbliższy via GND jest około **0,94 mm** od U6.2. Są to pomiary geometrii, nie indukcyjności. Finalny [audit via/pad](../reports/via_pad_audit.json), dla tego samego hasha PCB, wykazuje minimum otwór–Cu/pasta **0,150001 mm** także z uwzględnieniem tego samego netu.

Zachowano wspólną część trunku MCU na In2 do y=86,8 mm, z nominalną szerokością/odstępem 0,15/0,15 mm. Nowe końcówki i odcinki złączowe są prowadzone osobno; nie są zakwalifikowaną jednolitą parą. Aktualne sumy MCU–U6 wynoszą DP=31,231505 mm, DN=32,957221 mm, po dwa via. Sumy całego toru MCU–U6–J1 to DP=44,228143 mm i DN=48,509342 mm, po cztery via na linię. Obejmują odgałęzienia do dwóch pinów USB-C; pomijają beczki via i wnętrze elementów. Różnica sum miedzi nie jest pomiarem różnicy opóźnienia propagacji. Szczegóły i jawne dane historyczne: [usb_layout_review.md](usb_layout_review.md), [usb_routing_review.json](../reports/usb_routing_review.json).

## IMU: aktualny pinmap i dwa ostrzeżenia ERC

Potwierdzono **U4.4 INT1 → U3.27 P0.11** oraz **U4.9 INT2/DEN → U3.29 P0.12**. P0.24 i P0.25 są obecnie NC. Poprzednia tabela przedstawiała propozycję sprzed routingu; dokumentację poprawiono bez zmiany PCB.

[ST DS13511 Rev. 2, tabela 2 i §7.1](https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf) dopuszcza GND na pinach 2/3 w mode 1 przy wyłączonych analog hub i Qvar. Aktualne połączenie jest zatem właściwe dla tego zastosowania. Włączenie trybów wykorzystujących te piny w innej roli wymagałoby ponownej analizy hardware. Piny 6/7 są przyłączone do GND i mają pola lutownicze. Pin 10=+3V0/VDD_IO oraz pin 11=NC są dozwolone w mode 1; także NC11 powinien być przylutowany do swojego pola. VDD8 i VDD_IO5 mają wspólne 3,0 V; C12 i C13 są po 100 nF, a C14 ma 1 µF.

Zapisany `erc_current.json` zawiera dwa ostrzeżenia bidirectional-to-power dla U4.2 i U4.3 na GND. Wynikają z ogólnego typu symbolu obejmującego alternatywne tryby sensora i z flagi zasilania masy. Są uzasadnione opisanym trybem pracy; nie zostały zamaskowane ani usunięte przez zmianę typu pinów. Ponowne natywne ERC całego projektu prowadzi główny audyt.

## RF i mechanika IMU

Natywnie sprawdzono istniejący keepout anteny x=57,8…70,2 mm, y=49,8…55,0 mm na wszystkich czterech warstwach miedzi. Nie wykryto przecięcia przez rzeczywiste ścieżki, via, pady ani zapisane wypełnienia In1/In2. Strefa dochodzi poza krawędź PCB y=50 mm. Spełnia to sprawdzalne zasady tekstowe [Raytac §2.3](https://www.raytac.com/download/index.php?index_id=43): brak miedzi przy antenie w każdej warstwie i moduł przy krawędzi. Ten test porównuje miedź z zadeklarowaną strefą projektu; nie jest niezależnym wizualnym zatwierdzeniem wymiarowanego rysunku producenta ani testem anteny na nodze.

Według [ST TN1383, §3 i §4.5](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf) ważne są symetryczne wyjścia z padów, brak TOP routing/via pod sensorem, odsunięcie od ciepła i źródeł siły. Aktualny U4 ma jednakową szerokość 0,15 mm na wszystkich 13 podłączonych wyjściach padów; pin 11 jest NC. Centralna strefa TOP x=54,95…56,65 mm, y=75,9…77,1 mm nie zawiera ścieżek ani via. Nie wykryto kolizji nominalnych courtyard elementów po tej samej stronie. Odstępy obrysów FAB do SW1 i J1 wynoszą odpowiednio 16,20 i 17,63 mm, wobec zalecanego odsunięcia od źródeł siły co najmniej 10 mm. Nie jest to analiza naprężeń całej obudowy.

Model baterii, obudowa, śruby, docisk opaski, przewody i wtyczka nie są częścią zespołu CAD. Odległość do J2 opisuje złącze baterii, nie położenie ogniwa. Mocowanie musi ograniczać ugięcie PCB i bezpośredni nacisk na U4; kalibrację sprawdzić po reflow oraz po zamknięciu obudowy. [TN0018 Rev. 8](https://www.st.com/resource/en/technical_note/tn0018-handling-mounting-and-soldering-guidelines-for-mems-devices-stmicroelectronics.pdf) pozostaje podstawą procesu montażu MEMS. Nie wykonano analizy modalnej ani prób naprężeń.

STEP U3 jest modelem generycznym KiCad, bez zatwierdzenia dokładnej anteny i tolerancji P1MV2. Dokładnego modelu J1 nadal brak. Model U5 jest jawną obwiednią gabarytową. Ograniczenia te są opisane w [mechanical_model_review.md](mechanical_model_review.md); nie uzasadniają zatwierdzenia ciasnej obudowy na podstawie samego renderu.

## 4 warstwy / 1,0 mm: oferta JLCPCB i brak wyboru stackupu

[JLCPCB oferuje kontrolowaną impedancję dla czterech warstw i wybór grubości 1,0 mm](https://jlcpcb.com/impedance). [Aktualne capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/) podają dla grubości ≥1,0 mm tolerancję ±10%, czyli nominalnie 0,9…1,1 mm dla tej płytki, oraz tolerancję zamówionej impedancji ±10%. Ta tolerancja nie obejmuje automatycznie projektu bez wybranego stosu i specyfikacji impedancji.

Aktualny plik PCB zawiera **cztery warstwy i grubość całkowitą 1,0 mm**, ale nie zawiera jawnej sekcji stackup, grubości dielektryków, Er, wybranego identyfikatora laminacji ani potwierdzonego zamówienia controlled impedance. Statycznie otwarta strona JLC pokazuje domyślne tabele 1,6 mm; nie przepisano z nich wartości do projektu 1,0 mm. Nie zadeklarowano konkretnego stosu JLC04101H ani wyliczonej impedancji bez odczytanej konfiguracji 1,0 mm.

Sama wykonalność ścieżek 0,15 mm i via 0,50/0,25 mm nie potwierdza impedancji pary. In1 jest GND, In2 zawiera +3V0 i sygnały, a B.Cu sąsiaduje z mieszaną In2. **USB 90 Ω, referencje szybkich sygnałów, ESD oraz działanie RF w docelowym montażu pozostają do kwalifikacji.** Firmware jeszcze nie powstało. Ten audyt dokumentuje poprawne połączenia i jawne warunki otwarte; nie zwalnia projektu do produkcji.

Strona JLC dotycząca impedancji podaje minimum 3,5 mil (około 0,089 mm) dla szerokości/odstępu i 0,2 mm dla via. Obecne 0,15 mm i otwory 0,25 mm nie przekraczają tych ogólnych minimów. Dostępne są różne masy miedzi zewnętrznej i wewnętrznej; dokładne reguły DFM trzeba odnosić do wybranej opcji. Nie jest to zatwierdzenie całej geometrii produkcyjnej ani domyślny wybór grubości miedzi.
