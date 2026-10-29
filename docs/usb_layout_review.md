# USB i drogi powrotne — przegląd rzeczywistego routingu

Odczyt z 28.10.2026 po korektach LFXO, połączenia GND przy C3 i lokalnego zasilania Flash: `hardware/Ankle_Sensor_V1.kicad_pcb`, SHA-256 `b5487d09753bbf0490bf91bda6c803934609b778283ef87c044309bc1514f678`. Przegląd był wyłącznie odczytem; nie zmieniał PCB ani wypełnień. Natywny KiCad 10.0.7 sprawdził zapisane wypełnienie In1.Cu przez `Contains`, `BooleanIntersection` i `BooleanSubtract` oraz geometrię rzeczywistych ścieżek. Dane i lokalizacje wszystkich ubytków są w [return_path_review.json](../reports/return_path_review.json); metoda jest odtwarzalna skryptem [review_return_paths.py](../scripts/review_return_paths.py).

Warstwa In1.Cu ma jedno zapisane wypełnienie GND o powierzchni 1355,170 mm². Wszystkie 60 padów GND należy do jednej natywnej składowej połączeń. Wypełnienie zawiera antypady; liczba obrysów nie oznacza braku otworów w płaszczyźnie.

Pod badanymi osiami USB, IMU i QSPI nie znaleziono dodatkowych długich przerw w rzucie In1 poza okolicami własnych przelotek. Każda próbka osi bez GND znajdowała się w promieniu 0,42 mm od własnej przelotki sygnałowej. Najdłuższy połączony odcinek trasy bez GND przy przejściu między warstwami wynosił około 0,864 mm; dla USB MCU było to 0,856 mm. Są to lokalne ubytki przy antypadach, obejmujące ścieżki przed i za przelotką. Nie jest to dowód ciągłości najbliższej referencji dla ścieżek B.Cu — ten przypadek opisano poniżej.

| Sieć USB | Długość ścieżek [mm] | Warstwy i długości [mm] | Via | Rzut miedzi nad In1 GND |
|---|---:|---|---:|---:|
| USB_DP: MCU–U6 | 35,670 | F 2,716; In2 32,954 | 2 | 95,490% |
| USB_DN: MCU–U6 | 36,136 | F 2,325; In2 33,812 | 2 | 95,479% |
| USB_DP_CONN: U6–USB-C | 18,717 | F 18,717 | 0 | ≈100% |
| USB_DN_CONN: U6–USB-C | 20,563 | F 11,742; In2 8,821 | 2 | 91,706% |

Główny wspólny trunk MCU–U6 jest prowadzony na In2.Cu, z szerokością 0,15 mm i nominalnym odstępem 0,15 mm. Każda z tych dwóch sieci ma dwa via 0,50/0,25 mm i krótkie fanouty F.Cu. Różnica długości tej części wynosi 0,466226 mm. Fanouty i przejścia przez przelotki lokalnie rozchodzą się; całej długości nie należy traktować jako jednorodnej pary sprzężonej.

Natywne przecięcie rzutu pełnej szerokości USB_DP ujawniło ponadto dwa małe ubytki jego krawędzi poza przyjętym promieniem 0,42 mm własnej przelotki: łącznie 0,000155 mm², w okolicy `(69,74; 64,85)` i `(69,80; 64,73)` mm. Ich obwiednie mają najwyżej około 0,018 mm. Sąsiednie antypady zawężają tam miedź GND. Oś ścieżki poza własnym obszarem via nadal leży nad GND; wynik nie uzasadnia określenia całej szerokości ścieżek jako pokrytej masą w 100%.

Dla całej drogi MCU–U6–USB-C suma długości ścieżek wynosi DP **54,387098 mm**, DN **56,699291 mm**: różnica **2,312193 mm**. Liczba przelotek całego toru jest różna: DP **2**, DN **4**. Sumy pomijają beczki przelotek, połączenia wewnątrz U6 i modułu oraz styki złącza. Geometria od U6 do USB-C nie została zakwalifikowana jako para o kontrolowanej impedancji. Dane MCU skopiowano z uprzedniego raportu weryfikacji; zgadzają się z aktualną płytką. Trwała kopia pomiarów, przebieg wspólnej osi i ograniczenia znajdują się w [usb_routing_review.json](../reports/usb_routing_review.json), poza katalogiem roboczym `.work`.

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
