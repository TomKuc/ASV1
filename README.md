# Ankle Sensor V1 — rewizja A1 do przeglądu

**NOT FOR FABRICATION — projekt nie jest zwolniony do zamówienia PCBA.**

KiCad 10.0.7 jest zainstalowany i przeprowadzono rzeczywiste kontrole. Schemat ma 72 symbole w pięciu arkuszach funkcjonalnych i główny arkusz hierarchii. PCB ma 69 footprintów, cztery warstwy, obrys **51,6 × 30 mm** i grubość roboczą 1,0 mm. Wszystkie połączenia są poprowadzone. Natywny końcowy DRC po wypełnieniu stref: **0 naruszeń, 0 niepołączonych elementów, 0 rozbieżności schemat–PCB**. Projekt wymaga dalszego przeglądu elektrycznego/DFM i zamknięcia wymienionych poniżej warunków przed zamówieniem. [Raport walidacji](reports/validation_status.json) podaje rzeczywiste wyniki i hashe wejść.

## Pliki projektu

- [Projekt KiCad](hardware/Ankle_Sensor_V1.kicad_pro), [schemat](hardware/Ankle_Sensor_V1.kicad_sch), [PCB](hardware/Ankle_Sensor_V1.kicad_pcb).
- [PDF schematu z KiCad](reports/Ankle_Sensor_V1_A1_schematic.pdf).
- [Roboczy STEP](reports/Ankle_Sensor_V1_A1_mechanical_review.step) i [render z KiCad](reports/Ankle_Sensor_V1_A1_3d_review.png).
- [BOM z numerami JLCPCB](manufacturing/review/assembly/BOM_REVIEW_NOT_RELEASED.csv), [CPL/Pick and Place](manufacturing/review/assembly/CPL_REVIEW_ROTATIONS_UNCONFIRMED.csv), [pinmapa](reports/pinmap.csv).
- [Gerber i Drill — ZIP do przeglądu](manufacturing/review/Ankle_Sensor_V1_A1_GERBERS_DRILL_REVIEW.zip), [manifest eksportu](manufacturing/review/export_manifest.json), [instrukcja eksportów](manufacturing/review/README.txt).

Footprinty, symbole i dostępne modele 3D są lokalne. STEP służy przeglądowi: **brakuje modelu USB-C**, moduł Raytac ma model ogólny, a pamięć ma jawny model gabarytowy 8,10 × 6,10 × 0,80 mm, wyprowadzony z maksymalnych wymiarów dokumentacji. Nie używać go jako kompletnej geometrii do finalnego dopasowania obudowy. Szczegóły: [przegląd modeli](docs/mechanical_model_review.md).

## Wykonane kontrole i zmiany

Aktualny zestaw to MDBT50Q-P1MV2, LSM6DSV32XTR, **W25Q01JVZEIQ 128 MiB**, BQ25185DLHR i TPS7A2030PDBVR 3,0 V. Zwiększenie pamięci zachowuje korpus 8 × 6 mm. Sterownik wymaga obsługi obu matryc. Konserwatywny budżet 16 B/próbkę i 95% dostępnej pamięci daje około 69 min przy 1920 Hz lub 138 min przy 960 Hz na każdą nogę.

Schemat został odczytany i wyeksportowany przez KiCad. ERC ma 0 błędów i 2 widoczne ostrzeżenia o celowym uziemieniu nieużywanych pinów 2/3 IMU, zgodnie z opisanym trybem producenta. Nie wyłączono globalnie tej kontroli. Zgodność schemat–PCB sprawdza natywny DRC z opcją `--schematic-parity`.

Przegląd geometrii po routingu wykrył zbyt długą LF_XL2. Obrócono niepolaryzowany kwarc i skrócono oba połączenia zegara do około 5 mm łącznie z gałęziami do kondensatorów, bez przelotek. Kontrole powtórzono po tej zmianie. BOM i natywny CPL mają zgodne zbiory **59 części montowanych na TOP**; pola testowe i SWD nie są częściami do montażu. CPL zachowuje rotacje KiCad — nie zastosowano niezweryfikowanych korekcji orientacji JLCPCB.

