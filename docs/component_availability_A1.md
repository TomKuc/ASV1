# A1 — dokładne części i dostępność montażu, 29.10.2026

Sprawdzono publiczne karty katalogowe JLCPCB. To identyfikacja części i ograniczeń usługi, nie oferta, bieżąca rezerwacja magazynowa ani akceptacja BOM/PCBA. Liczby magazynowe z indeksu wyszukiwarki mogą być opóźnione; nie przyjęto ich jako gwarancji realizacji.

| Ref | Dokładny MPN / numer JLC | Ustalenie i decyzja |
|---|---|---|
| U5 | [W25Q01JVZEIQ / C5137036](https://jlcpcb.com/partdetail/WinbondElec-W25Q01JVZEIQ/C5137036) | Publiczna karta: WSON-8-EP 8×6 mm, 1 Gbit, 2.7–3.6 V, MSL3, SMT Economic/Standard. Zachowano128MiB. Nie mylić z W25Q512 ani wariantem1.8V. |
| U4 | [LSM6DSV32XTR / C22461202](https://jlcpcb.com/partdetail/STMicroelectronics-LSM6DSV32XTR/C22461202) | Karta: LGA14 2.5×3mm, **Standard Only**, MSL3, **X-ray required**. To narzuca wybór usługi PCBA i kontrolę montażu, nawet jeżeli inne części dopuszczają Economic. |
| U3 | [MDBT50Q-P1MV2 / C5119772](https://jlcpcb.com/partdetail/RAYTAC-MDBT50QP1MV2/C5119772) | Istnieje dokładny identyfikator katalogowy wariantu z anteną PCB. Nie potwierdzono rezerwacji ani terminu dostawy. Nie zastępować automatycznie wersją z anteną chipową lub modułem o podobnej nazwie. |
| U1 | [BQ25185DLHR / C19725033](https://jlcpcb.com/partdetail/TEXASINSTRUMENTS-BQ25185DLHR/C19725033) | Dokładny układ i obudowa pozostają. Dostępność do konkretnego zlecenia niepotwierdzona. Zbiorczy atrybut karty handlowej nie zastępuje programowania R1/R2 ani datasheet TI. |
| U2 | [TPS7A2030PDBVR / C963429](https://jlcpcb.com/partdetail/TexasInstruments-TPS7A2030PDBVR/C963429) | Wybrany dotychczasowy LDO3.0V, 300mA pozostaje; nie zmieniano na TPS7A02. Minimalne Ceff/ESR, prąd i termika wymagają zamknięcia wg TI oraz docelowego obciążenia. |

Aktualny [BOM](../manufacturing/review/assembly/BOM_REVIEW_NOT_RELEASED.csv) ma33 grupy i59 montowanych elementów. Pinmapa i schemat określają obwód; pozycje/rotacje w CPL pochodzą z KiCad. Nie zatwierdzono jeszcze translacji bibliotek montażowych JLC, pin1, polaryzacji ani zamienników. Numery pasywów i UI są opisane również w `passives_sourcing.md` i `ui_battery_selection.md`.

Przed zamówieniem wykonać pełny import BOM/CPL do Standard PCBA, uzyskać potwierdzenie dokładnych MPN, ilości, MSL/reflow/X-ray oraz podglądu montażu. Nie składano zamówienia ani nie kontaktowano się z dostawcą w imieniu użytkownika.

Akumulator nie jest pozycją SMT: wymagany oddzielnie dobrany i chroniony LiPo1S4.2V z NTC fizycznie na ogniwie. Nadal brak kwalifikowanego MPN pakietu/wiązki/NTC. Nie przyjęto, że dowolne złącze3-pin ma zgodną kolejność PACK+/NTC/PACK−.
