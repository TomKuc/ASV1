# A1 — dostarczenie zamknięcia warunków A01–A04

Aktualną decyzję określa [production_readiness_A1.md](production_readiness_A1.md), a pliki [manifest](../reports/current_A1_manifest.json). Bazą jest lokalny `b17f1457de876ecb27e94dc514c9a4844be44bc0`. Stary commit `ce616878…` nie został potwierdzony na GitHubie: publiczny URL 404, Git DNS failure. Nie wykonano push. Pliki starego commita poza `.gitignore` są identyczne z bazą b17f145; treść plików to odrębna kwestia od historii Git.

Główny `.git` jest tylko do odczytu w tej sesji. Nowy commit powstaje w `.work/prod_closure_git_20261029`, z rodzicem b17f145. Jest przenoszony przez **`reports/ASV1_A1_PRODUCTION_2026-10-29.bundle`**. Rzeczywisty SHA, hash bundle/ZIP oraz wynik niezależnego lokalnego importu znajdują się w **`reports/production_commit_delivery_A1.json`**. Bundle i ten rekord powstają po commicie i nie są rekurencyjnie jego zawartością ani zawartością własnej paczki.

W zwykłym Terminalu w repozytorium można zaimportować gałąź **bez checkoutu, resetu i nadpisywania plików**:

```sh
git bundle verify reports/ASV1_A1_PRODUCTION_2026-10-29.bundle
git fetch reports/ASV1_A1_PRODUCTION_2026-10-29.bundle production/a1-conditions-2026-10-29:refs/heads/production/a1-conditions-2026-10-29
git show --stat production/a1-conditions-2026-10-29
```

Wymagany rodzic b17f145 już jest w repozytorium. Po obejrzeniu gałęzi i własnej decyzji o wysłaniu:

```sh
git push origin production/a1-conditions-2026-10-29
ASV1_PRODUCTION_COMMIT=$(python3 -c 'import json; print(json.load(open("reports/production_commit_delivery_A1.json"))["commit"])')
python3 -B scripts/verify_github_A1.py --branch production/a1-conditions-2026-10-29 --expected-commit "$ASV1_PRODUCTION_COMMIT"
```

Weryfikator niczego nie wysyła ani nie zapisuje w głównym `.git`: sprawdza reklamowany ref, pobiera do temp i porównuje manifest oraz wszystkie jego pliki. Dopiero `PASS` dla rzeczywistego GitHub oznacza zgodność w danym momencie. Lokalny test importu bundle nie jest testem GitHub. Push gałęzi nie zmienia automatycznie master; merge z innym SHA wymaga weryfikacji rzeczywistego SHA i zgodności manifestu.
