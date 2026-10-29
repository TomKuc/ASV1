# Przegląd rozmieszczenia zasilania i propozycja korekty

Data: 2026-10-28. Weryfikacja geometrii przez rzeczywisty KiCad 10.0.7, bibliotekę `pcbnew` i `kicad-cli pcb drc`. Nie zmieniono głównego PCB ani `hardware/placement.json`. Propozycja do nałożenia przez prowadzącego: `hardware/power_placement_proposal.json` (mapa `ref: [x_mm, y_mm, angle_deg]`).

## Stan wejściowy i ograniczenie kontroli

Pierwszy odczyt natywnego PCB przed routingiem zawierał 69 footprintów, 0 ścieżek i 2 strefy. Raport `drc_placement_current.json` zawierał 177 niepołączonych elementów, 0 błędów zgodności ze schematem i jedno ostrzeżenie o różnicy footprintu J1. Wcześniejszy `drc_placement_initial.json` miał 488 naruszeń, 177 niepołączonych elementów i 69 rozbieżności schematu. Raporty dotyczą różnych etapów; zniknięcie błędów geometrii nie oznacza poprawnego routingu.

Płytka zmieniała się równolegle podczas przeglądu. Do testowania propozycji skopiowano nowszy PCB do `.work/power_proposal/Ankle_Sensor_V1.kicad_pcb`, usunięto z kopii wszystkie dotychczasowe ścieżki, przelotki i strefy, a następnie naniesiono wyłącznie nowe rozmieszczenie i dwie proponowane zewnętrzne przelotki termiczne z połączeniami do EP. Jest to test rozmieszczenia, a nie raport zakończonego PCB.

## Obowiązkowa korekta przed ponownym routingiem

