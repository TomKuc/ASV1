# Statyczna kontrola schematu i manifestu

Status: **STATIC_CHECKS_PASS**

**To nie jest ERC ani DRC KiCad. Nie stanowi zwolnienia do produkcji.**

Sprawdzono jedynie zgodność parsowanego schematu z manifestem oraz ograniczony model połączeń.

Ten skrypt nie uruchamia ERC/DRC. Rzeczywiste raporty KiCad są zapisane osobno w katalogu reports.

- schematic_components: 72
- connected_pins_checked: 223
- nc_pins_checked: 32
- wires: 223
- labels: 223
- manifest_components: 72
- sheets: 6
- nets: 44
- uuids: 839
- errors: 0

## Wykryte problemy

Brak rozbieżności w objętym zakresem modelu statycznym. Wymagane otwarcie i ERC w KiCad.

BOM `bom_from_design.csv` pochodzi wyłącznie z manifestu. Nie potwierdza dostępności części ani montażu PCBA.
