# Dokumentace: Kalkulačka (Python & Tkinter)

Tento projekt obsahuje jednoduchou grafickou kalkulačku vytvořenou v jazyce Python. Jako grafické rozhraní je využita standardní knihovna `tkinter`.

## Požadavky

- **Python 3.x**: Pro spuštění je vyžadován nainstalovaný Python.
- **Žádné externí balíčky**: Knihovna `tkinter` je součástí standardní instalace Pythonu, není tedy nutné nic stahovat přes `pip`.

## Spuštění

Aplikaci lze spustit standardně přes terminál příkazem:

```bash
python kalkulačka.py
```
Případně ji můžete spustit přímo ze svého oblíbeného editoru (např. VS Code).

## Přehled funkcí

- **Číselník (0-9)** pro zadávání hodnot.
- **Základní matematické operace**: Sčítání (`+`), odčítání (`-`), násobení (`*`) a dělení (`/`).
- **Tlačítko "C"**: Slouží pro smazání celého aktuálního vstupu a vynulování displeje.
- **Tlačítko "="**: Okamžitě vyhodnotí zadaný matematický výraz.

## Architektura a princip fungování

Hlavní logika výpočtu stojí na vestavěné funkci Pythonu `eval()`. 
Když uživatel kliká na tlačítka, znaky se spojují do jednoho dlouhého textového řetězce (proměnná `current_equation`). Ve chvíli, kdy uživatel klikne na rovná se (`=`), předá se tento řetězec funkci `eval()`, která ho vyhodnotí jako platný pythonový výraz.

```python
# Zjednodušená ukázka:
# Pokud current_equation obsahuje "5+5*2", 
# result bude vrácen jako "15"
result = str(eval(current_equation))
```

### Ošetření chyb

Program je chráněn proti pádům pomocí bloku `try...except`:
1. **`ZeroDivisionError`**: Zabrání pádu aplikace v případě, že se uživatel pokusí dělit nulou. Místo toho se na obrazovce objeví "Dělení nulou!".
2. **`Exception`**: Zachytí veškeré ostatní chyby (např. nevhodně seřazené operátory jako `++` nebo neplatné výrazy) a vypíše na displej "Chyba". V takovém případě se pak rozdělaný výpočet vynuluje.
