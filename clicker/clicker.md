# Minimalistická Clicker Hra

Toto je naprosto základní verze "Clicker" hry vytvořená v Pythonu pomocí knihovny `pygame`. Cílem bylo napsat hru na co nejméně řádků kódu.

## Co kód dělá?
1. **Příprava okna**: Vytvoří herní okno o velikosti 400x400 pixelů a připraví font pro vykreslování textu.
2. **Definice objektů**: 
   - Proměnná `score` uchovává aktuální počet bodů.
   - Objekt `cube` typu `pygame.Rect` definuje modrou kostku (čtverec) uprostřed obrazovky.
3. **Herní smyčka (`while True`)**:
   - Neustále kontroluje události.
   - Pokud kliknete na křížek, hra se zavře.
   - Pokud kliknete levým tlačítkem myši (`event.button == 1`) a kurzor se zrovna nachází uvnitř kostky (`cube.collidepoint(event.pos)`), přičte se bod ke skóre.
4. **Vykreslování**:
   - Vymaže obrazovku tmavou barvou, aby nezůstávaly stopy z předchozího snímku.
   - Vykreslí modrou kostku.
   - Vypíše aktuální skóre do levého horního rohu.
   - Aktualizuje obraz (`pygame.display.flip()`).

## Jak spustit
Otevřete terminál a spusťte kód pomocí vašeho Python prostředí:
```powershell
.venv\Scripts\python.exe clicker/clicker.py
```
