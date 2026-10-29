> **Etap historyczny sprzed zmiany C9.** Aktualny stan określa [production_readiness_A1.md](production_readiness_A1.md). Oryginalne wyniki i hashe obliczeń zachowano; ich zastosowanie do nowego PCB opisują raporty produkcyjne i dowód identyczności geometrii.

# USB / wybrany przekrój JLCPCB — audyt A1

Odczyt 29.10.2026. Aktualny natywny PCB ma SHA-256 `cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`, po przyjęciu przez root lokalnego poszerzenia 18 odcinków USB. Ten audyt nie zmienia PCB. Dane źródłowe, rzeczywiste przekroje miedzi oraz wszystkie obliczenia zapisuje [usb_stackup_final_A1.json](../reports/usb_stackup_final_A1.json); powtarzalne narzędzia to [review_usb_stackup.py](../scripts/review_usb_stackup.py) i [usb_cross_section_fd.cpp](../scripts/usb_cross_section_fd.cpp). Dane 0,15/0,15 w porównaniu poniżej opisują poprzedni trunk, a nie aktualną szerokość przyjętych 18 odcinków.

## Wybór laminacji i granice potwierdzenia

Do analizy i potwierdzenia zamówienia wybrano **JLC7628, 4 warstwy, nominalnie 1,0 mm, miedź zewnętrzna 1 oz i wewnętrzna 0,5 oz**. Statyczna, oficjalna tabela JLC zawiera osobne przekroje 0,8/1,0/1,2/1,6/2,0 mm; użyto drugiego przekroju 7628, a nie domyślnej tabeli 1,6 mm z nowej strony. [JLCPCB: kompletna tabela laminacji](https://cart.jlcpcb.com/client/template/placeOrder/impedance.html).

| Warstwa od góry | Materiał / funkcja | Grubość [mm] | Er użyte w modelu |
|---|---|---:|---:|
| F.Cu | Cu / elementy i sygnały | 0,0350 | — |
| Dielektryk | prepreg 7628 × 1 | 0,2104 | 4,4 |
| In1.Cu | Cu / GND | 0,0152 | — |
| Dielektryk | core | 0,4000 | 4,6 |
| In2.Cu | Cu / USB, inne sygnały i +3V0 | 0,0152 | — |
| Dielektryk | prepreg 7628 × 1 | 0,2104 | 4,4 |
| B.Cu | Cu / sygnały | 0,0350 | — |

Suma bez maski wynosi 1,0212 mm; nazwa „1,0 mm” jest grubością nominalną. Nowa strona JLC podaje Er=4,4 dla 7628 oraz 4,6 dla core; starsza strona podaje dla 7628 Er=4,6. Różnicę zachowano w analizie czułości. Parametry maski z nowej strony: Er=3,8, nad podłożem i między ścieżkami 0,03048 mm, nad ścieżką 0,01524 mm. [JLCPCB: aktualne parametry impedancji](https://jlcpcb.com/impedance).

**Nie potwierdzono bieżącego identyfikatora wariantu w formularzu zamówienia ani przyjęcia tego przekroju przez fabrykę.** Aktualna strona wymaga JavaScript do pobrania przekroju 1,0 mm; dostępna wersja statyczna podaje geometrię starszej tabeli. Endpoint JLC `getImpedanceTemplateSettings` wymaga POST; dostępne narzędzia WWW nie zwróciły odpowiedzi dla 4L/1,0 mm, a pobranie lokalne blokuje brak DNS. Nie zastąpiono tych danych niezweryfikowanym profilem z repozytorium osoby trzeciej. Przed produkcją należy związać konkretny bieżący wariant JLC z instrukcją produkcyjną i potwierdzić Cu, dielektryki oraz Er. W bazowym pliku PCB są tylko cztery warstwy i grubość 1,0 mm, bez sekcji `stackup`. [JLCPCB: możliwości produkcji](https://jlcpcb.com/capabilities/pcb-capabilities/).

## Obliczenie impedancji

To własny, bezstratny model elektrostatyczny 2D quasi-TEM: rozwiązanie `div(ε grad V)=0` metodą objętości skończonych, wzbudzenie odd-mode +1/−1 V i osobne rozwiązanie tej samej geometrii w próżni. Z ładunku obliczono `Codd`, a następnie `Zdiff = 2/(c·sqrt(Codd·Codd0))`. Modelowanie modów różnicowych i wyprowadzanie parametrów linii z przekroju są opisane w dokumentacji producenta narzędzi symulacyjnych. [COMSOL: TEM i quasi-TEM](https://www.comsol.com/support/learning-center/article/modeling-tem-and-quasi-tem-transmission-lines-21971), [COMSOL: parametry RLGC](https://doc.comsol.com/6.4/doc/com.comsol.help.models.rf.transmission_line_coaxial/transmission_line_coaxial.html).

Solver używa prostokątnego Cu, idealnej In1.GND i jawnych warstw dielektryka/air/maski. Nie jest solverem pełnego toru USB. W obu siatkach wewnętrzne Cu zaokrągla się do 0,0150 mm zamiast 0,0152 mm. Nie uwzględniono trapezu trawienia, strat, zmian Er z częstotliwością, pełnej geometrii sąsiednich sygnałów B, vias, ESD, modułu, złącza ani kabla. Kryterium PCG wynosi względnie 10⁻⁹. Zgodność z analitycznym kondensatorem płaskim sprawdza jednostki, ładunek i przelicznik impedancji; nie kalibruje rzeczywistego przekroju względem komercyjnego solvera.

| Przekrój nominalny | W/gap [mm] | Zdiff przy siatce 2,5 µm |
|---|---:|---:|
| Dawny In2, tylko odległa In1.GND | 0,15 / 0,15 | **101,79 Ω** |
| Dawny In2, dodatkowo idealna miedź coplanar AC=0 po obu bokach, clearance 0,15 mm | 0,15 / 0,15 | **93,98 Ω** |
| Dawny In2, hipotetyczna ciągła B.GND w odległości 0,2104 mm | 0,15 / 0,15 | **93,01 Ω** |
| Aktualny trunk In2, tylko In1.GND | 0,17 / 0,13 | **94,14 Ω** |
| Aktualny trunk In2, warunkowe coplanar AC=0 | 0,17 / 0,13 | **87,16 Ω** |

Przy 5 µm pierwsze trzy wyniki wynoszą odpowiednio 102,15/94,36/93,35 Ω, a wariant 0,17/0,13 daje 94,48/87,51 Ω. Zmiana siatki daje około 0,35 Ω różnicy. Podwojenie rozmiarów pudełka dla pierwszego przekroju przy 5 µm zmienia wynik tylko o 0,042 Ω. Ta zbieżność numeryczna nie obejmuje błędu modelu ani tolerancji fabryki.

**Rzeczywisty +3V0 nie został automatycznie uznany za masę.** Natywne wypełnienie potwierdza miedź po obu bokach pary w przekrojach y=68/71/80/84 mm, około 0,15 mm od jej zewnętrznych krawędzi. Na y=73,5 mm prawa krawędź +3V0 odsuwa się do x≈72,573 mm; występują też antypady i sygnały B. Scenariusze GND-only i idealnego coplanar pokazują czułość na otoczenie. Nie stanowią ścisłego przedziału gwarantowanej impedancji całego toru. Wspólny tryb i rzeczywista impedancja zasilania wymagają osobnej oceny.

## Końcówki i zakres najmniejszej poprawki

W aktualnym PCB 18 odcinków zachowanego wspólnego trunku In2 ma 0,17 mm szerokości i nominalny odstęp 0,13 mm, do y=86,8 mm. Pozostałe USB mają 0,15 mm. Końcówki U6 i J1 są prowadzone osobno na F/In2 i nie mają stałego sprzężenia. Hipotetyczna równoległa para F o 0,15/0,15 daje 105,49 Ω przy 2,5 µm, ale nie odpowiada całym rzeczywistym końcówkom. Izolowane ścieżki F/In2 dają w modelu Z0 około 72,1/84,4 Ω przy 5 µm. To lokalne scenariusze przekroju, a nie wyliczona impedancja całego toru. Nie należy przypisywać końcówkom Zdiff przez podwojenie wyniku pary albo sumowanie lokalnych impedancji.

Fizyczne sumy odcinków bazowego MCU→U6 to DP=31,232 mm i DN=32,957 mm, po dwa via. U6→J1 to DP=12,997 mm i DN=15,552 mm, również po dwa via. Suma obejmuje rozgałęzienia do zdublowanych pinów USB-C, a nie pojedynczą ścieżkę propagacji. Nie obejmuje długości wewnątrz modułu/ESD/złącza ani pionowych odcinków via.

**Przyjęta minimalna poprawka:** root zwiększył wyłącznie szerokość 18 odcinków zachowanego wspólnego trunku In2 z 0,15 do 0,17 mm, zachowując środki ścieżek. Odstęp krawędzi wynosi nominalnie 0,13 mm. Oba modele nominalne mieszczą się w roboczym celu 90 Ω ±10% (81–99 Ω). Plik `hardware/Ankle_Sensor_V1.kicad_dru` zawiera jawną regułę 0,125 mm wyłącznie dla DP/DN; inne sieci zachowują 0,15 mm. Root wykonał refill i natywne DRC/parity 0/0/0. Nowy odczyt potwierdza po dziewięć odcinków 0,17 mm na DP i DN, z niezmienionymi długościami i liczbą vias. [Dziennik korekty](../reports/usb_width_correction_A1.json) potwierdza zachowanie UUID, środków, warstw, sieci, elementów i vias. Szerokość zmienia otoczkę Cu o 0,01 mm na każdą stronę; nie dodano nowej trasy ani vias. Nie wolno uznać okna nominalnego za gwarancję tolerancji produkcji.

**Wariant B.GND odrzucony.** Idealny pas masy szerokości 1,5 mm pod środkiem pary daje 93,36 Ω przy 5 µm, lecz sprawdzona przez root kopia z prostokątem B.GND `(68,5;64)..(74,6;89)` pokrywa rzeczywistą oś tylko w około 69,3% DP i 73,5% DN. Przecinają ją inne sygnały B. Idealnego wyniku 93 Ω nie można przypisać tej pociętej płaszczyźnie; brak wykazanej korzyści uzasadniającej jej przyjęcie. Canonical nie otrzymał tej masy.

## Raytac §8.3 i zasilanie USB

Oficjalny PDF Ver.L z 24.05.2023 potwierdza tekstowo, że §8.3 jest wariantem dla napięcia wejściowego poniżej 3,6 V. Natywny odczyt U3: pad28 VDD i pad30 VDDH są na +3V0, pad31 DCCH jest niepołączony, pad32 VBUS jest na VBUS, pad34→USB_DN, pad35→USB_DP. Zwarcie VDD/VDDH jest normalnym trybem nRF52840, z REG0 automatycznie wyłączonym. Pływające DCCH przy nieużywanym REG0 jest potwierdzone przez Nordic; REG1 jest osobnym stopniem. [Raytac Ver.L, §8](https://www.raytac.com/download/index.php?index_id=43), [Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html), [Nordic: DCCH](https://devzone.nordicsemi.com/f/nordic-q-a/108362/vdd-vddh-and-dcch-mistake).

**Rysunek §8.3 nadal nie został wizualnie odczytany.** Ponowione screenshoty stron PDF39–40 przez oba narzędzia zwróciły wyłącznie tekst `ImageDisplayed`, bez bitmapy. Nie pobrano lokalnego PDF przez shell. Odnaleziony schemat oficjalnego dongla MDBT50Q-RX nie jest dokładnym rysunkiem §8.3 i go nie zastępuje. Literalne wartości zewnętrznych kondensatorów i ich zgodność z tym rysunkiem pozostają kontrolą dokumentacyjną przed produkcją. C11 na VBUS nie jest kondensatorem wewnętrznego wyjścia DECUSB; moduł nie wyprowadza tego sygnału. Nie wymyślono brakujących wartości.

Nie ma podstaw do automatycznego dodania 22 Ω w D+/D−: producent potwierdza rezystory w samym USB PHY nRF52840. [Nordic: zewnętrzne rezystory USB](https://devzone.nordicsemi.com/f/nordic-q-a/94955/resistors-for-d-and-d-).

## A — zamknięcie sprzętu i fabrykacji; B — kwalifikacja prototypu

**A:** potwierdzić bieżący wariant JLC i powiązać z instrukcją produkcyjną; dokończyć wizualne porównanie Raytac §8.3. Lokalna poprawka szerokości została przyjęta i sprawdzona natywnie, a nowe wypełnienie odczytano w tym raporcie. Sam model dawnego trunku około 102 Ω nie dowodził, że urządzenie nie będzie działało; pokazywał mały nominalny margines. Aktualne nominalne 94,14/87,16 Ω poprawia ten margines, ale nie kwalifikuje całego toru. Nie ma podstaw do pełnego reroutingu ani do fikcyjnej deklaracji „90 Ω sprawdzone”.

**B:** nRF52840 ma USB **full speed 12 Mb/s**, z UI≈83,33 ns. Testy należy prowadzić dla FS, z właściwym kablem i przyrządem; maska HS480 Mb/s nie jest właściwym kryterium. USB-IF rozróżnia także czasy zboczy FS/HS. Potrzebny jest firmware USB, długi transfer z kontrolą integralności i ponownym łączeniem, obie orientacje USB-C, pomiary przebiegów oraz testy ESD. W chwili audytu firmware urządzenia nie istnieje. DRC i model 2D nie potwierdzają działania fizycznego. [Nordic: USB12 Mb/s](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/keyfeatures_html5.html), [USB-IF: FS/HS i zbocza](https://www.usb.org/node/214), [USB-IF: aktualizacje pomiarów elektrycznych](https://compliance.usb.org/index.asp?UpdateFile=Electrical).
