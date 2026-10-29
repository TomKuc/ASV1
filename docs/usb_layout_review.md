# USB i drogi powrotne — przegląd rzeczywistego routingu

Odczyt z 29.10.2026 po scaleniu poprawek root, domyślnej blokady ładowania R24 i lokalnego przesunięcia U6/R25: `hardware/Ankle_Sensor_V1.kicad_pcb`, SHA-256 `38545441d19c70f355dd06a2539d2aa0937b113d92569c9b4798a1a04e08c45b`. Przegląd był wyłącznie odczytem; nie zmieniał PCB ani wypełnień. Natywny KiCad 10.0.7 sprawdził zapisane wypełnienie In1.Cu przez `Contains`, `BooleanIntersection` i `BooleanSubtract` oraz geometrię rzeczywistych ścieżek. Dane i lokalizacje wszystkich ubytków są w [return_path_review.json](../reports/return_path_review.json); metoda jest odtwarzalna skryptem [review_return_paths.py](../scripts/review_return_paths.py).

Warstwa In1.Cu ma jedno zapisane wypełnienie GND o powierzchni 1352,639 mm². Wszystkie 59 padów GND należy do jednej natywnej składowej połączeń. Wypełnienie zawiera antypady; liczba obrysów nie oznacza braku otworów w płaszczyźnie.

Pod badanymi osiami USB, IMU i QSPI każda próbka bez GND nadal znajduje się w promieniu 0,42 mm od własnej przelotki sygnałowej. Nie wykryto nowych przerw pod długimi prostymi trunkami poza okolicami ich przejść warstwowych. Dla USB MCU największa suma połączonych odcinków bez GND przy pojedynczym przejściu wynosi około 0,856 mm. Dla nowego USB_DP_CONN wynosi 1,433 mm przy via (65,25; 96,10), ale obwiednia tych odcinków ma przekątną tylko 0,763 mm: ścieżka lokalnie zakręca w obszarze antypada. Dla rozgałęzionego QSPI_IO3 suma wynosi 1,239 mm. Te sumy długości po różnych warstwach i gałęziach nie oznaczają szczeliny w płaszczyźnie o takiej szerokości. Nie potwierdzają też ciągłości najbliższej referencji B.Cu — ten przypadek opisano poniżej.

| Sieć USB | Długość ścieżek [mm] | Warstwy i długości [mm] | Via | Rzut miedzi nad In1 GND |
|---|---:|---|---:|---:|
| USB_DP: MCU–U6 | 31,232 | F 1,476; In2 29,756 | 2 | 94,777% |
| USB_DN: MCU–U6 | 32,957 | F 8,010; In2 24,948 | 2 | 95,020% |
| USB_DP_CONN: U6–USB-C | 12,997 | F 7,803; In2 5,194 | 2 | 83,998% |
| USB_DN_CONN: U6–USB-C | 15,552 | F 7,423; In2 8,129 | 2 | 89,788% |

Zachowano część wspólnego trunku MCU na In2.Cu do y=86,8 mm, z szerokością 0,15 mm i nominalnym odstępem 0,15 mm. Nowe końcówki do U6 są prowadzone osobno; deklaracja stałego sprzężenia nie obejmuje całej drogi. Każda sieć MCU ma dwa via 0,50/0,25 mm. Aktualna różnica sum długości MCU wynosi 1,725716 mm. Stare wartości 35,670/36,136 mm i różnica 0,466226 mm dotyczą wcześniejszego położenia U6. W JSON są wyłącznie jako jawne dane historyczne, bez warunku zgodności z aktualną płytką.

Natywne przecięcie rzutu pełnej szerokości USB_DP ujawniło ponadto dwa małe ubytki jego krawędzi poza przyjętym promieniem 0,42 mm własnej przelotki: łącznie 0,000155 mm², w okolicy `(69,74; 64,85)` i `(69,80; 64,73)` mm. Ich obwiednie mają najwyżej około 0,018 mm. Sąsiednie antypady zawężają tam miedź GND. Oś ścieżki poza własnym obszarem via nadal leży nad GND; wynik nie uzasadnia określenia całej szerokości ścieżek jako pokrytej masą w 100%.

