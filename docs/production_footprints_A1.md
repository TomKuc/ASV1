# A01 — footprinty produkcyjne U3, J1 i Y1

**Status: EXTERNAL CONFIRMATION.** Dla trzech elementów wykonano pełny odczyt padów z rzeczywistego PCB i porównanie z lokalnymi bibliotekami. Ten podpunkt odczytu jest **CLOSED**. Nie uzyskano wystarczającego odczytu rysunków producentów do zatwierdzenia wszystkich współrzędnych, numeracji, otworów i bazy krawędzi PCB. Nie zmieniono padów ani PCB. Nie stwierdzono na tej podstawie, że obecne footprinty są nielutowalne.

Odczyt: 29.10.2026, KiCad 10.0.7. Bazowy commit `b17f1457de876ecb27e94dc514c9a4844be44bc0`; rzeczywisty PCB po zmianie wartości C9 ma SHA-256 **`1d3bb700a2b686ef68589bf3295488d2144a1d51a857cec7651e45be175a6134`**. Zmiana C9 nie jest przedmiotem tego przeglądu. Pełne współrzędne wszystkich padów, ich numerów, netów, warstw, wymiarów Cu/pasty, otworów i orientacji są w [production_footprints_A1.json](../reports/production_footprints_A1.json). Hash przed i po odczycie jest identyczny.

| Element i dokładny wariant | Wynik natywnego odczytu | Porównanie instancji z lokalną biblioteką | Co pozostaje do A01 |
|---|---|---|---|
| U3 Raytac MDBT50Q-P1MV2 | 61 padów SMD | Identyczna geometria wszystkich padów | Dokładny rysunek Ver.L lub CAD producenta: współrzędna i numer każdego pada, orientacja TOP/pin1 |
| J1 HRO TYPE-C-31-M-12 / C165948 | 16 obiektów padów SMD, 4 metalizowane kotwy, 2 NPTH | Identyczna geometria wszystkich 22 obiektów | Aktualna rewizja rysunku dostarczanego złącza: sloty, kołki, zalecane PCB EDGE i ustawienie kontaktów |
| Y1 ABS07-32.768KHZ-7-T / C276424 | 2 pady SMD po 1,00 × 1,80 mm, rozstaw środków 2,50 mm | Identyczna geometria obu padów | Jednoznaczne przypisanie wymiarów zalecanego landu dokładnej rodziny ABS07; obecne pady pozostają bez zmian |

## Granica dowodu z dokumentacji

Oficjalny PDF i indeks wyszukiwarki nie są równoważne obejrzeniu rysunku. Oba dostępne narzędzia screenshotów — `web__run` i surowy MCP — ponownie zwróciły tekstowe referencje lub `ImageDisplayed`, bez bitmapy i bez bloku typu `image`. Lokalny `curl` nie pobiera plików z powodu błędu DNS. Nie uzyskano archiwum CAD producenta, które dałoby się lokalnie otworzyć i zmierzyć.

Niektóre wyniki wyszukiwania zawierają automatyczne opisy `visual_element`. Te opisy pomagają odnaleźć figurę, lecz **nie są literalnym tekstem PDF ani niezależnym odczytem jej cyfr i linii wymiarowych**. Nie użyto ich do zamknięcia A01 ani do zmiany Y1. Wcześniejsze określenie takiego opisu jako „literalnego” skorygowano podczas audytu.

## U3 — Raytac MDBT50Q-P1MV2

