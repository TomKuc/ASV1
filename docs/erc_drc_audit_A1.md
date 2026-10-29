# ERC/DRC A1 — audyt profilu kontroli, 2026-10-29

Punkt odniesienia: commit `c353696` i `reports/baselines/A1_before_audit_manifest.json`. Oryginalny routing zachowano w archiwum obok manifestu. Pliki `*_before.json` opisują odczyt bazy z włączonymi kontrolami; aktualny wynik podają `reports/erc_current.json`, `reports/drc_final.json` i `reports/validation_status.json` z hashami.

## Co rzeczywiście było wyłączone

W bazowym `.kicad_pro` znaleziono pięć ignorowanych klas DRC i cztery ERC. Nie było indywidualnych wykluczeń (`drc_exclusions=[]`, `erc_exclusions=[]`). Nie przyjęto, że zastany profil oznacza indywidualne zatwierdzenie tych klas.

| Kontrola | Wynik audytu i decyzja |
|---|---|
| DRC `missing_courtyard` | Włączona jako warning. Nie zgłosiła braków; nadal wymagana jest ocena obrysów mechanicznych i tolerancji. |
| DRC `footprint_filters_mismatch` | Włączona. Brak zgłoszeń nie stanowi porównania wymiarów padów z dokumentacją producenta. |
| DRC `footprint_type_mismatch` | Włączona. Klasyfikację części i padów sprawdza natywny KiCad, także dla mieszanego USB-C. |
| DRC `track_not_centered_on_via` | Ujawniła11 ostrzeżeń. Końce miały przesunięcie0.070711mm względem środka połączonego via. Wykonano lokalne dopasowania końców, bez dodawania/usuwania tras. To poprawa geometrii połączenia, bez twierdzenia, że wcześniej była przerwa elektryczna. |
| DRC `tuning_profile_track_geometries` | Włączona. Projekt nie ma kwalifikowanego profilu strojenia. Wynik nie ustala impedancji USB ani dopuszczalnego skew. |
| ERC `footprint_filter` | Włączona. Brak dodatkowych zgłoszeń. |
| ERC `four_way_junction` | Włączona. Brak dodatkowych zgłoszeń połączeń czteroramiennych. |
| ERC `single_global_label` | Włączona. Brak dodatkowych pojedynczych etykiet globalnych. |
| ERC `simulation_model_issue` | Włączona. Nie uruchamiano SPICE ani nie zatwierdzono modeli symulacyjnych. |

**Po audycie żadna z tych klas nie pozostaje ignorowana.** Poziom warning zachowuje widoczność problemów. Kontrole zwarć, odstępów, reguł otworów, obrysu, zgodności schematu i łączności nadal mają swoje ustawione poziomy. Natywne raporty zapisują `ignored_checks`; należy sprawdzić je ponownie przy zmianie wersji KiCad.

## Dwa ostrzeżenia IMU

U4.2 `SDx_Qvar1` i U4.3 `SCx_Qvar2` mają w uniwersalnym symbolu typ dwukierunkowy, a w tej konfiguracji są podłączone do GND. ERC widzi ich połączenie z flagą zasilania masy `#FLG03` jako bidirectional–power_out.

[ST LSM6DSV32X, DS13511 Rev2, tabela2 i §7.1](https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf) dopuszcza takie połączenie w mode1 przy wyłączonych Qvar i analog hub. Firmware ma zachować te funkcje wyłączone. Nie zmieniono typu pinów ani nie wyciszono ostrzeżeń; uzasadnienie jest ograniczone do tej konfiguracji sprzętu. Włączenie alternatywnych funkcji tych pinów wymaga ponownej analizy.

## Co sprawdzono teraz

Wykonano rzeczywisty KiCad10.0.7: native ERC, DRC po refill/save z `--schematic-parity`, odczyt sieci schematu i padów PCB, statyczne porównanie manifestu i hierarchii. Lokalny dziennik zmian UUID: `reports/audit_geometry_changes_A1.json`, zmiana domyślnego ładowania: `reports/audit_charge_default_A1.json`.

Wynik0 DRC dotyczy zadeklarowanych reguł. Sam poziom `error` dla par różnicowych nie ustanawia brakujących wymagań geometrycznych. Nie wykonano elektrycznej symulacji oka USB, pól elektromagnetycznych, testu anteny, prób MEMS ani testów ładowania na urządzeniu. [KiCad — DRC](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#design-rule-checking).