Dla całego toru MCU–U6–USB-C suma długości ścieżek wynosi DP **44,228143 mm**, DN **48,509342 mm**: różnica **4,281199 mm**. Obie linie mają teraz po **4 via**. Są to sumy fizycznych odcinków danej sieci, także odgałęzień do obu pinów USB-C. Nie są wyznaczeniem różnicy opóźnienia propagacji w rozgałęzionym torze. Pomijają beczki via, wnętrze U6 i modułu oraz styki złącza. Geometria złączowa pozostaje niezakwalifikowana jako para o kontrolowanej impedancji. Aktualne pomiary są w [usb_routing_review.json](../reports/usb_routing_review.json); dawna propozycja MCU ma osobne pole `historical_mcu_proposal`.

Dla sześciu sieci IMU pokrycie rzutu pełnej szerokości ścieżek przez In1 GND wynosi 85,65–94,36%; dla siedmiu sieci QSPI/FLASH_CS 59,51–100%. Wszystkie wykryte próbki osi bez GND nadal mieszczą się przy własnych via. Niski wynik 59,51% dla krótkiego QSPI_SCK wynika głównie z jego dwóch przejść warstwowych: około 1,644 mm z 3,923 mm trasy leży w ich lokalnych antypadach. Odcinek QSPI_CLK_FLASH za rezystorem szeregowym, 14,529 mm na F.Cu, ma pełne pokrycie rzutu GND w granicy dokładności operacji geometrycznych. QSPI_IO0 także nie ma wykrytej przerwy osi nad In1.

Istotne ograniczenie dotyczy warstwy B.Cu. Układ warstw to F.Cu / In1 GND / In2 zasilanie i sygnały / B.Cu. Najbliższą warstwą odniesienia dla B.Cu jest więc mieszana In2.Cu. Sam rzut dalszej In1 GND nie potwierdza jednorodnej drogi prądu powrotnego. Natywna analiza zapisanego wypełnienia +3V0 wykazała następujące odcinki B.Cu bez tego wypełnienia bezpośrednio pod osią:

| Sieć na B.Cu | Najdłuższy taki odcinek [mm] | Obwiednia XY [mm] |
|---|---:|---|
| IMU_MISO | 5,885 | (61,450; 66,073) – (65,527; 70,270) |
| IMU_INT2 | 2,647 | (68,100; 63,070) – (69,850; 64,687) |
| FLASH_CS_N | 2,212 | (70,524; 64,824) – (71,274; 66,724) |

Pod tymi odcinkami występuje dalsza In1 GND. Przegląd nie symuluje rozkładu pól ani przechodzenia prądu powrotnego pomiędzy +3V0 i GND przez odsprzęganie, więc nie potwierdza jakości sygnałowej tych przejść odniesienia. Nie stwierdza też na tej podstawie awarii interfejsu.

Próbkowanie osi ma krok najwyżej 0,01 mm; granice pojedynczego przedziału są przybliżone z taką rozdzielczością. Natywne rzuty ścieżek mają błąd aproksymacji łuków 0,001 mm. Dodatkowy pas badania o szerokości 0,50 mm jest powtarzalną sondą geometryczną, a nie obliczoną szerokością prądu powrotnego. W PCB zapisano grubość całkowitą 1,0 mm, bez jawnego stackupu dielektryków, ich grubości i Er.

**Impedancja 90 Ω, jakość oka USB i integralność SPI/QSPI pozostają niezakwalifikowane.** Przed zatwierdzeniem tych torów trzeba ustalić rzeczywisty stackup JLCPCB i na nim ocenić pełną geometrię USB, przejścia referencji B.Cu oraz przebiegi na prototypie przy docelowych częstotliwościach. Pomiary powinny objąć USB w całym torze i bezbłędny transfer oraz zapis/odczyt SPI/QSPI z kontrolą integralności. Natywne DRC, łączność i zgodność ze schematem nie zastępują tej kwalifikacji.