Podstawa producenta: [Raytac Ver.L, 24.05.2023, §2.1–2.2](https://www.raytac.com/download/index.php?index_id=43), [kopia tego dokumentu producenta w Mouser](https://www.mouser.com/datasheet/3/1361/1/nRF52840_MDBT50Q_1MV2_MDBT50Q_P1MV2_Ver.L_spec.pdf). Dokument obejmuje dokładnie wariant PCB-antenna P1MV2. [Oficjalny support Raytac](https://www.raytac.com/document/index.php?index_m_id=12) wymienia pakiet **MDBT50Q & MDBT50Q-P & MDBT50Q-U Footprint_Design Guide (230606)**. Strona dostępna narzędziom nie ujawniła bezpośredniego adresu ZIP; pakietu nie pobrano i nie uznano za sprawdzony vendor CAD.

Rzeczywista instancja to `AnkleSensor:Raytac_MDBT50Q`, pozycja `(64,00;59,00)` mm, obrót 0°. Początek lokalny jest w środku korpusu. Obrys F.Fab ma 10,50 × 15,50 mm: x=±5,25, y=±7,75 mm. Wszystkie 61 padów ma zapisane wymiary 0,60 × 0,40 mm; dolne i wewnętrzne rzędy są obrócone o 90°, więc ich rzut w osiach footprintu ma 0,40 × 0,60 mm. Pady są prostokątne, na F.Cu/F.Mask/F.Paste, bez lokalnego pomniejszenia pasty.

Wybrane punkty kontrolne, w lokalnych osiach projektu; pełna tabela jest w JSON:

| Pad | x [mm] | y [mm] | Obrót pada |
|---|---:|---:|---:|
| 1 | −4,65 | −3,75 | 0° |
| 3 | −4,65 | −1,85 | 0° |
| 15 | −4,80 | +7,15 | 90° |
| 17 / 18 | −3,20 / −2,40 | +7,15 | 90° |
| 24 | 0,00 | +7,15 | 90° |
| 28 / 30 | +1,60 / +2,40 | +7,15 | 90° |
| 31 / 32 / 33 | +3,20 / +4,00 / +4,80 | +7,15 | 90° |
| 34 / 35 | +4,65 | +6,15 / +5,35 | 0° |
| 51 / 53 | +4,65 | −1,85 / −2,65 | 0° |
| 56 / 61 | −2,00 / +2,00 | +0,55 | 90° |

Do porównania z ewentualną bazą w lewym dolnym narożniku korpusu przygotowano transformację `x′=x+5,25`, `y′=7,75−y`. To tylko przeliczenie współrzędnych; nie jest zatwierdzeniem, że właśnie taka baza i takie powiązanie numerów obowiązuje na niewidzianym rysunku producenta.

Biblioteka KiCad i zgodność jej kopii z instancją są dowodem pochodzenia projektu, a nie zastępstwem porównania wszystkich 61 landów z dostarczanym modułem. Nie podstawiono starszego rysunku rodziny bez V2 ani wariantu U1MV2 jako dowodu exact P1MV2.

Wcześniej zmierzony keepout anteny obejmuje wszystkie warstwy Cu, x=57,8…70,2, y=49,8…55,0 mm. [Zapisany raport geometrii](../reports/rf_filled_copper_review.json) wykazuje zerowe przecięcia miedzi; jego hash źródłowy jest jawnie zachowany w nowym JSON. Ten wąski audyt nie powtarza pełnego przeglądu RF i nie używa keepoutu jako dowodu poprawności numeracji padów. Generyczny STEP U3 nie stanowi zatwierdzonego CAD anteny P1MV2, ale sam brak dokładnego STEP nie jest blokadą produkcji PCB.

## J1 — HRO TYPE-C-31-M-12 / C165948

Źródła: [oficjalna karta HRO](https://en.krhro.com/Product-Details/726.html), [rysunek producenta powiązany z C165948](https://datasheet.lcsc.com/lcsc/1903211732_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf), [bieżący odnośnik rysunku z LCSC](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948). Strona HRO podaje nominalny gabaryt 8,94 × 7,35 × 3,16 mm. Tabela funkcji pinów w kopii dokumentu producenta jest czytelna tekstowo; pełne linie wymiarowe nie były dostępne do niezależnego obejrzenia.

Instancja `AnkleSensor:USB_C_Receptacle_HRO_TYPE-C-31-M-12` jest w `(64,00;99,00)` mm, obrót 0°. Dane niżej są **pomiarami natywnego PCB**, nie zatwierdzonym przepisaniem rysunku HRO:

| Element | Lokalna geometria [mm] |
|---|---|
| Rząd SMT | y=−4,045; długość padów 1,45; szerokość sygnałów 0,30, wspólnych GND/VBUS 0,60 |
| Kolejność sygnałów od lewej | B8 x−1,75; A5 −1,25; B7 −0,75; A6 −0,25; A7 +0,25; B6 +0,75; A8 +1,25; B5 +1,75 |
| Wspólne GND/VBUS | A1/B12 x−3,25; A4/B9 x−2,45; A9/B4 x+2,45; A12/B1 x+3,25 |
| NPTH | 2 × Ø0,65, x=±2,89; y=−2,60 |
| Dłuższe metalizowane kotwy SH | x=±4,32; y=−3,13; otwór 0,60 × 1,70; Cu 1,00 × 2,10 |
| Krótsze metalizowane kotwy SH | x=±4,32; y=+1,05; otwór 0,60 × 1,20; Cu 1,00 × 1,60 |
| F.Fab | x=±4,47; y=±3,65, czyli 8,94 × 7,30 |
| Courtyard | x=±5,32; y=−5,27…+4,15 |

Cztery pary współrzędnych padów mają wspólne nety, odpowiednio GND/VBUS/VBUS/GND; nie ma konfliktu elektrycznego w nakładających się polach. Wszystkie kotwy SH mają GND i warstwy Cu/Mask, bez F.Paste. Proces lutowania kotew musi zatem zostać zaakceptowany przez montaż, a nie wywnioskowany z obecności padów sygnałowych SMT.

Aktualna krawędź PCB y=101,60 mm znajduje się lokalnie **y=+2,60 mm względem początku J1**. Projektowy F.Fab sięga do y=102,65 mm, czyli wystaje o 1,05 mm. Nie potwierdzono, czy ta baza odpowiada zalecanemu `PCB EDGE` aktualnego rysunku HRO. Różnica 0,05 mm między długością grafiki F.Fab 7,30 a nominalnym opisem produktu 7,35 nie dowodzi błędu padów; pokazuje, dlaczego samego prostokąta bibliotecznego nie należy traktować jako zatwierdzonego gabarytu z tolerancjami.

**Do potwierdzenia:** oba rozmiary slotów, Ø i rozstaw NPTH, rząd padów, rewizja części dostarczanej jako C165948 oraz położenie krawędzi PCB. Brak modelu STEP J1 nie jest osobnym blockerem A01; ma znaczenie dla obudowy i dostępu wtyczki.

## Y1 — dokładny ABS07, bez sufiksu LR

Źródło: [Abracon ABS07, rewizja 08-10-22, Mechanical Dimensions na stronie PDF4](https://abracon.com/Resonators/ABS07.pdf). Osobny [rysunek obudowy ABS07](https://abracon.com/Support/PackageDrawing/Resonators/ABS07.PDF) obecnie przekierowuje przy bezpośrednim otwarciu na konto Abracon, choć jego indeks zawiera liczby i tytuł zalecanego landu. Dokładny MPN ma sufiks `7` oznaczający CL=7 pF oraz standardową wysokość 0,9 mm maksimum. Przegląd pojemności obciążenia jest osobnym zadaniem.

Aktualny footprint pochodzi od bibliotecznego Epson FC-135; podobny korpus 3215 nie dowodzi identyczności zalecanego landu Abracon. Pozycja Y1 to `(61,00;68,50)` mm, obrót **180°**:

| Pad | Środek lokalny [mm] | Środek na PCB [mm] | Cu i pasta | Net |
|---|---|---|---|---|
| 1 | (+1,25;0) | (59,75;68,50) | 1,00 × 1,80 | LF_XL1 |
| 2 | (−1,25;0) | (62,25;68,50) | 1,00 × 1,80 | LF_XL2 |

Rozstaw środków wynosi 2,50 mm, wewnętrzny odstęp Cu 1,50 mm, zewnętrzny rozstaw krawędzi 3,50 mm. Margines pasty wynosi zero. Obrys F.Fab ma 3,20 × 1,50 mm; courtyard 4,00 × 2,30 mm.

**Możliwa różnica zalecenia — niepotwierdzona do zmiany.** Indeks dokładnego rysunku ABS07 zawiera liczby `2X 0.043 / 1.1`, `0.075 / 1.9` i `0.055 / 1.4` obok `Recommended Land Pattern`. Automatyczny opis figury sugeruje pady 1,10 × 1,90 mm i gap 1,40 mm; z tego wynikałby ten sam rozstaw środków 2,50 mm. Bez niezależnego odczytu przypisania osi i linii wymiarowych nie zatwierdzono jednak tej interpretacji. **Y1 pozostaje 1,00 × 1,80 mm; nie wykonano korekty na podstawie opisu indeksu.** Nie ma tu stwierdzenia, że obecna geometria jest nielutowalna.

Odnaleziony ABS07-LR jest odrębną rodziną Low ESR. Jej rysunek został wyłączony z dowodów zgodności dokładnego ABS07-32.768KHZ-7-T. Nie wolno zamknąć tej pozycji przez użycie podobnego wariantu ani przez sam zgodny obrys korpusu.

## Konkretne pytania do JLCPCB / dostawcy — szkic, niewysłany

1. **U3:** potwierdzić na podstawie Ver.L §2.1/2.2 lub CAD 230606 wszystkie 61 numerów, centrów, wymiarów i obrotów padów z tabeli JSON, w widoku TOP. Potwierdzić bazę początku footprintu, pin1 i stronę anteny dokładnego P1MV2. Wskazać każdą różnicę, zamiast ogólnego „ten sam moduł 10,5 × 15,5”.
2. **J1:** zatwierdzić dla faktycznie dostarczanej rewizji C165948 tabelę SMT/slotów/NPTH powyżej, bazę `PCB EDGE` względem lokalnego y=+2,60 mm oraz proces lutowania czterech kotew bez F.Paste. Zwrócić numer lub datę sprawdzonego rysunku.
3. **Y1:** potwierdzić zalecane szerokość, wysokość, gap i rozstaw środków dla **ABS07 bez LR**. Jawnie zaakceptować obecne 1,00 × 1,80 mm / rozstaw2,50 mm albo dostarczyć czytelny rysunek i wskazać wymagane zmiany. Dołączyć warunek pasty/szablonu, jeśli akceptacja zależy od procesu.

Po uzyskaniu takiego potwierdzenia można zamknąć odpowiadającą mu pozycję A01 albo wykonać niewielką, jednoznacznie uzasadnioną korektę i ponowić odpowiedni DRC. Wynik 0 DRC sam w sobie nie porównuje footprintu z rzeczywistą częścią dostawcy.
