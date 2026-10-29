# A01 — C9/C10/C11 przy module Raytac

Data: **29.10.2026**. Zakres ograniczony do kondensatorów modułu i skutków ich zmiany dla VBUS. Bazowy HEAD `b17f1457de876ecb27e94dc514c9a4844be44bc0`, wejściowy PCB `cdcbd234…`; po korekcie wyłącznie C9 aktualny PCB ma SHA256 **`1d3bb700a2b686ef68589bf3295488d2144a1d51a857cec7651e45be175a6134`**. Nie powtarzano całego audytu zasilania, symulacji ani prób sprzętowych. [Dane, źródła i świeży natywny odczyt pięciu kondensatorów](../reports/production_caps_A1.json) można odtworzyć skryptem [review_production_caps_A1.py](../scripts/review_production_caps_A1.py), uruchamianym przez Python KiCad.

**Wynik: EXTERNAL CONFIRMATION.** C9 zmieniono minimalnie z 4.7 na **10 µF nominalnie** w tym samym 0603. To usuwa rozbieżność nominału względem wartości 10 µF zgłoszonej przez użytkownika z Raytac §8.3, **nie stanowi gwarancji 10 µF efektywnie**. C11 pozostaje **4.7 µF** do odpowiedzi Raytac o dopuszczalnym odsprzęganiu wejścia VBUS. Nie wykazano tu błędu sprzętu uzasadniającego oznaczenie C11 jako BLOCKED, ale nie zamknięto jego zgodności aplikacyjnej. Nie należy automatycznie zamieniać C11 na 10 µF.

## Wymagania: trzy różne węzły

| Węzeł | Obecny element / zakres | Co wiadomo |
|---|---|---|
| U3 VDD28/VDDH30, +3V0 | C9 **10 µF/10 V X5R**, C10 100 nF/16 V X7R; regulacja 2.955–3.045 V | To zewnętrzne zasilanie modułu. Przyjęto 10 µF jako nominalną korektę do podanego odniesienia Raytac. Nie ustalono gwarantowanego Ceff wymaganego przez Raytac. |
| U3 VBUS32 | C11 **4.7 µF/10 V X5R**; Nordic VBUS 4.35–5.5 V | To wejście regulatora sygnalizacji USB. C11 łączy się bezpośrednio z VBUS złącza, podobnie jak C1 przy BQ. |
| nRF52840 DECUSB | Nie jest wyprowadzony jako pad hosta modułu | Nordic określa C_DECUSB min/typ/max **2.35/4.7/5.5 µF na DECUSB**. Tego limitu nie wolno przypisywać C11 na VBUS. |

