# A1 — przekazanie aktualnej wersji do GitHub

W czasie tej weryfikacji lokalny HEAD i lokalny cache origin/master miały identyfikator `28d88f22a6a9c0c0e1feb639546009518a6b5f8e`. Pliki poprzedniego audytu20dd2667 były w nim zgodne, ale zapisano je pod inną tożsamością commita. Dawny `reports/commit_delivery.json` jest odtąd jawnie historyczny.

Nie potwierdzono aktualnej zawartości serwera: shell nie rozwiązuje DNS GitHub, a publiczna przeglądarka udostępniła historyczny widok i nie potwierdziła stron konkretnych commitów. [Wynik próby](../reports/github_verification_final_A1.json). **Nie wykonano push.** Nie mylić lokalnego `origin/master` z aktualną odpowiedzią serwera.

Główny `.git` jest chroniony przed zapisem w tej sesji. Rzeczywisty nowy commit powstaje w odrębnym repozytorium na bazie28d88f2 i jest dostarczany jako `reports/ASV1_A1_FINAL_2026-10-29.bundle`. Jego pełny SHA, hash bundle i wynik niezależnego importu znajdują się w `reports/final_commit_delivery_A1.json`. Te dwa pliki powstają po commicie, więc nie są rekurencyjnie jego zawartością ani częścią własnego ZIP. Źródła i eksporty w katalogu roboczym są już aktualne.

## Import bez zastępowania plików roboczych

W zwykłym Terminalu, z katalogu tego repozytorium:

```sh
git bundle verify reports/ASV1_A1_FINAL_2026-10-29.bundle
git fetch reports/ASV1_A1_FINAL_2026-10-29.bundle final/a1-prototype-2026-10-29:refs/heads/final/a1-prototype-2026-10-29
git show --stat final/a1-prototype-2026-10-29
```

Fetch tworzy gałąź; nie robi checkoutu ani resetu i nie nadpisuje plików. Wymagany rodzic28d88f2 już istnieje w tym repozytorium. Nie wykonywać destrukcyjnego resetu w celu „wyczyszczenia” aktualnych plików.

## Wysłanie gałęzi do przeglądu i sprawdzenie serwera

Po obejrzeniu commita i własnej decyzji o wysłaniu:

```sh
git push origin final/a1-prototype-2026-10-29
ASV1_FINAL_COMMIT=$(python3 -c 'import json; print(json.load(open("reports/final_commit_delivery_A1.json"))["commit"])')
python3 scripts/verify_github_A1.py --branch final/a1-prototype-2026-10-29 --expected-commit "$ASV1_FINAL_COMMIT"
```

Push dotyczy gałęzi do przeglądu, nie zmienia automatycznie master. Repozytorium GitHub musi wskazywać tę gałąź jako wersję ocenianą; po akceptacji można ją scalić własnym zwykłym workflow. Przy scaleniu z nowym SHA należy weryfikować rzeczywisty commit serwera i ten sam manifest plików.

Weryfikator niczego nie wysyła. Odczytuje reklamowany ref, pobiera go do tymczasowego repozytorium, sprawdza pełny SHA oraz `current_A1_manifest.json` i wszystkie wskazane w nim hashe źródeł/eksportów. `PASS` oznacza zgodność odczytanego commita i plików w danym momencie. Błąd DNS, brak gałęzi lub rozbieżność daje wynik negatywny/niezweryfikowany, a nie deklarację synchronizacji. Wynik zapisuje się w `reports/github_verification_after_import.json`.
