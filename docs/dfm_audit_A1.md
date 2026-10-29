# A1 — odstępy przelotek, maska i pasta, 2026-10-29

## Wniosek dla punktu0.090mm

Pomiar bazowego PCB potwierdził nominalny odstęp **0.090001mm** od krawędzi otworu via QSPI_IO3 `(71.85,73.9)` do pada U5.7 i jego apertury pasty. Nie było nominalnego przecięcia ani wykazanego zwarcia. Była mała rezerwa na tolerancję procesu; nie utożsamiono jej z limitem0.09mm dotyczącym innych struktur, np. ścieżek w capabilities fabryki.

Zamiast deklarować zgodność bez akceptacji wykonawcy przesunięto istniejące via do **`(71.85,73.76)`**. Zachowano średnicę0.50mm, otwór0.25mm, tenting obu stron i ten sam net. Zmieniono jedynie przyłączone końce dwóch istniejących ścieżek. Nowy nominalny odstęp otwór–Cu/pasta wynosi **0.230001mm**. Pad i paste U5 nie były zmieniane; nie zmieniono wybranego W25Q01JVZEIQ.

W globalnym odczycie znaleziono analogicznie ciasną lokalizację VBUS przy J1.A9/B4:0.105001mm. Via `(66.45,94.0)` odsunięto do `(66.45,93.93)`, uzyskując0.175001mm. Nie zmieniono padów złącza. Warianty powodujące naruszenie odstępu do R1/GND zostały odrzucone na kopii projektu; ich nie przyjęto.

## Zestawienie

| Lokalizacja | Bazowa geometria | Przyjęta geometria | Decyzja |
|---|---|---|---|
| U5.7 / QSPI_IO3 | hole→SMD/paste0.090001mm | 0.230001mm | Lokalne odsunięcie istniejącej przelotki; ryzyko ograniczono, brak obietnicy tolerancji niepodanej przez fabrykę. |
| J1.A9/B4 / VBUS | 0.105001mm | 0.175001mm | Analogiczna lokalna korekta. |
| C4/C5 GND | 0.150001mm | Bez zmiany | Pozostaje do zatwierdzenia maski i rejestracji w DFM. |

Finalnie sprawdzono164 vias:0 przecięć Cu/pasty, minimum0.150001mm przy U6.2 (oraz równoważne wcześniejsze miejsca C4/C5). Nie zwiększono średnic ani nie zastosowano via-in-pad.

Wynik globalny po wszystkich końcowych zmianach, w tym przyjętym lokalnym wariancie USB, należy czytać w `reports/via_pad_audit.json`. Audytor `scripts/audit_vias.py` bada rzeczywiste zaokrąglone kształty Cu i apertur pasty na obu stronach, także dla tej samej sieci, bo zwykły DRC może takie zbliżenie dopuścić. Zawiera dodatnią kontrolę starej kolizji C3 oraz test aktualnego odsunięcia. Nie obejmuje tolerancji wykonania ani rozpływu pasty w reflow.

## Co wynika z JLCPCB

[Capabilities JLCPCB](https://jlcpcb.com/capabilities/Capabilities) podają tolerancję pozycji otworu±0.075mm. Dla bazowego0.090mm sama ta wielkość pozostawiała jedynie0.015mm rezerwy w uproszczonym przesunięciu w stronę pada. Nie jest to pełna analiza najgorszego przypadku; producent osobno opisuje tolerancje padów PTH i nie przypisuje im automatycznie tolerancji otworów vias.

[JLC — solder mask](https://jlcpcb.com/blog/basic-design-of-solder-mask) opisuje multilayer LDI z otwarciami1:1 i dokładnością±0.02mm. To warunki procesu do uzgodnienia z wykonawcą, bez dodawania tej wartości do CAD jako potwierdzonej gwarancji każdego otworu. U5 ma w tym projekcie zerowy dodatkowy margines maski; dla padów sygnałowych apertura pasty odpowiada ich nominalnej geometrii. Tenting nie jest wypełnieniem ani zakorkowaniem otworu.

[JLC — via covering](https://jlcpcb.com/help/article/pcb-via-covering) rozróżnia tenting, ink plugging i epoxy/copper-filled-and-capped. Warunku0.35mm dla ink plugging nie zastosowano jako uniwersalnej reguły tentingu. Nie zamówiono procesu via-in-pad. Nie zastosowano tolerancji gotowego PTH `+0.13/−0.08mm` jako udowodnionej tolerancji via.

## Warunki do przeglądu produkcyjnego

- Sprawdzić rzeczywiste Gerbery maski/pasty i Excellon po ostatnim eksporcie, bez automatycznego powiększenia maski zmieniającego projekt.
- Uzyskać akceptację aktualnych zbliżeń przez JLCPCB; preferować zieloną maskę i rozważyć ENIG dla płaskości montażu LGA/WSON. Dokładny proces i wycena nie zostały wybrane/zamówione.
- Potwierdzić szablon, reflow, MSL i X-ray dla LSM6DSV32XTR. Katalog JLC wskazuje Standard Only i wymagane X-ray dla C22461202.
- Nominalne odstępy i wynik0 DRC nie zastępują oceny procesu, rejestracji maski i lutowania. Zmiany ograniczają ryzyko; nie stanowią pełnego zwolnienia produkcyjnego.
