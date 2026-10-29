# A02 — USB i stackup produkcyjny A1

**EXTERNAL CONFIRMATION.** Publiczna tabela JLCPCB zawiera wariant czterowarstwowy JLC7628 o nominalnej grubości 1,0 mm. Nie uzyskano potwierdzenia aktualnego identyfikatora tego wariantu w konkretnym zamówieniu ani akceptacji fabryki. Istniejący routing zachowano. Odczyt geometrii wykonano ponownie w KiCad 10.0.7 dla PCB SHA-256 `1d3bb700a2b686ef68589bf3295488d2144a1d51a857cec7651e45be175a6134`.

## Konkretny przekrój do potwierdzenia

Wybór do wyceny: **JLC7628, 4L, 1,0 mm nominalnie, zewnętrzne Cu 1 oz, wewnętrzne Cu 0,5 oz**. Druga tabela 7628 w oficjalnym zestawieniu odpowiada grubości 1,0 mm; nie użyto geometrii domyślnego przekroju 1,6 mm. [Oficjalna tabela JLCPCB](https://cart.jlcpcb.com/client/template/placeOrder/impedance.html).

| Kolejność od góry | Funkcja / materiał | Grubość użyta w modelu [mm] |
|---|---|---:|
| F.Cu | elementy, sygnały | 0,0350 |
| Dielektryk | prepreg 7628 × 1 | 0,2104 |
| In1.Cu | GND | 0,0152 |
| Dielektryk | core | 0,4000 |
| In2.Cu | sygnały USB i inne, +3V0 | 0,0152 |
| Dielektryk | prepreg 7628 × 1 | 0,2104 |
| B.Cu | sygnały | 0,0350 |

Suma tych pozycji wynosi **1,0212 mm bez maski**, więc nie jest obietnicą dokładnie 1,000 mm po produkcji. Starsza tabela zawiera też opis core „0,45 mm with copper”; jego konwencja nie daje się jednoznacznie utożsamić z powyższą sumą i wymaga wyjaśnienia przez CAM. Starsze Er dla prepregu to 4,6, natomiast aktualna strona podaje 4,4; dla core obie podają 4,6. Model używa Er=4,4/4,6 oraz aktualnego nominalnego profilu maski: 0,03048 mm nad podłożem, 0,01524 mm nad ścieżką, Er=3,8. [Parametry aktualnego kalkulatora JLCPCB](https://jlcpcb.com/impedance).

Bieżąca strona pokazuje statycznie przekrój 1,6 mm i wymaga JavaScript do zmiany wariantu. Dostępna tabela historyczna oraz opcja „1,0 mm” nie potwierdzają przyjęcia tego stosu do konkretnej partii. Dlatego dokument zawiera parametry do potwierdzenia, a nie fikcyjny numer zaakceptowanego szablonu.

## Aktualna geometria i ponowne wykorzystanie obliczeń

Nowy odczyt potwierdza **9 odcinków DP i 9 DN na In2.Cu po 0,17 mm**, z nominalnym odstępem krawędzi 0,13 mm. Końcówki mają 0,15 mm i zmienne sprzężenie. C9 otrzymał inną wartość i MPN, ale [porównanie całej geometrii](../reports/production_geometry_equivalence_A1.json) potwierdza zachowanie wszystkich 1822 obiektów ścieżek/przelotek, 69 footprintów, padów oraz wypełnień. Nie zmienił się żaden przekrój USB.

Dlatego zachowano istniejące obliczenia FVM wykonane na poprzednim PCB `cdcbd23449ce12977567ecdd061c598cc0dc2830e28d7cea8fada4b1bcea9e40`. **Nie uruchamiano ponownie solvera.** Nowy raport oddziela `computed_on_board_sha256` od aktualnego odczytu. [Wynik i dane odczytu](../reports/production_usb_A1.json), [powtarzalny skrypt odczytu](../scripts/review_production_usb_A1.py), [oryginalne obliczenia](../reports/usb_stackup_final_A1.json).

| Model przekroju aktualnego trunku 0,17/0,13 mm | Zdiff, siatka 2,5 µm |
|---|---:|
| Idealna In1.GND, bez idealizacji bocznego +3V0 jako masy | 94,139 Ω |
| Dodatkowo idealne boczne przewodniki AC=0, odsunięte o 0,15 mm | 87,162 Ω |

To nominalne, bezstratne przybliżenia elektrostatyczne 2D, z `Zdiff=2/(c·√(Codd·Codd0))`. Nie są pomiarem, gwarancją tolerancji JLCPCB ani ścisłymi granicami impedancji całej trasy. Rzeczywiste +3V0 nie staje się automatycznie idealną masą. Model nie obejmuje pełnych przejść via, złącza, ESD, wnętrza modułu, kabla, trawienia ani częstotliwościowej zmienności materiału. Wyniki są wystarczającą podstawą, by **nie wykonywać kolejnego reroutingu bez nowych dowodów**, lecz nie zastępują potwierdzenia stosu i kwalifikacji prototypu.

## Odniesienie GND i przelotki

Ponownie odczytano rzeczywiste zapisane wypełnienie In1.GND wraz z antypadami, a nie sam obrys strefy. Wszystkie 59 padów GND należy do jednej natywnej sieci połączeń. Nie oznacza to ciągłego, niezakłóconego odniesienia pod każdą ścieżką. [Pełna kontrola geometrii powrotu](../reports/return_path_review.json).

| Sieć | Suma odcinków [mm] | Via | Oś rzutowana nad In1.GND | Największa suma połączonych odcinków bez tego rzutu [mm] |
|---|---:|---:|---:|---:|
| USB_DP | 31,232 | 2 | 95,25% | 0,825 |
| USB_DN | 32,957 | 2 | 95,44% | 0,856 |
| USB_DP_CONN | 12,997 | 2 | 84,00% | 1,433 |
| USB_DN_CONN | 15,552 | 2 | 89,79% | 0,852 |

Brakujące rzuty występują m.in. przy antypadach i końcówkach. Ta metryka geometryczna nie jest obliczeniem prądu powrotnego; rozgałęzienia mogą zwiększać sumę jednej składowej. Próbkowanie osi ma krok maksymalnie 0,01 mm. B.Cu sąsiaduje z mieszaną In2, a nie bezpośrednio z płaszczyzną GND. Nie zatwierdzono przez to całej trasy jako jednolitej linii 90 Ω.

Tor ma po cztery via DP/DN od J1 przez U6 do MCU; sumy obejmują zdublowane styki i rozgałęzienia USB-C, bez długości pionowej via oraz wnętrza podzespołów. U6 jest oddalony od J1 o 9,5 mm między początkami footprintów. Odcinki złącze–U6 mają powyżej 12,997/15,552 mm. Nie przypisano im nieistniejącego limitu długości producenta: ST zaleca krótkie połączenia I/O, VBUS i GND oraz ochronę przy złączu. Zachowano istniejącą poprawę położenia U6, a odporność systemową ESD pozostawiono do pomiaru. [ST USBLC6-2, §2.3](https://www.st.com/resource/en/datasheet/usblc6-2.pdf).

## Raytac i rezystory USB

Natywny odczyt potwierdza U3.28 VDD i U3.30 VDDH na +3V0, U3.31 DCCH niepodłączony, U3.32 VBUS na USB, U3.34→DN i U3.35→DP. W niniejszym kroku nie zmieniono tych połączeń ani zabezpieczenia. Kwestie kondensatorów oraz dokładnego footprintu modułu są oddzielnie opisane w [A01 kondensatory](production_caps_A1.md) i [A01 footprinty](production_footprints_A1.md).

Dodatkowe szeregowe rezystory 27 Ω nie są wymagane wyłącznie ze względu na ich brak na schemacie: Nordic potwierdza rezystory w USB PHY nRF52840. Nie dodano ich. [Odpowiedź techniczna Nordic](https://devzone.nordicsemi.com/f/nordic-q-a/94955/resistors-for-d-and-d-).

## Pytania do JLCPCB — przygotowane, niewysłane

1. Podać aktualny identyfikator i rysunek dostępnego stosu **4L / 1,0 mm / JLC7628 / outer1oz / inner0.5oz**, wraz ze sprasowanymi odległościami między Cu i końcową tolerancją grubości.
2. Potwierdzić Cu i dielektryki z tabeli oraz wyjaśnić konwencję core 0,400 mm względem opisu 0,45 mm „with copper”; podać Er prepregu/core, profil maski i właściwy materiał dla tej partii.
3. Ocenić aktualną parę **In2, W=0,17 mm, gap=0,13 mm**, odległą od In1.GND o core, z mieszaną miedzią +3V0 na In2 i sygnałami na B. Potwierdzić akceptację procesu, a jeśli ma być zamawiana kontrola impedancji — wskazać zakres gwarancji i kupon.
4. Zgłosić każdą proponowaną zmianę stosu, szerokości, odstępu albo obróbki CAM przed jej zastosowaniem. Nie traktować generycznego `.gbrjob` jako zatwierdzonej instrukcji laminacji.

**Do uruchomienia prototypu, nie do fikcyjnego wykonania przed PCB:** transfer USB FS12Mb/s z CRC i ponownym łączeniem, obie orientacje USB-C, pomiar zboczy/eye właściwy dla FS oraz ESD. Żadnego z tych testów nie wykonano. Obecna decyzja pozostawia routing do pierwszej partii prototypowej, z warunkiem potwierdzenia rzeczywistego stosu i zamknięcia pozostałych pozycji A01–A04 przed zwolnieniem produkcji.
