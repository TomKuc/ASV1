# Dobór UI, złącza baterii i przegląd MLCC — 28.10.2026

Rekomendacja A0: przycisk **SKQGABE010**, dioda **19-217/G7C-AN1P2/6T**, złącze **SM03B-SRSS-TB(LF)(SN)**. Wszystkie mają rzeczywiste oznaczenia; status zakupowy złącza wymaga potwierdzenia w JLC. Ten dokument nie zatwierdza PCB do zamówienia ani nie zmienia generatora.

## Elementy i footprinty

| Ref. | Wybrany MPN / źródło JLC | Footprint KiCad 10, potwierdzony lokalnie | Decyzja |
|---|---|---|---|
| SW1 | ALPS Alpine **SKQGABE010**, **C115351**, [JLC](https://jlcpcb.com/partdetail/ALPSALPINE-SKQGABE010/C115351) | `Button_Switch_SMD:SW_SPST_SKQG_WithStem` | Wybrany wariant ze standardową biblioteką i modelem STEP |
| D1 | Everlight **19-217/G7C-AN1P2/6T**, **C2986030**, [JLC](https://jlcpcb.com/partdetail/EverlightElec-19_217_G7C_AN1P26T/C2986030) | `LED_SMD:LED_0603_1608Metric` | Żółtozielona AlGaInP, zgodna z szyną 3 V |
| J2 | JST **SM03B-SRSS-TB(LF)(SN)**, **C160403**, [LCSC](https://lcsc.com/product-detail/Others_JST-Sales-America__JST-Sales-America-SM03B-SRSS-TB-LF-SN-P_C160403.html) | `Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal` | Wybrany 3-pin SH, status `PROCUREMENT_REVIEW` |

Publiczne rekordy JLC potwierdzają dla SW1 i D1 montaż SMT Economic/Standard. Strona SW1 pokazała zapas 55 560 sztuk; to odczyt katalogu z jego pamięcią podręczną, nie rezerwacja. Dla D1 nie uzyskano wiarygodnej aktualnej liczby magazynowej. Numer C160403 i dokładny MPN J2 są potwierdzone w LCSC; bezpośredniej strony JLC nie udało się odczytać. Nie należy zamieniać tego ograniczenia dostępu w deklarację „brak części”. Przed PCBA potrzebna jest akceptacja BOM przez JLC i potwierdzenie konkretnych dostaw.

### Przycisk

[Specyfikacja ALPS SKQGABE010 z października 2025](https://tech.alpsalpine.com/cms.media/SKQGAB_KQG_719_EN_cc4e10226e.pdf) i [aktualna strona producenta](https://tech.alpsalpine.com/e/products/detail/SKQGABE010/) potwierdzają przycisk top-push, 5.2×5.2×1.5 mm, nominalnie 1.57 N, skok 0.25 mm. Minimum pracy kontaktu wynosi 10 µA przy 1 V; pullup 100 kΩ przy 3 V daje około 30 µA. Przycisk nie jest uszczelniony. Obudowa musi chronić go przed potem i pyłem, ograniczać nadmierny skok oraz naciskać centralnie.

Lokalny footprint zawiera cztery fizyczne pady, ale tylko dwa numery elektryczne:

| Numer pada | Środki padów względem środka footprintu | Rozmiar każdego pada |
|---|---|---|
| 1 | (−3.1, −1.85), (+3.1, −1.85) mm | 1.8×1.1 mm |
| 2 | (−3.1, +1.85), (+3.1, +1.85) mm | 1.8×1.1 mm |

Courtyard ma 8.5×5.7 mm. Biblioteka zawiera strefy keepout na F.Cu po bokach przycisku; nie usuwać ich przy importowaniu. Symbol dwupinowy ma przypisać odpowiednio `USER_BTN_N` i GND. Nie tworzyć czterech różnych sygnałów dla czterech końcówek. Model `SW_SPST_SKQG_WithStem.step` istnieje w lokalnej bibliotece KiCad.

Dokumentacja ALPS zaleca ograniczenie impulsu przy obciążeniu pojemnościowym. Przyjęta decyzja A0 zachowuje C17 100 nF i dodaje **R25 1 kΩ** między pinem 2 SW1 (`SW_RETURN`) a GND. Wybrano **UNI-ROYAL 0402WGF1001TCE, JLC C11702**, [bezpośredni rekord JLC](https://jlcpcb.com/partdetail/C11702): 1 kΩ ±1%, 62.5 mW, 50 V, TCR ±100 ppm/K, Basic, SMT Economic/Standard. Footprint: `Resistor_SMD:R_0402_1005Metric`.

R25 ogranicza początkowy prąd rozładowania C17 z 3 V do około 3 mA, a przy pullup 100 kΩ pozostawia ustalony niski poziom około 30 mV. Stała czasowa rozładowania wynosi około 0.1 ms, narastania około 10 ms. Są to obliczenia nominalne; odbicia i progi GPIO należy sprawdzić. R25 ogranicza prąd rozładowania kondensatora; nie zastępuje kwalifikowanej ochrony ESD portu/przycisku. Netlistę i generator aktualizuje agent główny.

SKRPACE010/C139797 był również rzeczywistym małym kandydatem, lecz nie znaleziono dokładnego gotowego footprintu w lokalnej bibliotece. Nie jest aktualnym wyborem SW1. Wybrany SKQG umożliwia użycie istniejącego footprintu i modelu bez zgadywania geometrii.

### Dioda

[Oficjalna karta Everlight DSE-0014851 Rev.4](https://www.everlighteurope.com/custom/files/datasheets/DSE-0014851.pdf) określa dla wybranego D1 nominalne VF 2.0 V, maksimum 2.4 V przy 20 mA oraz korpus 0603. Część jest również wymieniona w [katalogu producenta 2026–2027](https://www.everlighteurope.com/files/cto_layout/img/Everlight/Online_Catalogs/2026-2027_Everlight_Catalogue.pdf). Nie wybieramy wcześniejszego `19-217/G7C-BK2L2VY/3T`/C264462, który okazał się EOL.

Zachować R17 2.2 kΩ jako początkową wartość. Orientacyjne obliczenie dla VF 2.0 V daje około 0.45 mA przy GPIO nisko; rzeczywiste VF przy tym prądzie jest inne od specyfikowanego przy 20 mA. Widoczność przez obudowę trzeba sprawdzić. Krótkie impulsy statusu ograniczają zużycie energii.

Footprint standardowy ma pad 1 = katoda, pad 2 = anoda. Obecny symbol D1 również używa 1 = `LED_K`, 2 = `LED_A`. Sprawdzić marker katody na rysunku producenta i podglądzie orientacji JLC przed zatwierdzeniem CPL. Generyczny model STEP LED 0603 służy wizualizacji; wysokość i otwór w obudowie należy brać z dokumentacji rzeczywistej części.

### Złącze i pakiet

[Oficjalna dokumentacja JST SH](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf) zawiera dokładny SM03B-SRSS-TB, pasującą obudowę **SHR-03V-S** i styki **SSH-003T-P0.2-H**. Raster 1.0 mm, prąd znamionowy 1 A przy AWG28, korpus 3-pin około 5.0×4.25 mm i wysokość około 2.9 mm. Do obudowy trzeba dodać przestrzeń na wtyk, zagięcie przewodów i chwyt przy rozłączaniu.

W lokalnej bibliotece potwierdzono footprint i STEP. Pady sygnałowe mają środki x=−1,0,+1 mm przy y=−2 mm, rozmiar 0.6×1.55 mm. Dwa pady mocujące `MP` są mechaniczne; nie są dodatkowym stykiem baterii. Courtyard rozciąga się maksymalnie do x=±3.4 i y=±3.28 mm. Zachować pin 1 wskazany przez bibliotekę i producenta — nie odczytywać kolejności według przypadkowego widoku zdjęcia.

Wymagany pinout instalacji: **1 VBAT+, 2 NTC_TS, 3 GND**. To własna specyfikacja projektu, a nie uniwersalny pinout baterii JST. Wymaga oznaczenia na PCB i sprawdzenia miernikiem każdej wiązki przed podłączeniem. Nie zakładać zgodności gotowego pakietu na podstawie samego kształtu wtyczki.

Docelowo: chroniony pakiet LiPo 1S, **300 mAh**, 4.2 V ładowania, PCM oraz NTC 10 kΩ fizycznie na ogniwie. Krzywa NTC i graniczne R(0°C)/R(45°C) muszą spełniać [przegląd zasilania](power_review.md). Nie znaleziono i nie wpisano fikcyjnego gotowego MPN pakietu. Dostawca baterii musi potwierdzić prąd, temperaturę, geometrię, przewody i tabelę R(T). Montaż pakietu i wiązki jest oddzielną operacją po reflow PCBA.

Alternatywa na prototyp: trzy duże pola przewodowe, z jednoznacznym opisem `+ / T / −` i odciążeniem przewodów w obudowie. Takie pola nie mają MPN ani numeru JLC; nie należy tworzyć dla nich fikcyjnej pozycji zakupowej. Obecna decyzja głównego projektanta pozostawia JST SH.

## MLCC: wynik kontroli i konieczna korekta

`Ceff` oznacza pojemność podczas pracy, a nie wartość wydrukowaną w BOM. Oceniono przypisania z `design.json` i [dobór pasywów](passives_sourcing.md). Krzywe DC-bias Samsung są udostępniane przez dynamiczną bibliotekę; pobranie kompletnych liczbowych modeli/krzywych w tym środowisku nie powiodło się. Nie wpisano odczytów, których nie uzyskano.

| Referencje / napięcie | Stan i zalecenie |
|---|---|
| **C1 na VBUS, C3 na VBAT** | Dotychczasowe 1 µF ±10% nie gwarantuje ≥1 µF efektywnie już z samej tolerancji. **Zmieniamy dobór na Samsung CL10A225KA8NNNC, 2.2 µF/25 V/X5R/0603, JLC C57895.** Pozostaje kontrola pełnego Ceff przy VBUS do 5.5 V i VBAT do 4.2 V. |
| C2, SYS około 4.5 V | CL10A106KP8NNNC, 10 µF/10 V/0603; wymagane ≥1 µF efektywnie przy nominalnym 10 µF według BQ25185. MPN pozostaje kandydatem z dużym zapasem nominalnym; brak zatwierdzonego minimum dla wszystkich warunków. |
| C4, IN LDO około 4.5 V | CL10A225KO8NNNC, 2.2 µF/16 V/0603; wymagane lokalnie ≥0.47 µF efektywnie. Nie zatwierdzono pełnej charakterystyki przy 4.5 V. |
| C5, OUT LDO około 3 V | CL10A106KP8NNNC, 10 µF/10 V/0603. Znaleziono liczbową informację producenta układów TI dla dokładnego MPN: **5.2 µF przy DC-bias 3.3 V**, [LM3281, tabela 6](https://www.ti.com/lit/ds/symlink/lm3281.pdf). To dane projektowe typowe, nie gwarantowane minimum w temperaturze i po starzeniu. Margines do minimum LDO 0.47 µF jest znaczny. |
| C9/C11/C16, 4.7 µF/10 V/0603 | CL10A475KP8NNNC potwierdzony w Samsung; krzywych liczbowych przy 3 V i 5.5 V nie pozyskano. C11 jest istotny dla USB/VBUS modułu. |
| 100 nF przy pinach | CL05B104KO5NNNC pozostaje lokalnym odsprzęganiem; dodatkowy bulk nie zastępuje jego bliskiego umieszczenia. |

Nowy C1/C3: [JLC C57895](https://jlcpcb.com/partdetail/58932-CL10A225KA8NNNC/C57895), [oficjalna strona Samsung](https://product.samsungsem.com/mlcc/CL10A225KA8NNN.do), [specyfikacja producenta udostępniona przez DigiKey](https://media.digikey.com/pdf/Data%20Sheets/Samsung%20PDFs/CL10A225KA8NNNC-Spec.pdf). Zmiana zachowuje footprint 0603. Wymóg X5R ogranicza profil temperaturowy do zakresu tej klasy; nie jest automatycznym zamiennikiem X7R dla dowolnej temperatury.

Przykładowy budżet do oceny krzywych, **nie gwarancja części**: tolerancja 0.9 × temperatura 0.85 × rezerwa starzenia 0.9 =0.6885. Dla 2.2 µF i wymagania 1 µF pozostaje wymagane zachowanie co najmniej około 66% wartości nominalnej pod samym DC-bias. Dokładny łączny limit wymaga danych producenta; temperatury i DC-bias nie zawsze można traktować jako niezależne mnożniki.

Po zmianie C1 suma bezpośrednich pojemności na VBUS C1+C11 wynosi 6.9 µF nominalnie, do około 7.59 µF z tolerancją +10%. Nie zamyka to sprawy USB inrush: pojemności SYS i 3 V są dołączane przez power-path/LDO i trzeba sprawdzić ich rzeczywisty prąd rozruchu. Nie dopisywać arbitralnie „USB compliant”.

## Zachowanie obecnej topologii zasilania

Pozostawienie U7/U8/Q1/Q2 jest uzasadnione na A0: okno NTC działa sprzętowo, supervisor blokuje przed ustaleniem zasilania, a MCU może tylko zabronić ładowania. Sam BQ25185 z bezpośrednim NTC 10 kΩ/B3435 nie realizuje wymaganego 0–45°C. Liczba elementów nie jest powodem usunięcia tych funkcji podczas routingu.

Cena energetyczna jest jawna: około **138 µA** tego bloku w spodziewanym stanie battery-only, czyli około **3.31 mAh/dobę**, plus pozostałe układy. Dla samego tego obciążenia 300 mAh daje idealnie około 90 dni. Prąd ten jest mały wobec aktywnej rejestracji, lecz znaczący dla wielomiesięcznego przechowywania. Nie rozpoczynamy kolejnej architektury w A0. Pomiary standby, upływów, rozruchu, temperatury pakietu i pełnego cyklu ładowania pozostają wymagane; aktualne obliczenia są w `reports/charge_temperature_corners.json`.
