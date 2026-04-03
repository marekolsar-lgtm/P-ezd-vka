# 2D Survival Game - Dokumentace

## Přehled hry

**2D Survival Game** je 2D akční survival hra vytvořená v Pythonu s využitím knihovny Pygame. Hra nabízí top-down pohled na procedurálně generovaný dungeon, kde hráč musí přežít vlny nepřátel, sbírat předměty a bojovat o co nejvyšší skóre.

## Hlavní mechaniky

### Pohyb a ovládání
- **Pohyb**: Použijte klávesy `WASD` nebo šipky pro pohyb ve všech směrech
- **Útok**: Automatický u nejbližších nepřátel nebo ve směru myši (automatický sword swing)
- **Fullscreen**: Klávesa `F` pro přepínání mezi okenním a fullscreen režimem
- **Ukončení**: `ESC` pro ukončení hry

### Hráč
- **Zdraví**: Začíná na 100 životech (lze zvýšit v menu vylepšení)
- **Úroveň a XP**: Hráč sbírá XP orby z nepřátel; po naplnění lišty XP získá novou úroveň a vyskočí menu pro výběr 1 ze 3 vylepšení (např. Max Health, Damage, Speed, Heal, Cooldown).
- **Rychlost**: 5 pixelů za snímek
- **Útok**: Meč s dosahem a cooldown systémem
- **Inventář**: Klíče pro potenciální budoucí mechaniky

### Nepřátelé

Hra obsahuje pět typů nepřátel s různými vlastnostmi:

#### 1. Walker (Chodec) - Zelený Slime/Zombie
- **Zdraví**: 30 životů (Poškození: 15)
- **XP Hodnota**: 5 XP
- **Chování**: Pronásleduje hráče přímočaře
- **Rychlost**: 2 pixely za snímek
- **Vzhled**: Zelený čtverec s červenýma očima

#### 2. Flying (Létající) - Fialový Netopýr
- **Zdraví**: 20 životů (Poškození: 10)
- **XP Hodnota**: 5 XP
- **Chování**: Létá pomalu a pronásleduje hráče, nereaguje na knockback
- **Rychlost**: 1 pixel za snímek
- **Vzhled**: Fialový blok s křídly

#### 3. Tank (Golem) - Šedý
- **Zdraví**: 100 životů (Poškození: 30)
- **XP Hodnota**: 15 XP
- **Chování**: Pohybuje se pomaleji, má velkou výdrž a menší snížení po útoku (knockback)
- **Rychlost**: 1.2 pixelu za snímek
- **Vzhled**: Šedý kámen s oranžovýma očima

#### 4. Fast (Duch/Malé oko) - Průhledný
- **Zdraví**: 10 životů (Poškození: 5)
- **XP Hodnota**: 5 XP
- **Chování**: Rychle se přibližuje k hráči a velmi výrazně odskakuje při zásahu
- **Rychlost**: 3 pixely za snímek
- **Vzhled**: Částečně průhledný bílý/světle modrý kruh s okem

#### 5. Boss - Velký červený golem
- **Zdraví**: 500 životů (Poškození: 40) - roste s každou další vlnou
- **XP Hodnota**: 150 XP
- **Chování**: Větší obdoba tanka, spawnuje se na konci každé vlny za okrajem obrazovky. Nereaguje tolik na knockback.
- **Rychlost**: 1.6 pixelu za snímek (0.8 násobek základní rychlosti)
- **Vzhled**: Velký červený blok se žlutýma očima

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

#### XP Orb - Zelená zářící kulička
- **Efekt**: Přidá zkušenosti hráči pro postup na novou úroveň (samo se přitahuje z blízkosti)
- **Spawn**: Padá z mrtvých nepřátel

#### Money (Peníze) - Zlatá mince
- **Efekt**: Přičte peníze na konto hráči (samo se přitahuje z blízkosti)
- **Spawn**: 30% šance, že padne po zabití jakéhokoliv nepřítele společně s XP orbem

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
- **Spawn interval**: Začíná na 60 snímků (1 sekunda), zrychluje se časem
- **Počet nepřátel**: Základ 1, pomalu se zvyšuje každou vlnu (max 10 per tick)
- **Spawn radius**: Minimálně 300 pixelů od hráče, spawny probíhají těsně za hranicí kamery
- **Druhy nepřátel**: Mění se s rostoucím číslem vlny, objevují se různé variace walkerů, letců, tanků apod.
- **Boss event**: Na konci každé vlny (cca 2 minuty) se za okrajem aktuální polohy kamery objeví obrovský Boss s buffovanými statistikami.

### Kolize a poškození
- **Hráč vs Nepřítel**: Kontakt způsobí poškození (podle typu nepřítele) a lehký odraz hráče (knockback)
- **Útok**: Meč má švih (swoosh efekt) a zasáhne všechny nepřátele ve 180° výseči před hráčem
- **Imunita**: 30 snímků po zásahu hráče

### Skóre a Progrese
- **Za zabití nepřítele**: +10 bodů do skóre, padá XP Orb podle typu nepřítele a s 30% šancí zlatá mince (Money).
- **Level up**: Při dosažení hranice potřebných XP získá hráč novou úroveň, čímž se zdvihne množství XP potřebné pro další úroveň (x1.5) a otevře se speciální menu s možností vybrat si jeden upgrade v reálném čase.
- **Žádný trest za smrt**: Hra spadne zpět na začátek, restartuje se nový dungeon od vlny 1

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
PLAYER_MAX_HEALTH = 100
ENEMY_SPAWN_INTERVAL = 60
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
- [x] Boss fights
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
