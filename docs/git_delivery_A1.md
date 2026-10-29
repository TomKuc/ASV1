# Dostarczenie commita audytu A1

Główny katalog `.git` jest w tej sesji chroniony przed zapisem. Nie zmieniano jego historii i nie wykonano push do GitHub. Z tego powodu commit powstaje w osobnym, lokalnym repozytorium roboczym na bazie tego samego rodzica `c3536966d15fab3ada32515650615b947dce1349`.

Rzeczywisty identyfikator, hash i wynik sprawdzenia Git bundle znajdują się w `reports/commit_delivery.json`, dostarczanym po utworzeniu commita obok paczki ZIP. Sam bundle i ten plik nie należą do własnego commita ani archiwum projektu; unika to cyklicznej zależności jego identyfikatora. Zawartość commita obejmuje źródła, raporty i nowe archiwum audytu. `reports/audit_changed_files.txt` wymienia ścieżki w commicie.

Import w zwykłym Terminalu z katalogu tego repozytorium:

```sh
git bundle verify reports/ASV1_A1_AUDIT_2026-10-29.bundle
git fetch reports/ASV1_A1_AUDIT_2026-10-29.bundle audit/a1-2026-10-29:refs/heads/audit/a1-2026-10-29
git show --stat audit/a1-2026-10-29
```

`fetch` tworzy gałąź z commitem, bez przełączania gałęzi i bez zastępowania plików roboczych. Wymaga repozytorium zawierającego powyższy commit bazowy. Pliki projektu już są zmienione lokalnie; ich integrację z bieżącą gałęzią należy wykonać po obejrzeniu stanu `git status` i zachowaniu ewentualnych własnych zmian. Nie uruchamiano resetu, checkoutu nad zmianami ani wysyłania z tego środowiska.

Stare paczki A0/A1 oraz archiwum bazowego routingu pozostają zachowane. Nowa paczka nazywa się `Ankle_Sensor_V1_A1_AUDIT_REVIEW.zip` i ma status REVIEW.