TI wymaga lokalnych kondensatorów IN/SYS/BAT oraz ciągłego GND połączonego z pinem GND i EP. [BQ25185, rozdział 7.4](https://www.ti.com/lit/ds/symlink/bq25185.pdf). LDO wymaga krótkich połączeń kondensatorów wejściowego i wyjściowego z odpowiednim pinem i masą. [TPS7A20, rozdział 7.4](https://www.ti.com/lit/ds/symlink/tps7a20.pdf).

Odległości poniżej to odległości między środkami właściwych padów sygnałowych, sprawdzone na podstawie rzeczywistego numeru pinu i nazwy sieci w KiCad. Nie są długościami przyszłych ścieżek ani gwarancją małej indukcyjności pętli.

| Kondensator | Pin układu / sieć | Pierwotnie [mm] | Propozycja [mm] | Nowe x, y, kąt |
|---|---|---:|---:|---|
| C1 | U1.10 / VBUS | 1.856 | 1.494 | 66.25, 90.95, 0° |
| C2 | U1.1 / VSYS | 4.322 | 1.274 | 61.60, 89.40, 90° |
| C3 | U1.2 / VBAT | 4.475 | 1.456 | 59.75, 92.10, 180° |
| C4 | U2.1 / VSYS | 3.455 | 1.475 | 69.15, 79.80, 90° |
| C5 | U2.5 / +3V0 | 2.689 | 1.475 | 71.45, 79.80, 90° |
| C18 | U7.8 / +3V0 | 3.442 | 1.405 | 58.00, 81.90, 180° |
| C19 | U8.3 / +3V0 | 2.994 | 1.483 | 66.90, 84.50, 0° |

W tych MLCC pad 1 jest szyną, pad 2 masą; są niepolaryzowane. Kąty są konwencją `SetOrientationDegrees()` KiCad, nie konwencją pliku Pick and Place JLC. Dla 90° pad 1 kondensatora znajduje się poniżej środka w układzie współrzędnych PCB; sprawdzono rzeczywiste pozycje po transformacji.

Dodatkowe przesunięcia dają miejsce powyższym kondensatorom bez zmiany schematu:

| Ref | Nowe x, y, kąt | Powód |
|---|---|---|
| Q1 | 58.55, 88.30, 0° | Miejsce na pionowy C2 nad U1 |
| R1 | 65.90, 93.20, 0° | Rezystor ILIM po stronie pinu 7 U1 |
| R2 | 65.90, 92.20, 0° | Rezystor ISET po stronie pinu 8 U1 |
| R3 | 63.50, 89.70, 0° | Zwolnienie miejsca C1; blisko obwodu CE |
| R22 | 61.50, 87.00, 0° | Zwolnienie miejsca Q1 i C2 |
| U2 | 70.30, 83.00, 0° | +0.20 mm w dół, miejsce C4/C5 między NOR a LDO |
| R24 | 73.40, 85.00, 0° | +0.20 mm w prawo, odsunięcie od nowej pozycji LDO |

U1 pozostaje w (63.0, 92.2). Przy routingu należy prowadzić pin układu bezpośrednio do właściwego pada kondensatora, dać lokalną przelotkę GND przy jego padzie 2 i połączyć pin/EP układu z ciągłą masą. Samo połączenie kondensatora odległym odcinkiem z przypadkową odnogą szyny nie realizuje celu tej korekty. Nie wymuszać przejścia GND przez długą ścieżkę do sąsiedniego kondensatora. Rezystory odniesienia NTC i TS prowadzić z dala od pętli prądowych i szybkich sygnałów.

## EP U1 i technologia montażu

EP U1 ma 0.90 × 1.50 mm i należy do GND. Ostateczna zaakceptowana propozycja stosuje dwie **zewnętrzne** przelotki GND 0.50 mm / otwór 0.25 mm, w pozycjach **(63.0, 91.0)** i **(63.0, 93.4)**, z maską po obu stronach. Nie znajdują się wewnątrz EP. Sprawdzono natywnym DRC dwie proste ścieżki F.Cu GND szerokości 0.30 mm od środka EP do tych przelotek. Przy EP kończącym się na y=91.45/92.95 mm odstęp miedzi przelotki od krawędzi EP wynosi 0.20 mm. Otwór przelotki pozostaje poza polem lutowniczym.

Przelotki muszą łączyć EP z pełną płaszczyzną GND; oprócz ścieżek lokalne pole F.Cu GND o clearance 0.15 mm ma rozpraszać ciepło. To sensowna geometria dla standardowego procesu z przelotkami poza padami; skuteczność cieplna wymaga pomiaru. Brak przelotki i brak lokalnego ciągłego GND nie może być zaakceptowany tylko dlatego, że router osiągnął elektryczną ciągłość.

Wcześniej sprawdzona opcja dwóch via-in-pad w EP została odrzucona na rzecz geometrii zewnętrznej, aby nie wprowadzać niedopiętego procesu wypełniania. JLC wskazuje ryzyko odpływu lutowia i opisuje epoxy/copper filled-and-capped; via-in-pad oraz otwory blisko otwarcia maski nie kwalifikują się do zwykłego wypełniania farbą. Nie oznacza to zakazu użycia standardowych przelotek zakrytych maską poza padem. [JLC: via covering](https://jlcpcb.com/help/article/pcb-via-covering), [JLC: via-in-pad](https://jlcpcb.com/help/article/via-in-pad-pofv-guide).

Przed wypuszczeniem plików obowiązkowo sprawdzić zachowanie osobnych apertur pasty EP, miedzi i maski oraz faktyczne zakrycie zewnętrznych przelotek maską bez ingerencji w otwarcie EP. Sam pad EP nie ma warstwy F.Paste, co jest poprawne, jeżeli footprint zachowuje odrębne pola pasty. Powyższa liczba przelotek jest sensownym punktem startowym tego wariantu; nie zastępuje kwalifikacji termicznej w rzeczywistej obudowie.

## Wynik natywnego DRC propozycji

Klona sprawdzono z kopią aktualnego pliku `.kicad_pro` i tabelą wskazującą prawdziwe lokalne footprinty. Raport: `reports/drc_power_placement_proposal.json`.

- **0 błędów geometrii:** brak overlapów courtyards, zwarć, naruszeń odstępów miedzi, maski i sitodruku w sprawdzanym stanie.
- **2 ostrzeżenia `via_dangling`:** wyłącznie proponowane zewnętrzne przelotki termiczne, ponieważ kopia celowo nie zawiera płaszczyzn i reszty routingu.
- **177 niepołączonych elementów:** oczekiwany stan usuniętego routingu; wynik nie jest dopuszczeniem do produkcji.

Po nałożeniu JSON przez generator konieczny jest ponowny DRC, ponieważ generator może inaczej umieścić teksty lub odbudować footprinty. Po routingu konieczne są kontrola połączeń, rzeczywista inspekcja pętli zasilania, wypełnienie stref i kompletny DRC końcowego pliku.

## Kwestie do zamknięcia później

1. **Stos warstw i USB:** aktualnie PCB ma założenie 4L/1.0 mm. [Oficjalny stos JLC](https://jlcpcb.com/impedance) udostępnia wybór 1.0 mm, lecz odczyt tekstowy eksponuje domyślną konstrukcję 1.6 mm. Nie przenosić z niej grubości dielektryków do 1.0 mm. Przed deklaracją 90 Ω USB trzeba wybrać konkretny stos w kalkulatorze/ofercie i dopasować rzeczywistą geometrię pary. Nie potwierdzono tutaj impedancji USB.
2. **Pojemność efektywna MLCC:** C1/C3 są już 2.2 µF/25 V, ale pozostaje potwierdzenie minimalnego Ceff po bias, temperaturze i starzeniu; patrz `docs/ui_battery_selection.md`. Rozmieszczenie nie zamyka tej kwestii.
3. **Termika i zasilanie:** pełen cykl ładowania rzeczywistego chronionego pakietu 300 mAh z NTC na ogniwie, rozruch/odłączenie USB, obciążenia impulsowe RF/Flash, temperatura U1/LDO i baterii w obudowie, reakcja nadzoru napięcia przy szybkim zaniku szyny.
4. **Budżet uśpienia:** obecny blok odniesienia NTC/pullup pobiera około 138 µA w battery-only, plus inne układy. To jawny koszt obecnej topologii, nie wynik pomiaru. Nie wymaga rozpoczęcia nowej architektury w tym etapie.

## Dodatkowa korekta pod fanout U1

Po wdrożeniu 14 przesunięć sprawdzono na kolejnym klonie wariant zwalniający miejsce przy prawych pinach U1. Oryginalna propozycja C1=(65.3,90.0,90°) powoduje overlap courtyard z U1. Wybrany wariant bez tego konfliktu zapisano jako `hardware/power_fanout_placement_proposal.json`:

| Ref | x, y, kąt |
|---|---|
| C1 | 65.50, 90.00, 90° |
| Q2 | 52.50, 80.40, 0° |
| C13 | 56.10, 79.20, 0° |
| C14 | 58.60, 80.20, 0° |
| R2 | 66.00, 92.20, 0° |

Ostatecznie sprawdzono przelotkę `CHG_STAT1_N` o rozmiarze 0.50/0.25 mm w **(64.8,91.65)** oraz trzy konkretne trasy F.Cu o szerokości 0.15 mm:

- STAT1: U1.9 → (64.65,91.8) → (64.8,91.65), ostatni odcinek po przekątnej 45°.
- ISET: prosta pozioma U1.8 → R2.1.
- IN: U1.10 → (64.05,90.775) → C1.1.

Przesunięcie STAT1 w górę zachowuje miejsce dla poziomej trasy ISET i jej zapasu routera. R2 przesunięto o +0.10 mm w prawo; przy wcześniejszej przelotce w (64.8,91.8) bez tego przesunięcia pojawiały się naruszenia do jego pada 1: odstęp miedzi 0.1182 mm przy wymaganym 0.15 mm i odstęp otworu 0.2432 mm przy wymaganym 0.25 mm.

Rzeczywista pozycja pada 1 C1 przy 90° to (65.50,90.775), odległość od U1.IN=(64.05,91.4) wynosi **1.579 mm**. To nadal krótka lokalna trasa. Native footprint ma offset pada 0.775 mm; pozycję sprawdzono w KiCad.

Wynik `reports/drc_power_fanout_proposal.json`: **0 błędów geometrii**, jedno oczekiwane `via_dangling` dla STAT1 bez dalszej trasy na B.Cu oraz 175 niepołączonych elementów po celowym usunięciu reszty routingu z kopii. Zmiany Q2/C13/C14 mieszczą się w istniejącym rozmieszczeniu bez konfliktów. Q2 jest elementem sterowania statycznego o pomijalnym wydzielaniu ciepła w tym zastosowaniu; ta korekta nie wprowadza istotnego źródła ciepła przy IMU. Nadal należy prowadzić jego gate i pulldown w sposób odporny na zakłócenia oraz sprawdzić kompletne nowe trasowanie. Głównego PCB nie modyfikowano.

## Niezależny przegląd rzeczywistego routingu A1

Powyższe sekcje opisują wcześniejsze propozycje i klony. Poniższe ustalenia odświeżono **29.10.2026 na rzeczywistym końcowym PCB** o SHA256 **`38545441d19c70f355dd06a2539d2aa0937b113d92569c9b4798a1a04e08c45b`**, po naprawach C3/Flash, R24 pull-up, relokacji U6 i poprawkach geometrii. Wcześniejszy odczyt `b5487d09…` jest historyczny. Ponownie odczytano 17 par IC–kondensator i wszystkie 17 padów GND/EP U1–U8. Szczegóły i współrzędne rzeczywistych ścieżek: `reports/power_routing_review.json`. Natywne DRC po refill/save ma 0 naruszeń, 0 niepołączonych elementów i 0 rozbieżności schemat–PCB. To przegląd geometrii, nie kwalifikacja elektryczna/termiczna prototypu.

Sprawdzono sąsiedztwo elementów i ścieżek przez natywną łączność KiCad, połączenia vias z In1/In2 oraz zapisane wielokąty wypełnień. Wspólny polygon zasilania nie został uznany automatycznie za krótki obwód: dla gałęzi bez bezpośredniego F.Cu wyszukano lokalną drogę w rzeczywiście zapisanej miedzi z krokiem 0.05 mm. Wagi grafu natywnej łączności nie są długością ścieżki — kontakt może zachodzić wewnątrz pada lub na krawędziach szerszych odcinków. Raport rozdziela te wagi od jawnych polilinii i dokładnych odległości środków.

| Obwód | Rzeczywista lokalna droga zasilania | Powrót kondensatora do In1 |
|---|---|---|
| U1 IN / C1 | Bezpośrednie F.Cu, polilinia 2.075 mm | Via GND 0.825 mm od środka pada |
| U1 SYS / C2 | Bezpośrednie F.Cu, polilinia 1.999 mm | 0.850 mm |
| U1 BAT / C3 | Bezpośrednie F.Cu, polilinia 1.949 mm po przesunięciu C3 | 0.775 mm po naprawie via |
| U2 IN/OUT / C4/C5 | Bezpośrednie F.Cu, po 1.475 mm | Po 0.725 mm |
| U3 VDD/VDDH / C10 | Krótkie osobne stuby do In2; lokalna droga między vias 1.490–1.997 mm | 0.650 mm |
| U3 bulk C9 | Lokalne połączenie po In2 1.595–2.395 mm między vias | 0.850 mm |
| U3 VBUS / C11 | Ciągłe lokalne F.Cu w obszarze około 3×3 mm; bez objazdu przez resztę płytki | 0.850 mm |
| U4 VDD / C12, VDDIO / C13 | Lokalne In2 między vias odpowiednio 1.191 i 1.341 mm; C14 bulk 2.586 mm | C12/C13 po 0.620 mm; C14 0.850 mm |
| U5 VCC / C15 | **Naprawiony lokalny obwód F.Cu–via–B.Cu–via–F.Cu**; odcinki XY łącznie 2.469 mm | 0.620 mm |
| U5 bulk C16 | Od lokalnego węzła C15 do via C16 po In2 3.578 mm; cała gałąź od U5 około 6.28 mm XY | 0.850 mm |
| U7 / C18 | Krótkie stuby i lokalne In2 między vias 1.390 mm | 0.620 mm |
| U8 / C19 | Krótkie stuby i lokalne In2 między vias 1.450 mm | 0.622 mm |
| U6 po relokacji | Gałąź VBUS krótsza; C11 nadal przy module U3, bez nowego lokalnego bypass U6 | 0.9375 mm F.Cu do via (71.4,93.3), przed zmianą 1.0125 mm |

Odległości GND w tabeli są odległościami środków pada i lokalnej via, a nie deklaracją całkowitej indukcyjności pętli. Długości XY nie obejmują pionowych przejść przez przelotki. Każda sprawdzona via GND kontaktuje In1; ponownie sprawdzono osiem próbek pierścienia między krawędzią otworu i krawędzią miedzi (dla 0.5/0.25 mm promień 0.1875 mm). Nie znaleziono odległej odnogi GND zastępującej lokalny powrót kondensatora.

### Wykryta i usunięta długa odnoga Flash

Na wcześniejszym końcowym PCB U5 i C15/C16 należały do tej samej wyspy +3V0, lecz ścieżki sygnałowe na mieszanej In2 wymuszały objazd **28.02 mm do C15 i 31.14 mm do C16**, sięgający y≈59.55 mm. DRC nie sygnalizuje takiej jakości odsprzęgania. Pierwotny wniosek o lokalnej gałęzi U5 został wycofany i zastąpiony ustaleniem PWR-02 w raporcie.

Bezpośrednią drogę F.Cu blokuje istniejący QSPI_CLK_FLASH. Przyjęta minimalna naprawa to **jeden odcinek +3V0 szerokości 0.30 mm na B.Cu**, między istniejącymi vias (71.75,72.5) i (72.9,73.0), długości 1.254 mm. Razem z krótkimi stubami zamyka lokalny obwód C15. C16 ma krótką drogę od tego samego węzła po zapisanej In2; nie wymagał następnego mostka. Nie zmieniono zegara QSPI, innych sieci, footprintów ani przelotek. Natywne DRC/opens/parity po zmianie są zerowe.

### EP ładowarki: istniejący stan termiczny

EP U1 0.90×1.50 mm ma dwa rzeczywiste połączenia F.Cu szerokości 0.30 mm do zewnętrznych vias GND (63,91.0) i (63,93.4), po 1.20 mm od środka EP. Pin 5 jest również dołączony do tego powrotu; obie vias kontaktują wypełnioną In1. **Nie ma lokalnej wylewki GND na F.Cu**: istnieje elektrycznie działająca płaszczyzna In1 i przelotki, a nie zadeklarowany wcześniej dodatkowy górny rozpraszacz ciepła.

Nie stwierdzono braku masy EP. Wąskie mostki termiczne i brak górnej powierzchni rozpraszającej pozostają jednak jawnym ograniczeniem do sprawdzenia przy pełnym cyklu ładowania, impulsach obciążenia i rzeczywistej obudowie. Nie wolno stosować bezpośrednio katalogowego RθJA dla płytki JEDEC ani deklarować bezpiecznej temperatury pakietu na podstawie samego DRC.

### Globalny audyt otworów względem SMD i pasty

Po przesunięciu C3 jego stara via GND (58.15,92.1) weszła otworem w pole SMD/pastę. Naprawiono tylko tę via, przesuwając ją do **(57.8,92.1)** i przedłużając jeden istniejący odcinek F.Cu GND. Otwór ma teraz **0.200 mm nominalnego zapasu** do miedzi i pasty C3. Jest to późniejsza rzeczywista korekta, niezależna od wcześniejszych propozycji placementu.

Trwały audytor `scripts/audit_vias.py` w finalnym raporcie sprawdza **164 przelotki, 255 kształtów miedzi SMD i 243 apertury pasty**, obie strony i również pary tej samej sieci, w tym osobne apertury EP. Używa natywnego `Collide`, rzeczywistego promienia otworu i marginesów pasty; kontrola dodatnia wykrywa dawną kolizję C3. **Brak przecięć otworów z miedzią SMD i brak przecięć z pastą** po poprawce. Raport: `reports/via_pad_audit.json`, source hash `38545441…`.

Historyczne minimum **0.090 mm przy U5.7 / QSPI_IO3**, via (71.85,73.9), zostało naprawione: obecna via (71.85,73.76) ma **0.230001 mm** do miedzi i pasty U5.7. Bieżące minimum całego PCB to **0.150001 mm**, przy U6.2 oraz C4.2/C5.2. Otwory leżą poza miedzią i pastą. Nadal wymagana jest akceptacja JLC DFM z tolerancjami wykonania i rejestracji maski/szablonu; wynik CAD nie gwarantuje zachowania nominalnego marginesu na egzemplarzu. Skrypt nie zmienia PCB.

