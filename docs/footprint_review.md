# Footprinty U3, U4 i Y1 — źródła i geometria

Data: 2026-10-28. Źródło lokalne: biblioteki dostarczone z **KiCad10.0.7**, `/Applications/KiCad/KiCad.app/Contents/SharedSupport`. Pliki projektu, SHA256 źródeł i wynik natywnego ładowania zapisano w `hardware/geometry_sources/imu_rf_geometry.json`. Pełne współrzędne padów wraz z aktualnymi netami są w `reports/imu_rf_pad_geometry.csv`.

| Ref | Identyfikator footprintu projektu | Podstawa |
|---|---|---|
| U3 | `AnkleSensor:Raytac_MDBT50Q` | Oficjalna biblioteka KiCad; dokładny symbol MDBT50Q-P1MV2 wskazuje ten footprint |
| U4 | `AnkleSensor:ST_LSM6DSV32X_LGA14_3x2.5mm_P0.5mm` | Adaptacja KiCad LGA14 według DS13511 i TN1383 |
| Y1 | `AnkleSensor:Crystal_SMD_3215-2Pin_3.2x1.5mm` | Biblioteczny footprint3215, korpus zgodny z ABS07; kontrola land-pattern producenta pozostaje do DFM |

## U3: Raytac

W `RF_Module.kicad_sym` dokładny wariant **MDBT50Q-P1MV2** dziedziczy po MDBT50Q-1MV2 i używa `RF_Module:Raytac_MDBT50Q`. Numeracja wszystkich61padów odpowiada wcześniej sprawdzonej tabeli Raytac Ver.L oraz projektowemu symbolowi. Nie użyto footprintu starszego układu o innej numeracji.

Skopiowano niezmienioną geometrię miedzi, masek, pasty i keepout; jedyna zmiana pliku to lokalna ścieżka STEP. Układ współrzędnych TOP: antena skierowana ku **ujemnemuY**. Obrys korpusu ma x=±5.25mm, y=±7.75mm. Wszystkie pady mają rozmiar0.6×0.4mm; dolne i wewnętrzne są odpowiednio obrócone. Pad1=(-4.65,-3.75),28=(1.6,7.15),30=(2.4,7.15),31=(3.2,7.15),32=(4.0,7.15). Pady56–61 mają y=0.55mm i x=-2,-1.2,-0.4,0.4,1.2,2mm.

Footprint zawiera dwie rzeczywiste strefy zakazu:

- Antena: x=-6.2…6.2mm, y=-7.75…-4.0mm; wszystkie warstwy miedzi. Zakazane ścieżki, vias, pady i wylewki.
- Obszar na TOP pod modułem: x=-2.3…-0.7mm, y=-3.95…-2.75mm; również bez miedzi, ścieżek i vias.

