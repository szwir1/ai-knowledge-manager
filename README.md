# AI Knowledge Manager

Projekt rozwijany w ramach nauki Python Backend + AI.

## Cel projektu

Aplikacja do przechowywania notatek i dokumentów, która docelowo będzie
wykorzystywać AI do ich streszczania i przeszukiwania.

## Wymagania

- Python 3.14 lub nowszy

Projekt korzysta wyłącznie ze standardowej biblioteki Pythona.

## Uruchomienie

Nową notatkę można utworzyć poleceniem:

```powershell
python -m src.main add --title "Pomysł" --content "Treść notatki" --author "Jan"
```

Zapisane notatki można wyświetlić poleceniem:

```powershell
python -m src.main list
```

Notatki są domyślnie przechowywane w pliku `data/notes.json`. Inną lokalizację
można wskazać globalną opcją `--storage`, umieszczoną przed nazwą polecenia:

```powershell
python -m src.main --storage C:\temp\notes.json list
```

## Testy

```powershell
python -m unittest discover -s tests -v
```
