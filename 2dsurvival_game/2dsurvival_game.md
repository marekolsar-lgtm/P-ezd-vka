# 2D Survival Game - Dokumentace

## Přehled hry

**2D Survival Game** je 2D akční survival hra vytvořená v Pythonu s využitím knihovny Pygame. Hra nabízí top-down pohled na procedurálně generovaný dungeon, kde hráč musí přežít vlny nepřátel, sbírat předměty a bojovat o co nejvyšší skóre.

## Hlavní mechaniky

### Pohyb a ovládání
- **Pohyb**: Použijte klávesy `WASD` nebo šipky pro pohyb ve všech směrech
- **Útok**: Klávesa `E` pro útok mečem
- **Fullscreen**: Klávesa `F` pro přepínání mezi okenním a fullscreen režimem
- **Ukončení**: `ESC` pro ukončení hry

### Hráč
- **Zdraví**: Maximálně 5 životů
- **Rychlost**: 5 pixelů za snímek
- **Útok**: Meč s dosahem a cooldown systémem
- **Inventář**: Klíče pro potenciální budoucí mechaniky

### Nepřátelé

Hra obsahuje tři typy nepřátel s různými vlastnostmi:

#### 1. Walker (Chodec) - Červený
- **Zdraví**: 3 životy
- **Chování**: Pronásleduje hráče přímočaře
- **Rychlost**: 2 pixely za snímek
- **Vzhled**: Červený čtverec s očima

#### 2. Flying (Létající) - Fialový
- **Zdraví**: 2 životy
- **Chování**: Rychle se pohybuje směrem k hráči
- **Rychlost**: 1 pixel za snímek (rychlejší reakce)
- **Vzhled**: Fialový s křídly

#### 3. Shooter (Střelec) - Oranžový
- **Zdraví**: 4 životy
- **Chování**: Pohybuje se pomalu a střílí projektily na hráče
- **Rychlost**: 0.5 pixelu za snímek
- **Vzhled**: Oranžový s hlaveňí

### Předměty

#### Health Potion (Léčivý lektvar) - Červený kříž
- **Efekt**: Obnoví 2 životy
- **Spawn**: Náhodně v dungeonu

#### Damage Boost (Posílení útoku) - Žlutý meč
- **Efekt**: Zvětší poškození na 2x po dobu 5 sekund
- **Spawn**: Náhodně v dungeonu

#### Key (Klíč) - Oranžový klíč
- **Efekt**: Přidá klíč do inventáře (pro budoucí mechaniky)
- **Spawn**: Náhodně v dungeonu

## Herní svět

### Dungeon generování
- **Velikost**: 5x5 místností
- **Místnosti**: Velikost 5-10 bloků (160-320 pixelů)
- **Bloky**: 32x32 pixely
- **Materiály**:
  - Dirt (Hlína) - Hnědá s kamínky
  - Stone (Kámen) - Šedá s texturou
  - Grass (Tráva) - Zelená s trávou nahoře

### Kamera
- **Deadzone**: 120x90 pixelů kolem hráče
- **Smooth following**: Kamera se pohybuje plynule za hráčem
- **Hranice**: Omezena velikostí dungeonu

## Herní mechaniky

### Wave systém
- **Spawn interval**: Začíná na 120 snímků (2 sekundy), zrychluje se časem
- **Počet nepřátel**: Základ 3, zvyšuje se o 1 za vlnu (max 10)
- **Spawn radius**: Minimálně 200 pixelů od hráče
- **Rozložení**: 60% walker, 30% flying, 10% shooter

### Kolize a poškození
- **Hráč vs Nepřítel**: Kontakt způsobí poškození a odražení
- **Útok**: Meč zasáhne nepřátele v dosahu
- **Projektily**: Střely od shooter nepřátel
- **Imunita**: 30 snímků po zásahu

### Skórovací systém
- **Za zabití nepřítele**: +10 bodů
- **Žádný trest za smrt**: Hra se restartuje s novým dungeonem

## Technické detaily

### Grafika a animace
- **Rozlišení**: 1024x768 pixelů
- **FPS**: 60 snímků za sekundu
- **Animace hráče**: Idle, walk, jump, attack
- **Textury**: Procedurálně generované bloky

### Audio
- **Aktuálně**: Žádný zvuk (pouze vizuální efekty)

### Kódová struktura
- **Hlavní třídy**:
  - `Player`: Hráč s animacemi a mechanikami
  - `Enemy`: Nepřátelé s různými typy
  - `Item`: Sbíratelné předměty
  - `Projectile`: Střely od shooter nepřátel
  - `Block`: Herní bloky s texturami
  - `Camera`: Kamera systém

### Konstanty
```python
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
BLOCK_SIZE = 32
PLAYER_MAX_HEALTH = 5
ENEMY_SPAWN_INTERVAL = 120
FPS = 60
```

## Instalace a spuštění

### Požadavky
- Python 3.x
- Pygame knihovna

### Instalace
```bash
pip install pygame
```

### Spuštění
```bash
python 2dsurvival_game.py
```

## Budoucí vylepšení

### Plánované funkce
- [ ] Zvukové efekty a hudba
- [ ] Více typů nepřátel
- [ ] Různé zbraně a vybavení
- [ ] Achievement systém
- [ ] Multiplayer mód
- [ ] Level editor
- [ ] Boss fights
- [ ] Upgrade systém pomocí klíčů

### Optimalizace
- [ ] Lepší kolizní detekce
- [ ] Chunk loading systém
- [ ] Particle efekty
- [ ] Smooth animace

## Autoři a verze

**Verze**: 1.0
**Vytvořeno**: 2024
**Jazyk**: Python s Pygame
**Platforma**: Windows, Linux, macOS

## Licence

Tento projekt je open-source a může být volně používán a upravován.