[Raytac Ver.L](https://www.raytac.com/tw/download/index.php?index_id=24) wymaga keepout na każdej warstwie. Biblioteczna strefa to dane wejściowe do PCB; obudowa, bateria i inne metalowe części także muszą pozostać poza anteną. Projektant PCB powinien zachować dodatkowy zapas tam, gdzie pozwala kształt płytki. Nie traktować samego courtyardu jako granicy RF.

DCCH31NC pozostaje zgodne z wcześniej znalezioną odpowiedzią wsparcia Nordic, ale nie uzyskano nowego lokalnego schematu referencyjnego Raytac §8.3. Skopiowanie footprintu nie zmienia statusu tego przeglądu elektrycznego.

## U4: LSM6DSV32X

[ST DS13511 Rev2, rys.33](https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf) podaje korpus3×2.5mm,14terminali0.475×0.25mm i raster0.5mm. Biblioteka KiCad LGA14 ma zgodną topologię4+3+4+3, centra i numerację. Wariant projektu zachowuje te centra, a miedź zmienia z0.625×0.35mm na **0.575×0.35mm**: powiększenie terminala o0.1mm w obu kierunkach według [TN1383 §3.1](https://www.st.com/resource/en/technical_note/tn1383-pcb-design-guidelines-for-mems-sensors-stmicroelectronics.pdf).

Centra padów TOP:

| Pady | x [mm] | y [mm] |
|---|---:|---|
|1–4|-1.1625|-0.75,-0.25,0.25,0.75|
|5–7|-0.5,0,0.5|0.9125|
|8–11|1.1625|0.75,0.25,-0.25,-0.75|
|12–14|0.5,0,-0.5|-0.9125|

Pasta ma współczynnik-0.05; KiCad potwierdził marginesy-0.02875/-0.0175mm, czyli otwór81% powierzchni prostokąta pada przed uwzględnieniem zaokrągleń. Wielkość rzeczywistego otworu i grubość szablonu podlegają kontroli montażowej. Dodano centralny TOP keepout x=±0.85mm,y=±0.6mm. Podczas routingu trzeba ponadto prowadzić każde wyjście pada na zewnątrz i nie prowadzić ścieżek między padami pod korpusem; centralny prostokąt nie zastępuje całej reguły mechanicznej ST.

## Y1: ABS07

Aktualizacja A1: dokładny **ABS07-32.768KHZ-7-T** jest dostępny katalogowo w JLCPCB jako **[C276424](https://jlcpcb.com/partdetail/AbraconLLC-ABS07_32_768KHZ_7T/C276424)**, SMT Economic/Standard. Kartę sprawdzono 2026-10-28; nie jest to rezerwacja magazynu. MPN, numer C i oficjalny datasheet uzupełniono w schemacie, PCB i BOM. Parametry producenta: CL7pF, ESR maks.70kΩ, ±20ppm w25°C; C7/C8 wymagają kwalifikacji z rzeczywistymi pojemnościami pasożytniczymi.

W przeglądzie routingu wykryto długą gałąź LF_XL2. Obrót niepolaryzowanego Y1 o180° wyrównał kolejność padów z wyprowadzeniami modułu; obie sieci przetrasowano naF.Cu bez przelotek. Łączna długość miedzi, z odgałęzieniami do kondensatorów: LF_XL1=5.075mm, LF_XL2=4.951mm. Poprzednie LF_XL2=48.689mm/5vias usunięto. Końcowy DRC i zgodność ze schematem ponowiono; źródło liczb: `reports/lfxo_repair_report.json`. To poprawa geometrii, bez deklaracji pomierzonego startu i stabilności oscylatora.

[Oficjalny ABS07](https://abracon.com/Resonators/ABS07.pdf) potwierdza korpus3.2×1.5×0.9mm oraz suffix7 dla CL7pF. Biblioteczny footprint3215 ma dwa niepolaryzowane pady1×1.8mm o centrach x=±1.25mm,y=0; pad1 jest po prawej. Jego pierwotne źródło to Epson FC-135. Nie opisujemy go jako CAD producenta Abracon. Przed produkcją porównać land-pattern z rysunkiem ABS07; pojemności obciążenia i ESR pozostają oddzielnym przeglądem elektrycznym.

## STEP i wykonane kontrole

Modele są lokalnie w `hardware/3dmodels`; footprinty używają `${KIPRJMOD}`. To modele biblioteczne KiCad, nie nowe modele CAD producentów. Odczyt zakresu współrzędnych STEP daje maksymalneZ: Raytac2.06mm, LGA0.8mm i kwarc0.93mm. **Dla IMU obudowa musi uwzględniać0.86mm maksimum ST, mimo modelowego0.8mm.** Nie projektować obudowy na styk do modeli.

Po obejrzeniu natywnego renderu doprecyzowano ograniczenieU3: model`Raytac_MDBT50Q.step` pokazuje osobny blok przypominający antenęchip, natomiast wybranyP1MV2 ma antenęPCB. **Wspólny poprawny footprint61padów nie oznacza dokładnego modelu3D wariantuP1.** ModelU3 jest przybliżony; jego nominalna podstawa10.5×15.5mm pasuje, lecz geometria anteny i maksymalny gabarytP1 z tolerancjami nie są zatwierdzone. Zobacz `docs/mechanical_model_review.md` i uzupełniony manifest.

Natywne `pcbnew.FootprintLoad` w KiCad10.0.7 przeszło: U3=61padów/2strefy, U4=14padów/1strefa, Y1=2pady. Sprawdzono zbiory numerów względem aktualnego `design.json`; kontrola nie polegała wyłącznie na parsowaniu nawiasów. `kicad-cli fp export svg` poprawnie wyeksportował podglądy do `reports/footprint_preview`. Nie jest to jeszcze DRC kompletnej płytki ani oględziny pod mikroskopem.

Odtwarzanie: `scripts/prepare_imu_rf_footprints.py`, uruchamiany Pythonem dostarczonym z KiCad. Źródła bibliotek podlegają [CC-BY-SA4.0 z wyjątkiem KiCad](https://www.kicad.org/libraries/license/); autorstwo geometrii bazowej: społeczność KiCad, adaptacja U4: projekt Ankle SensorV1.
