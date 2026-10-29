# Elementy pasywne — zweryfikowane numery katalogowe

Data sprawdzenia: **2026-10-27**. Dokument uzupełnia projekt roboczy; nie jest potwierdzeniem rezerwacji części ani gotowości PCBA. Numery C poniżej zostały rzeczywiście znalezione w podanych katalogach. Rozróżniono potwierdzenie JLCPCB i samo LCSC. Stan magazynu, cena, MOQ i Basic/Extended wymagają ponownego sprawdzenia w BOM Tool przy składaniu zamówienia. Nie traktować braku dostępu narzędzia do strony JLC jako dowodu braku obsługi części.

## Rezystory 0402, ±1%

Zwykłe rezystory mają moc 62,5 mW, napięcie robocze 50 V i TCR ±100 ppm/°C według wymienionych stron. Przy 3–5 V ich moc jest wystarczająca dla wskazanych funkcji; nie są to rezystory pomiarowe prądu.

| Wartość | Referencje obecnego schematu | Producent i dokładny MPN | Numer C i źródło | Status potwierdzenia |
|---|---|---|---|---|
| 24 kΩ ±1% | R1 | UNI-ROYAL **0402WGF2402TCE** | **C25769**, [LCSC](https://lcsc.com/product-detail/Chip-Resistor-Surface-Mount_Uniroyal-Elec-0402WGF2402TCE_C25769.html) | MPN, wartość i obudowa potwierdzone w LCSC; bezpośrednia strona JLC niedostępna narzędziu |
| 2,00 kΩ ±1% | R2 | YAGEO **RC0402FR-072KL** | **C60488**, [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-RC0402FR072KL/C60488) | JLC SMT, Economic and Standard; wariant preferowany w tej tabeli |
| 2,00 kΩ ±1%, alternatywa | R2 | UNI-ROYAL **0402WGF2001TCE** | **C4109**, [LCSC](https://www.lcsc.com/product-detail/C4109.html) | LCSC potwierdzone; montaż konkretnego rekordu JLC niepotwierdzony w tym odczycie |
| 100 kΩ ±1% | R3, R9, R10, R12, R13, R16 | UNI-ROYAL **0402WGF1003TCE** | **C25741**, [JLCPCB](https://jlcpcb.com/partdetail/0402WGF1003TCE/C25741) | JLC SMT, Economic and Standard |
| 10,0 kΩ ±1% | R4, R5, R8, R22 | UNI-ROYAL **0402WGF1002TCE** | **C25744**, [JLCPCB](https://jlcpcb.com/partdetail/0402WGF1002TCE/C25744) | JLC SMT, Economic and Standard |
| 1,00 MΩ ±1% | R6, R7, R23 | UNI-ROYAL **0402WGF1004TCE** | **C26083**, [JLCPCB](https://jlcpcb.com/partdetail/0402WGF1004TCE/C26083) | JLC SMT, Economic and Standard |
| 22,0 Ω ±1% | R11 | UNI-ROYAL **0402WGF220JTCE** | **C25092**, [JLCPCB](https://jlcpcb.com/partdetail/25835-0402WGF220JTCE/C25092) | MPN/obudowa i obecność w JLC potwierdzone; wartość tłumienia pozostaje do prób sygnałowych |
| 5,10 kΩ ±1% | R14, R15 | UNI-ROYAL **0402WGF5101TCE** | **C25905**, [JLCPCB](https://jlcpcb.com/partdetail/0402WGF5101TCE/C25905) | JLC SMT, Economic and Standard; osobny rezystor na każdej linii CC |
| 2,20 kΩ ±1% | R17 | UNI-ROYAL **0402WGF2201TCE** | **C25879**, [JLCPCB](https://jlcpcb.com/partdetail/0402WGF2201TCE/C25879) | JLC SMT, Economic and Standard |

[Oficjalna karta YAGEO RC0402FR-072KL](https://www.yageogroup.com/component-documentation/download/specsheet/RC0402FR-072KL) niezależnie potwierdza 0402, 2 kΩ, 1%, 0,063 W i TCR ±100 ppm/°C. Rezystory NTC-reference z następnej tabeli nie mogą być automatycznie zastępowane rezystorami 1%.

## Rezystory precyzyjne 0402, ±0,1%

**Aktualizacja R18:** bieżący schemat używa **100 kΩ ±0,1%**, po zmianie progu HOT dla najniższego napięcia przed zadziałaniem U8 (2,5872 V). Wcześniejsze 115 kΩ pozostawiono w tabeli wyłącznie jako historię doboru; nie jest wartością do obecnego BOM.

| Wartość i funkcja | Producent i dokładny MPN | Numer C i źródło | Status / ograniczenie |
|---|---|---|---|
| **100 kΩ ±0,1%, obecne R18 — preferowany** | Panasonic **ERA2AEB104X** | **C445619**, [JLCPCB](https://jlcpcb.com/partdetail/PANASONIC-ERA2AEB104X/C445619), [producent](https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA2AEB104X) | 0402, 63 mW, 50 V, **TCR ±25 ppm/°C**; JLC SMT Economic and Standard, MSL1. Wartość, tolerancję i TCR potwierdza również producent |
| 100 kΩ ±0,1%, alternatywa obecnego R18 | YAGEO **RT0402BRD07100KL** | **C852472**, [LCSC](https://www.lcsc.com/de/product-detail/C852472.html), [producent](https://www.yageogroup.com/component-documentation/download/specsheet/RT0402BRD07100KL) | 0402, 62,5 mW, TCR ±25 ppm/°C; LCSC potwierdzone. Bezpośredniego rekordu JLC nie potwierdzono |
| 115 kΩ ±0,1%, **historyczne, nie montować jako R18** | Viking **ARG02BTC1153** | **C5266097**, [LCSC](https://www.lcsc.com/product-detail/C5266097.html) | 0402, 62,5 mW, TCR ±25 ppm/°C; LCSC potwierdzone, montaż/zapas JLC niepotwierdzony |
| 115 kΩ ±0,1%, **historyczna alternatywa** | YAGEO **RT0402BRE07115KL** | **C852990**, [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-RT0402BRE07115KL/C852990) | Realny rekord JLC, 0402, 63 mW, **TCR ±50 ppm/°C**, stan publicznej strony 0; nie przedstawiać jako dostępnego z magazynu |
| 27,4 kΩ ±0,1%, R20 | YAGEO **RT0402BRD0727K4L** | **C852679**, [LCSC/szlcsc](https://item.szlcsc.com/913001.html) | 0402, 62,5 mW, TCR ±25 ppm/°C; MPN/wartość/numer potwierdzone. Montaż/zapas JLC niepotwierdzony |
| 10,0 kΩ ±0,1%, R19 i R21 | YAGEO **RT0402BRD0710KL** | **C190095**, [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-RT0402BRD0710KL/C190095) | 0402, 62,5 mW, TCR ±25 ppm/°C, JLC Economic and Standard; publiczny katalog pokazał zapas |

Tolerancja początkowa **±0,1%** nie obejmuje dowolnej temperatury ani starzenia. Model w `scripts/check_charge_temperature.py` przyjmuje dla każdego rezystora odniesienia **łączny budżet ±0,5%**, niezależnie dla poszczególnych rezystorów. Początkowe 0,1% + maksymalny dopuszczony TCR 50 ppm/K ×65 K daje 0,425%, zaokrąglone do 0,5%; pozostający zapas musi pokryć pozostały dryft w rzeczywistym profilu pracy. To założenie obliczeniowe, nie zamiennik kwalifikacji starzenia i lutowania. Wybrany Panasonic ma TCR 25 ppm/K. Nie zastępować elementów dowolnymi rezystorami 0,5%: wymóg BOM pozostaje **0,1% początkowo i TCR ≤50 ppm/K**. Przykładowo dla dwóch niezależnych rezystorów ±25 ppm/K i zmiany temperatury o 30 K sam najgorszy rozjazd ilorazu może osiągnąć około 0,15%. Przed zamówieniem ponownie potwierdzić dostępność wszystkich precyzyjnych MPN w JLC, szczególnie R20.

## Kondensatory

Wartości napięcia w wymaganiach należy traktować jako **minimum napięcia znamionowego**. Podniesienie 10 V do 16 V przy tym samym footprintcie jest dopuszczalne po sprawdzeniu rzeczywistej charakterystyki DC-bias wybranego MPN; sam wyższy rating nie gwarantuje większej pojemności efektywnej.

| Wymaganie / referencje | Producent i dokładny MPN | Parametry faktycznej części | Numer C i źródło | Status |
|---|---|---|---|---|
| 100 nF, ≥10 V, X7R, 0402; C6, C10, C12, C13, C15, C17, C18 | Samsung **CL05B104KO5NNNC** | 100 nF, 16 V, X7R, ±10%, 0402 | **C1525**, [JLCPCB](https://jlcpcb.com/partdetail/CL05B104KO5NNNC/C1525) | JLC rekord i parametry potwierdzone |
| 1 µF, ≥10 V, X7R, 0402; obecne C14 | **Dokładnego kandydata nie potwierdzono** | — | — | Nie wpisano zgadywanego numeru; dwa realne rozwiązania poniżej |
| C14 — wariant zachowujący 0402, wymaga zmiany X7R→X5R | Samsung **CL05A105KP5NNNC** | 1 µF, 10 V, **X5R**, ±10%, 0402 | **C14445**, [JLCPCB](https://jlcpcb.com/partdetail/15107-CL05A105KP5NNNC/C14445), [producent](https://product.samsungsem.com/mlcc/CL05A105KP5NNN.do) | Dostępny rzeczywisty kandydat; nie zatwierdzono Ceff przy 3 V |
| C14 — preferowany wariant: 0603 X7R; również C1 1µF/16V i C3 1µF/10V | YAGEO **CC0603KRX7R7BB105** | 1 µF, **16 V**, X7R, ±10%, **0603** | **C106248**, [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R7BB105/C106248) | JLC SMT, Economic and Standard; dla C14 zmienia się tylko footprint, nie obrys płytki |
| 1 µF/16V/X7R/0603, alternatywa | FH **0603B105K160NT** | 1 µF, 16 V, X7R, ±10%, 0603 | **C93816**, [JLCPCB](https://jlcpcb.com/partdetail/95014-0603B105K160NT/C93816) | JLC SMT, Economic and Standard; ponownie sprawdzić DC-bias przy zamianie producenta |
| 1 µF/16V/X7R/0603, alternatywa z danymi Samsung | Samsung **CL10B105KO8NNNC** | 1 µF, 16 V, X7R, ±10%, 0603 | **C59782**, [LCSC](https://www.lcsc.com/product-detail/C59782.html), [producent](https://product.samsungsem.com/mlcc/CL10B105KO8NNN.do) | LCSC potwierdzone; bezpośrednia strona JLC niedostępna narzędziu |
| 10 pF/C0G/0402; C7, C8 | Samsung **CL05C100JB5NNNC** | 10 pF, 50 V, C0G, ±5%, 0402 | **C32949**, [JLCPCB](https://jlcpcb.com/partdetail/33914-CL05C100JB5NNNC/C32949), [producent](https://product.samsungsem.com/mlcc/CL05C100JB5NNN.do) | JLC Basic, Economic and Standard; wartość obciążenia kwarcu nadal wymaga oceny CL i pasożytów |
| 10 µF/10V/X5R/0603; C2, C5 | Samsung **CL10A106KP8NNNC** | 10 µF, 10 V, X5R, ±10%, 0603 | **C19702**, [JLCPCB](https://jlcpcb.com/partdetail/C19702), [producent](https://product.samsungsem.com/mlcc/CL10A106KP8NNN.do) | JLC Basic, Economic and Standard |
| 2,2 µF/10V minimum/X5R/0603; C4 | Samsung **CL10A225KO8NNNC** | 2,2 µF, **16 V**, X5R, ±10%, 0603 | **C23630**, [JLCPCB](https://jlcpcb.com/partdetail/CL10A225KO8NNNC/C23630), [producent](https://product.samsungsem.com/mlcc/CL10A225KO8NNN.do) | JLC Basic, Economic and Standard; propozycja podniesienia ratingu z 10 do 16 V |
| 2,2 µF/10V/X5R/0603, dokładny wariant pierwotny | Samsung **CL10A225KP8NNNC** | 2,2 µF, 10 V, X5R, ±10%, 0603 | **C1607**, [LCSC](https://www.lcsc.com/product-detail/C1607.html), [producent](https://product.samsungsem.com/mlcc/CL10A225KP8NNN.do) | LCSC potwierdzone; bezpośrednia strona JLC niedostępna narzędziu |
| 4,7 µF/10V/X5R/0603; C9, C11, C16 | Samsung **CL10A475KP8NNNC** | 4,7 µF, 10 V, X5R, ±10%, 0603 | **C1705**, [JLCPCB](https://jlcpcb.com/partdetail/2057-CL10A475KP8NNNC/C1705) | JLC SMT, Economic and Standard |

### DC-bias i dopuszczalne zmiany

Nie zatwierdzono arbitralnej zamiany X7R na X5R na podstawie oznaczenia 10 V. Oba dielektryki tracą pojemność pod napięciem stałym; X7R/X5R opisują przede wszystkim zakres i zmienność temperaturową. Wartość nominalna w BOM nie jest minimalną pojemnością podczas pracy. Dla wszystkich krytycznych MLCC trzeba dołączyć dane wybranego producenta przy rzeczywistym napięciu, tolerancji, temperaturze i starzeniu.

W obecnym schemacie **C14 jest dodatkowym bulk przy IMU**, a wymagane 100 nF przy VDD i VDD_IO realizują osobne C12/C13. To daje podstawę do rozważenia X5R 0402, jeśli mieści się w temperaturze roboczej i po uwzględnieniu DC-bias pozostawia wystarczający zapas dla założonej funkcji. Nie podano tu nieodczytanej wartości pojemności przy 3 V. Preferowana propozycja zachowuje X7R i przenosi C14 na 0603/C106248; nie wymaga powiększenia obrysu PCB, ale wymaga uwzględnienia w rozmieszczeniu.

Źródła Samsung umożliwiają sprawdzenie dokładnego MPN i danych materiałowych: [CL05A105KP5NNNC — specyfikacja producenta przez DigiKey](https://media.digikey.com/pdf/Data%20Sheets/Samsung%20PDFs/CL05A105KP5NNN_Specsheet%20%281%29.pdf), [CL10A225KO8NNNC — specyfikacja producenta](https://media.digikey.com/pdf/Data%20Sheets/Samsung%20PDFs/CL10A225KO8NNNC_Spec.pdf). Krzywe charakterystyk mogą wymagać biblioteki symulacyjnej producenta; nie zostały zamienione tutaj na rzekome pomiary ani gwarantowane minima.

Weryfikacja przed zwolnieniem zasilania: C1 musi zachować wymagane minimum efektywne na VBUS; C3 na VBAT; C4/C5 muszą zapewniać wymagane minima i ESR TPS7A20 na IN/OUT; C2 minimum dla SYS przy 4,5 V. Przy C11 należy potwierdzić wymagania Raytac VBUS/USB i łączną pojemność wejściową portu. Kondensatory dodatkowe nie zastępują lokalnego odsprzęgania przy pinach układów.

Dokument nie modyfikuje generatora ani manifestu. Aktualne przypisanie referencji trzeba ponownie porównać z `hardware/design.json`, jeżeli numeracja komponentów zmieni się podczas dalszych prac.