[Nordic POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html) rozdziela VBUS i wyjście DECUSB; liczby 2.35/4.7/5.5 µF są także w [oficjalnym PDF nRF52840 PS v1.9, §5.3.8.6, strona 156](https://docs-be.nordicsemi.com/bundle/nRF52840_PS_v1.9/raw/resource/enus/nRF52840_PS_v1.9.pdf). Bare-SoC [reference circuitry](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/ref_circuitry.html) nie jest samodzielną zgodą na odstępstwo od zewnętrznego obwodu modułu Raytac.

[Raytac Ver.L, 24.05.2023](https://www.raytac.com/download/index.php?index_id=43) określa §8.3 jako konfigurację dla napięcia poniżej 3.6 V. Dostępna [kopia dokumentu producenta w LCSC](https://atta.szlcsc.com/upload/public/pdf/source/20230606/35774BD2C96BA53AFB7E2DA8EC789E8F.pdf) identyfikuje ten rysunek na drukowanych stronach 40–41. **W tym przeglądzie nie uzyskano czytelnej bitmapy rysunku.** Wartość 10 µF pochodzi z odczytu zgłoszonego przez użytkownika, nie z fikcyjnie wykonanego wizualnego porównania. Nie rozstrzygnięto, czy jest to jedynie nominał obwodu referencyjnego, czy producent wymaga konkretnego minimum po deratingu. Odpowiedź Raytac musi dotyczyć oddzielnie VDD i VBUS.

## Dokładne części i minimalna zmiana

| Ref. | MPN i JLC | Decyzja / status |
|---|---|---|
| C9 | **Samsung CL10A106KP8NNNC, C19702**, 10 µF ±10%, 10 V, X5R, 0603 | **CLOSED — nominalna korekta wdrożona** i odczytana z PCB/design; nie zamyka Ceff ani całego A01. |
| C10 | Samsung CL05B104KO5NNNC, C1525, 100 nF ±10%, 16 V, X7R, 0402 | **CLOSED — identyfikacja i brak zmiany**. Mały kondensator pozostaje odrębnym odsprzęganiem; nie zastępuje C9. |
| C11 | **Samsung CL10A475KP8NNNC, C1705**, 4.7 µF ±10%, 10 V, X5R, 0603 | **EXTERNAL CONFIRMATION** aplikacji i Ceff przy VBUS; pozostawiono dotychczasowy element. |

Oficjalne strony Samsung potwierdzają [10 µF](https://product.samsungsem.com/mlcc/CL10A106KP8NNN.do) i [4.7 µF](https://product.samsungsem.com/mlcc/CL10A475KP8NNN.do): oba mają L/W/T **1.60±0.10 / 0.80±0.10 / 0.80±0.10 mm**. Zatem zamiana C9 nie wymaga większego footprintu. [JLC C19702](https://jlcpcb.com/partdetail/20411-CL10A106KP8NNNC/C19702), [C1705](https://jlcpcb.com/partdetail/2057-CL10A475KP8NNNC/C1705) i [C1525](https://jlcpcb.com/partdetail/C1525) potwierdzają dokładne MPN i montaż SMT Economic/Standard; nie jest to rezerwacja części.

Natywnie odczytano C1/C5/C9/C10/C11, ich wartości, MPN/JLC, pady, nety i położenia. C9 nadal jest pomiędzy +3V0 i GND w (68.6,68.0), 0°; C11 nadal VBUS–GND w (70.9,66.8), 90°. C9 wykorzystuje ten sam MPN co istniejący C5. Nie wprowadzono innego zamiennika C11 bez danych jego charakterystyk.

## Ceff: liczby odczytane i granice oszacowania

**C9, CL10A106KP8NNNC.** Oficjalna dokumentacja [TI LM3281, tabela 6, strona drukowana 16](https://www.ti.com/lit/ds/symlink/lm3281.pdf) podaje dla dokładnego MPN: **10 µF ±10%, 5.2 µF przy 3.3 V DC bias**. Jest to punkt danych projektowych TI, a nie odczytana krzywa Samsung ani gwarantowane minimum produkcyjne dla naszego zakresu temperatur, częstotliwości i starzenia. Nie przenosić go bez dowodu na 3.0 V, 5.0 V lub 5.5 V.

Czy do 5.2 µF można jeszcze zastosować tolerancję i temperaturę? **Nie ustalono, czy TI uwzględniło już ±10% w tej liczbie.** Tabela nie definiuje jej jako gwarantowanego minimum ani nie opisuje łącznego rozkładu błędów. Dodatkowe mnożenie tolerancji może więc podwójnie liczyć ten sam margines.

Arytmetycznie **5.2 ×0.90 ×0.85 =3.978 µF**. To wyłącznie **warunkowe oszacowanie**, gdyby 5.2 opisywało wartość nominalną w temperaturze odniesienia, a dodatkowe −10% tolerancji i −15% TCC można było niezależnie dołożyć. Nie jest to gwarantowany bound. [Samsung, kod temperatury](https://product.samsungsem.com/mlcc/basic-search.do) definiuje X5R jako −55…+85°C, ±15%, lecz [Samsung Caution/Notice](https://product.samsungsem.com/resources/file/product-catalog/MLCC_2401.pdf) odróżnia TCC od Bias TCC i wymaga uwzględnienia napięcia, temperatury oraz starzenia. Zwykłe ±15% nie dowodzi niezależnego dodatkowego mnożnika przy danym bias. Nie dodano arbitralnego procentu starzenia.

**C11, CL10A475KP8NNNC.** Odczytano nominał i ±10%; początkowy zakres przy warunkach pomiaru to 4.23–5.17 µF. **Nie odczytano numerycznej krzywej DC-bias dla tego MPN przy 5.0/5.5 V ani Bias TCC.** Oficjalna strona i biblioteka Samsung nie przekazały w tym środowisku danych wykresu. Nie podano procentu utraty, minimum Ceff ani wartości zastępczej z innego MPN. Dostępna przykładowa krzywa 10 µF/6.3 V w katalogu Samsung nie dotyczy C1705 i nie została użyta do jego obliczeń.

Status gwarantowanego Ceff **obu** kondensatorów pozostaje **EXTERNAL CONFIRMATION**. Zamiana C9 poprawia zgodność nominału; nie zamienia nieznanego minimum w 10 µF efektywnie.

## C11 a pojemność bezpośrednio na USB

| Wariant | C1 + C11 nominalnie | Z początkową tolerancją obu ±10%, bez modelu bias |
|---|---:|---:|
| Obecny | 2.2 +4.7 = **6.9 µF** | **6.21–7.59 µF** |
| Automatyczna zamiana C11 na 10 µF | 2.2 +10 = **12.2 µF** | **10.98–13.42 µF** |

Oba kondensatory są przed ogranicznikiem wejściowym BQ. Nastawa BQ nie ogranicza ich bezpośredniego ładowania przy wpięciu kabla. [TI SLVA129](https://www.ti.com/lit/pdf/slva129) opisuje regułę 10 µF dla bezpośrednio dołączonego obciążenia USB i ograniczanie inrush przy większej pojemności. Wariant 12.2 µF **nie daje prostego konserwatywnego dowodu zgodności z tą regułą** i nie został przyjęty. Nie jest to jednocześnie pomiar przekroczenia: dla nieliniowego MLCC ładunek zależy od całego C(V), a nie tylko od pojemności końcowej przy 5 V. Bez tej charakterystyki nie wolno uzasadniać inrush samym spadkiem C pod napięciem.

Również obecne 6.9 µF nie jest testem inrush całego urządzenia: dochodzą pozostałe wejścia/moduł i obciążenia za BQ/LDO. C9 rośnie o 5.3 µF nominalnie **za** BQ i LDO, zatem nie zwiększa powyższej bezpośredniej sumy VBUS, ale zmienia obciążenie rozruchu i należy uwzględnić je w zaplanowanym pomiarze całego portu. Nie rozszerzano tu audytu firmware ani budżetu stanów USB.

## Co zamyka otwarte punkty

Do **Raytac** skierować przegląd konfiguracji MDBT50Q-P1MV2, VDD/VDDH=3.0 V i oddzielne VBUS=4.35–5.5 V:

1. Czy 10 µF na odpowiednich liniach §8.3 jest nominałem referencyjnym, czy minimum efektywnym? Jaki zakres Ceff, ESR i tolerancji jest dopuszczalny na VDD i osobno na VBUS?
2. Czy C11=CL10A475KP8NNNC 4.7 µF/10 V jest dopuszczalny na wejściu VBUS tego modułu, z C1=2.2 µF przy ładowarce? Jeśli nie, jaki wariant zachowuje wymagania USB inrush bez nieuzasadnionego przebudowania zasilania?
3. Czy C9=CL10A106KP8NNNC 10 µF/10 V wraz z C10=100 nF jest zgodny z tym odniesieniem przy 3.0 V? Jakie minimum po deratingu ma zapewnić projekt?

Od **Samsung** potrzebne są dane dla dokładnych MPN: C(V,T), Bias TCC, warunki pomiaru, tolerancje i starzenie oraz wyjaśnienie, które krzywe są tylko typowe. Po odczycie krzywych można liczyć oszacowanie; gwarantowany bound wymaga odpowiednich limitów specyfikacji.

**JLC nie zastępuje Raytac w zatwierdzaniu aplikacji regulatora USB ani minimum Ceff.** JLC może potwierdzić MPN, zakup, montaż, footprint/DFM i poprawność importu; kondensatory MLCC są niepolarne. Pomiar inrush wymaga osobno uzgodnionego testu i kryteriów. Zwykłe przyjęcie BOM/CPL/CAM nie jest takim pomiarem ani zgodą na C11.

Nie wysyłano korespondencji do producentów. C9 ma zamkniętą korektę nominalną i identyfikację; C11 oraz granice Ceff pozostają **EXTERNAL CONFIRMATION**. Brak dostępu do krzywej jest ograniczeniem dowodu, nie dowodem usterki hardware.
