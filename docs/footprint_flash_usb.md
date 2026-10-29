# Footprinty pamięci, ładowarki i USB-C — 2026-10-28

Zweryfikowano lokalne biblioteki **KiCad 10.0.7** w `/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints`. Trzy footprinty źródłowe skopiowano **bez skalowania i bez zmian geometrii** do `hardware/footprints/AnkleSensor.pretty`. Dodatkowo utworzono jawnie oznaczony wariant U1 z landami i pastą według przykładu TI. To przegląd bibliotek, nie zwolnienie PCB do produkcji. Nie zmieniano generatora ani manifestu.

| Ref. | Identyfikator w bibliotece projektu | Źródło lokalne | Wynik |
|---|---|---|---|
| U5 | `AnkleSensor:WSON-8-1EP_8x6mm_P1.27mm_EP3.4x4.3mm` | `Package_SON.pretty` | Wymiary obudowy, EP i numeracja odpowiadają W25Q01JVZEIQ; footprint źródłowy powstał dla innej pamięci, co jawnie odnotowano poniżej |
| U1 | **`AnkleSensor:BQ25185DLHR_DLH0010A_TILandPattern`** | Pochodna `Package_DFN_QFN.pretty:Texas_DLH0010A_WSON-10-1EP_2.2x2mm_P0.4mm_EP0.9x1.5mm` | Docelowy wariant z przykładem landów i pasty TI; oryginalną kopię zachowano pod nazwą KiCad |
| J1 | `AnkleSensor:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | `Connector_USB.pretty` | Dokładny MPN w nazwie; zgodne nazwy pinów. **Otwory i aktualna rewizja rysunku wymagają wizualnego porównania** |

Audyt maszynowy zapisano w `reports/footprint_flash_usb_audit.json`: SHA256 i identyczność kopii źródłowych, pełna geometria padów, porównanie numerów z `hardware/design.json`, kontrola zgodności netów padów współrzędnych oraz rzeczywista obecność plików STEP. Wszystkie trzy źródłowe footprinty załadowano natywnym `pcbnew.FootprintLoad` z KiCad 10.0.7: odpowiednio 13, 12 i 22 obiekty padów, wliczając otwory i pola pasty. Wariant projektowy TI również wczytano natywnie: 12 padów, numeracja 1–11 zgodna ze schematem. To kontrola odczytu biblioteki, nie DRC płytki.

## U5 — W25Q01JVZEIQ, 128 MiB

Źródło parametrów: [Winbond W25Q01JV Rev E, 2024-03-04, kopia dokumentu producenta w Mouser](https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf), sekcje 3.1/3.2 i rysunek obudowy ZE na stronie oznaczonej 81.

| Pad | Funkcja / obecny net | Położenie lokalne w mm |
|---|---|---|
| 1 | /CS / FLASH_CS_N | −3,75; −1,905 |
| 2 | IO1 / QSPI_IO1 | −3,75; −0,635 |
| 3 | IO2 / QSPI_IO2 | −3,75; +0,635 |
| 4 | GND | −3,75; +1,905 |
| 5 | IO0 / QSPI_IO0 | +3,75; +1,905 |
| 6 | CLK / QSPI_CLK_FLASH | +3,75; +0,635 |
| 7 | IO3 / QSPI_IO3 | +3,75; −0,635 |
| 8 | VCC / +3V0 | +3,75; −1,905 |
| 9 | EP / GND | 0; 0 |

Obrys F.Fab to 8×6 mm; raster 1,27 mm. Pady 1–8 mają 0,65×0,50 mm. EP ma 3,40×4,30 mm; cztery osobne otwory pasty mają po 1,37×1,73 mm. Dokument Winbond podaje wyprowadzenia nominalnie 0,50×0,40 mm i EP 3,40×4,30 mm. Numer „9” jest konwencją CAD dla EP; producent pozwala pozostawić EP niepołączony lub połączyć z GND. Manifest wybiera GND.

**Pochodzenie:** opis footprintu KiCad wskazuje rysunek GigaDevice GD5F1GQ4UFYIGR, nie Winbond. Porównano rzeczywiste współrzędne i wymiary z obudową Winbond; nie uznano podobnej nazwy za dowód. To zgodność geometrii obudowy, nie potwierdzenie zalecanego przez Winbond konkretnego rozmiaru landów i szablonu. Przed zamówieniem potwierdzić tolerancje ustawienia, pastę i rewizję dostarczanej obudowy. Zgodnie z uwagą Winbond nie umieszczać odkrytych przelotek pod EP.

## U1 — BQ25185DLHR, DLH0010A

Źródło: [TI BQ25185 SLUSF65B, sierpień 2026](https://www.ti.com/lit/ds/symlink/bq25185.pdf), tabela 4-1 oraz załączony rysunek **DLH0010A / 4226298/A 10/2020**, strony PDF 29–31.

Numeracja i obecny schemat: **1 SYS, 2 BAT, 3 STAT2, 4 /CE, 5 GND, 6 TS/MR, 7 ILIM/VSET, 8 ISET, 9 STAT1, 10 IN, 11 EP→GND**. Pad 1 jest u góry po lewej; pady 1–5 schodzą w dół, 6–10 wracają w górę po prawej. Raster 0,40 mm i obrys 2,20×2,00 mm są właściwe dla DLH, nie DSQ 2×2 mm.

| Parametr | KiCad — zachowana kopia źródłowa | Docelowy wariant projektowy = przykład TI |
|---|---|---|
| Pady sygnałowe | 0,75×0,20 mm, środki x=±1,10 mm | **0,50×0,20 mm, środki x=±1,05 mm**, rozstaw rzędów 2,10 mm |
| Pad EP | 0,90×1,50 mm | 0,90×1,50 mm |
| Otwór pasty EP | 0,84×1,41 mm, zaokrąglony | **0,85×1,38 mm**, promień narożnika 0,05 mm |

Oryginał KiCad ma dłuższe landy niż przykład TI. Projektowy `BQ25185DLHR_DLH0010A_TILandPattern` zmienia wyłącznie ich długość i położenie oraz otwór pasty EP, bez skalowania korpusu, rastra, EP ani modelu. Zachowano luźniejszy courtyard biblioteczny. EP musi być przylutowany i połączony z masą. Wariant nie ma przelotek w EP; wymagane odprowadzanie ciepła i połączenia między warstwami należy zaprojektować na PCB. Jeśli użyto przelotek pod pastą, TI zaleca ich wypełnienie, zaślepienie lub zakrycie. Szablon nadal wymaga akceptacji montażowej.

## J1 — Korean Hroparts TYPE-C-31-M-12 / C165948

Źródła: [oficjalna karta HRO](https://en.krhro.com/Product-Details/726.html), [rysunek producenta związany z LCSC C165948](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948), [JLC C165948](https://jlcpcb.com/partdetail/Korean_HropartsElec-TYPE_C_31_M12/C165948). Opis lokalnego footprintu wskazuje starszy adres rysunku HRO `http://www.krhro.com/uploads/soft/180320/1-1P320120243.pdf`.