Przydzielono footprinty i konkretne MPN części UI, złącza baterii oraz pasywów. Kondensatory wejściowe ładowarki zmieniono na 2,2 µF/25 V; dodano 1 kΩ ograniczający rozładowanie kondensatora przycisku. Rozmieszczenie zasilania skraca lokalne połączenia do około 1,3–1,6 mm. Przelotki termiczne ładowarki leżą poza EP; nie zakłada się nieuzgodnionego procesu via-in-pad. Keepout anteny przedłużono do krawędzi. Natywna kontrola zapisanych wypełnień potwierdza 0 mm² miedzi w zabronionym obszarze.

Po odsunięciu przelotki masy od pada C3 sprawdzono otwory wszystkich 160 przelotek względem 255 padów SMD i 243 apertur pasty, także dla tej samej sieci. Brak nominalnych przecięć; najmniejszy odstęp 0,090 mm pozostaje do DFM z tolerancją wykonania. Współrzędne eksportu porównano z natywnym PCB: 59 pozycji, 160 otworów via, 4 sloty metalizowane i 2 otwory NPTH. To nie zastępuje niezależnego przeglądu CAM ani kontroli przesunięć i rotacji JLCPCB.

Sprawdzono również rzeczywiste lokalne drogi odsprzęgania przez wylewki. Dla Flash samo wspólne pole +3V0 ukrywało długi objazd do C15/C16. Dodany mostek +3V0 na B.Cu między istniejącymi przelotkami skraca połączenie VCC–C15 do około 2,47 mm w XY; lokalna droga do C16 także została potwierdzona. Nie zmieniono tras sygnałów ani footprintów. Dane: [przegląd zasilania](reports/power_routing_review.json).

## Pozostałe warunki

Przed zamówieniem sprawdzić stackup JLCPCB 1,0 mm i geometrię całego toru USB, schemat referencyjny Raytac §8.3, rysunek mechaniczny aktualnej dostawy USB-C, land-pattern kwarcu i minimalną efektywną pojemność krytycznych MLCC. **Nie potwierdzono impedancji 90 Ω ani zgodności USB.** Natywny plik Gerber Job zawiera automatyczny, ogólny stos KiCad; nie jest wybranym stackupem JLCPCB. Konieczne są niezależny przegląd CAM, panelizacja z fiducjalami, kontrola rotacji i DFM w podglądzie JLCPCB oraz potwierdzenie zaopatrzenia. Katalogowy numer C nie oznacza rezerwacji części.

Akumulator jest oddzielnym zespołem: chroniony LiPo 1S 4,2 V, preferowane 300 mAh, NTC fizycznie na ogniwie. Wiązka JST: 1 PACK+, 2 NTC, 3 PACK−; nie zakładać zgodności gotowych przewodów handlowych. Dla 500 mAh limit wejścia 100 mA i timer 360 min nie gwarantują pełnego ładowania. Nie wdrożono szybkiego ładowania ani automatycznej detekcji prądu źródła.

Sprzętowe okno temperatury U7/U8/Q1/Q2 uzupełnia TS ładowarki. Pobiera na baterii około 138 µA według obliczeń. Pakiet i NTC, rozruch, zapady napięcia, termika, USB-suspend oraz integralność zapisu wymagają prób fizycznych. Nie ma gotowego firmware; wymagania jego implementacji opisano osobno. [Lista kontroli](docs/release_checklist.md) określa warunki zamknięcia projektu.

## Dokumentacja i odtwarzanie

[Architektura](docs/architecture.md), [IMU/RF](docs/imu_rf_review.md), [zasilanie](docs/power_review.md), [dobór UI](docs/ui_battery_selection.md), [rozmieszczenie zasilania](docs/power_placement_review.md), [pamięć](docs/memory_upgrade.md), [pasywa](docs/passives_sourcing.md), [wymagania firmware](docs/firmware_contract.md).

`sh scripts/kicad_cli.sh` uruchamia KiCad z ustawieniami i cache w `.work`, bez modyfikowania profilu użytkownika. **Natywne pliki w `hardware/` są stanem przekazywanego projektu**. `build_design.py` nadpisuje wygenerowane schematy i manifest; `build_pcb.py --replace` odtwarza rozmieszczenie i usuwa routing — używać wyłącznie po zapisaniu checkpointu. Jawne wyjścia i pętle zasilania tworzy `fanout_pcb.py`. Narzędzia routingu i scalania nie zastępują przeglądu projektanta. `export_manufacturing_review.py` eksportuje rzeczywiste pliki z aktualnego PCB i odmawia pracy przy nieaktualnych hashach lub niezamkniętym DRC. Nie zwalnia projektu do produkcji. Archiwum A0 zachowano jako wcześniejszy stan.