Mapowanie elektryczne zgadza się z rysunkiem i manifestem: A1/A12/B1/B12→GND, A4/A9/B4/B9→VBUS, A5→CC1, B5→CC2, A6/B6→D+, A7/B7→D−, A8/B8→NC. Wszystkie cztery kotwy `SH` mają GND. W footprintcie pary **A1/B12, A4/B9, A9/B4, A12/B1 są współrzędne**; sprawdzono, że każda para ma ten sam net. Nie wolno przypisać współrzędnym padom różnych netów.

Poniższe dane odczytano z biblioteki KiCad; **nie są deklaracją pełnego porównania mechaniki z aktualnym rysunkiem dostawcy**:

| Element | Geometria lokalna [mm] |
|---|---|
| Linia padów SMT | y=−4,045; długość 1,45; szerokości 0,30 lub 0,60 |
| Środki sygnałów, od lewej | B8 −1,75; A5 −1,25; B7 −0,75; A6 −0,25; A7 +0,25; B6 +0,75; A8 +1,25; B5 +1,75 |
| Wspólne GND / VBUS | x=±3,25 / ±2,45 |
| Otwory ustalające NPTH | x=±2,89; y=−2,60; Ø0,65 |
| Dłuższe kotwy SH | x=±4,32; y=−3,13; drill 0,60×1,70; pad 1,00×2,10 |
| Krótsze kotwy SH | x=±4,32; y=+1,05; drill 0,60×1,20; pad 1,00×1,60 |
| Courtyard | x=±5,32; y=−5,27…+4,15 |

**Otwarte:** obrazowy PDF producenta jest dostępny, ale użyte narzędzie nie udostępniło obrazu do oglądu; nie potwierdzono zatem wymiarów otworów, przesunięcia względem PCB EDGE i pełnej zgodności z rewizją dostawcy. Szczególnie krótsze sloty 0,60×1,20 mm wymagają ponownego porównania. Nie skorygowano ich na podstawie przypuszczenia. Złącze wymaga czterech metalizowanych slotów kotwiących i dwóch NPTH; przy zamówieniu sprawdzić obsługę tego drill/rout przez producenta.

## Modele 3D i atrybucja

**Stan końcowego A1:** do U5 dodano jawnie oznaczony lokalny model maksymalnego gabarytu W25Q01JVZEIQ, a J1 nadal nie ma modelu. Szczegóły i ograniczenia są w `mechanical_model_review.md`. Poniższy opis braków w zainstalowanej bibliotece dotyczy źródłowego przeglądu; nie oznacza braku obecnego gabarytu U5. W lokalnym J1 skrócono dwie linie silkscreen do krawędzi modułu, bez zmiany padów ani otworów; kopia po tej zmianie nie jest bajtowo identyczna ze źródłem. Końcowy DRC potwierdza zgodność instancji z lokalną biblioteką.

Plik STEP dla **DLH0010A istnieje** w zainstalowanej bibliotece i skopiowano go do `hardware/3dmodels/Texas_DLH0010A_WSON-10-1EP_2.2x2mm_P0.4mm_EP0.9x1.5mm.step`. Wariant TI używa ścieżki `${KIPRJMOD}/3dmodels/...`, skali 1 i zerowych przesunięć/obrotów. Odwołania do modeli STEP dla **WSON8 8×6 mm** oraz **HRO TYPE-C-31-M-12** są w footprintach, ale pliki **nie istnieją** w lokalnej bibliotece 3D KiCad. Nie podstawiono modeli innej obudowy i nie deklaruje się kompletności modelu 3D zespołu. Te braki muszą zostać uzupełnione lub wyraźnie opisane przed eksportem STEP dla obudowy.

Kopie pochodzą z **KiCad Libraries Contributors**, [repozytorium kicad-footprints](https://gitlab.com/kicad/libraries/kicad-footprints), licencja [CC-BY-SA-4.0 z wyjątkiem KiCad](https://www.kicad.org/libraries/license/). Zachowano nazwy i oryginalną zawartość trzech źródeł, a zmiany pochodnej U1 opisano powyżej. Model pochodzi z bibliotek KiCad, nie jest określany jako model producenta. Nie należy traktować obecności w bibliotece jako dowodu fizycznej kwalifikacji montażu.
