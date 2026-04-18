# 2D Survival Game - Dokumentace

## Přehled hry

**2D Survival Game** je 2D akční survival hra vytvořená v Pythonu s využitím knihovny Pygame. Hra nabízí top-down pohled na procedurálně generovaný dungeon (otevřenou arénu s kamennými okraji), kde hráč musí přežít vlny nepřátel, sbírat předměty, levelovat se a vybírat upgrady s různou vzácností.

## Hlavní mechaniky

### Pohyb a ovládání
- **Pohyb**: Použijte klávesy `WASD` nebo šipky pro pohyb ve všech směrech
- **Útok**: Automatický útok mečem ve směru myši (arc/slash efekt s cooldownem)
- **Fullscreen**: Klávesa `F` pro přepínání mezi oknem a fullscreen režimem
- **Ukončení**: `ESC` pro ukončení hry

### Hráč
- **Zdraví**: Začíná na 100 životech (lze zvýšit upgrady při level up)
- **Úroveň a XP**: Hráč sbírá XP orby z nepřátel; po naplnění lišty XP získá novou úroveň a vyskočí menu pro výběr 1 ze 3 upgradů s raritním systémem (Common → Uncommon → Rare → Epic → Legendary).
- **Rychlost**: 5 pixelů za snímek (normalizovaná diagonála)
- **Útok**: Automatický meč s obloukovým švihem (180° výseč, `ATTACK_SIZE = 40`, cooldown 40 snímků = ~0.67s)
- **Inventář**: Klíče pro potenciální budoucí mechaniky
- **Peníze**: Sbírané zlaté mince z nepřátel
- **Knockback**: Při zásahu nepřítelem je hráč odhozen (1.5× rychlost, 7 snímků)
- **Imunita po zásahu**: 30 snímků po zásahu (blikající červený efekt)

### Nepřátelé

Hra obsahuje pět typů nepřátel s různými vlastnostmi:

#### 1. Walker (Chodec) - Zelený Slime/Zombie
- **Zdraví**: 30 životů (Poškození: 15)
- **XP Hodnota**: 5 XP
- **Chování**: Pronásleduje hráče přímočaře
- **Rychlost**: 2 pixely za snímek
- **Knockback**: Standardní (síla 12)
- **Vzhled**: Zelený zaoblený obdélník s červenýma očima

#### 2. Flying (Létající) - Fialový Netopýr
- **Zdraví**: 20 životů (Poškození: 10)
- **XP Hodnota**: 5 XP
- **Chování**: Pomalý let přímo za hráčem, ignoruje kolize se zdmi stejně jako pozemní jednotky (odraz)
- **Rychlost**: 1 pixel za snímek
- **Knockback**: Standardní (síla 12)
- **Vzhled**: Fialový kruh s křídly a žlutýma očima

#### 3. Tank (Golem) - Šedý
- **Zdraví**: 100 životů (Poškození: 30)
- **XP Hodnota**: 15 XP
- **Chování**: Pohybuje se pomaleji, má velkou výdrž
- **Rychlost**: 1.2 pixelu za snímek (0.6× základ)
- **Knockback**: Snížený (síla 4)
- **Vzhled**: Šedý kámen s oranžovýma očima

#### 4. Fast (Duch/Malé oko) - Průhledný
- **Zdraví**: 10 životů (Poškození: 5)
- **XP Hodnota**: 5 XP
- **Chování**: Rychle se přibližuje k hráči
- **Rychlost**: 3 pixely za snímek (1.5× základ)
- **Knockback**: Výrazný (síla 16)
- **Vzhled**: Částečně průhledný světle modrý kruh s červeným okem

#### 5. Boss - Velký červený golem
- **Zdraví**: 500 životů + 200 za každou další vlnu (Poškození: 40 + 10 za vlnu)
- **XP Hodnota**: 150 XP
- **Chování**: Větší obdoba tanka, spawnuje se na konci každé vlny za okrajem obrazovky
- **Rychlost**: 1.6 pixelu za snímek (0.8× základ)
- **Knockback**: Minimální (síla 1)
- **Velikost**: 2× větší než běžní nepřátelé (56×56 px)
- **Vzhled**: Velký červený blok se žlutýma očima

### Předměty

#### Health Potion (Léčivý lektvar) - Červený kříž
- **Efekt**: Obnoví 2 životy
- **Spawn**: Náhodně v dungeonu (startovní generace)

#### Damage Boost (Posílení útoku) - Žlutý meč
- **Efekt**: Zvětší poškození na 2× po dobu 5 sekund (300 snímků)
- **Spawn**: Náhodně v dungeonu (startovní generace)

#### Key (Klíč) - Oranžový klíč
- **Efekt**: Přidá klíč do inventáře (pro budoucí mechaniky)
- **Spawn**: Náhodně v dungeonu (startovní generace)

#### XP Orb - Zelená zářící kulička
- **Efekt**: Přidá zkušenosti hráči pro postup na novou úroveň
- **Magnetismus**: Samo se přitahuje z blízkosti (do 150 px, rychlost 4 px/snímek)
- **Spawn**: Padá z mrtvých nepřátel

#### Money (Peníze) - Zlatá mince
- **Efekt**: Přičte peníze na konto hráči (1–3 mince)
- **Magnetismus**: Samo se přitahuje z blízkosti (do 150 px, rychlost 4 px/snímek)
- **Spawn**: 30% šance, že padne po zabití jakéhokoliv nepřítele společně s XP orbem

## Herní svět

### Dungeon / Aréna
- **Layout**: Otevřená travnatá aréna ohraničená kamennými zdmi
- **Velikost mřížky**: 5×5 místností (generovaná grid struktura)
- **Místnosti**: Velikost 5–10 bloků (160–320 pixelů) na šířku/výšku
- **Bloky**: 32×32 pixely
- **Materiály zdí**: Stone (Kámen) – šedé texturované bloky po obvodu arény
- **Pozadí**: Zelený travnatý vzor (šachovnicový pattern)

### Zoom a kamera
- **Zoom**: 1.5× přiblížení (hra se renderuje na menší plátno a zvětšuje na celou obrazovku)
- **Rozlišení**: Borderless fullscreen (dynamicky dle monitoru)
- **Sledování**: Kamera přímo sleduje hráče (bez deadzone, bez smooth)
- **Hranice**: Omezena velikostí dungeonu

## Herní mechaniky

### Wave systém
- **Spawn interval**: Začíná na 60 snímcích (1 sekunda), zrychluje se koeficientem 0.985 (minimum 15 snímků)
- **Počet nepřátel**: Základ 1, pomalu se zvyšuje každou vlnu (max 10 za spawn tick)
- **Max nepřátel na mapě**: 40 současně
- **Spawn pozice**: Za okrajem kamery (edge spawning)
- **Druhy nepřátel**: Rotují podle čísla vlny (walker → flying → tank → fast → ...)
- **Délka vlny**: 7200 snímků = 2 minuty při 60 FPS
- **Boss event**: Na konci každé vlny se za okrajem kamery objeví Boss s buffovanými statistikami (HP +200 a damage +10 za každou další vlnu)

### Kolize a poškození
- **Hráč vs Nepřítel**: Kontakt způsobí poškození (podle typu nepřítele) a lehký odskok hráče (knockback 1.5× rychlost, 7 snímků)
- **Útok**: Meč má automatický švih (arc efekt) a zasáhne všechny nepřátele ve 180° výseči kolem směru myši
- **Imunita**: 30 snímků po zásahu hráče (vizuální červené blikání)
- **Hit flash nepřátel**: Při zásahu nepřítel na 6 snímků zběle (bílá maska)
- **Knockback nepřátel**: Každý typ má jinou sílu odskoku (walker: 12, tank: 4, fast: 16, boss: 1)

### Upgrade systém (Level Up)

Při zvýšení úrovně se zobrazí 3 karty s upgrady. Každý upgrade má raritní stupeň ovlivňující pravděpodobnost výběru:

| Rarita | Pravděpodobnost | Barva |
|---|---|---|
| Common | 50 | Šedá (200, 200, 200) |
| Uncommon | 25 | Zelená (50, 205, 50) |
| Rare | 15 | Modrá (30, 144, 255) |
| Epic | 8 | Fialová (138, 43, 226) |
| Legendary | 2 | Zlatá (255, 215, 0) |

#### Dostupné upgrady:

**Common:**
- Minor Vitality: +5 Max HP
- Minor Strength: +1 Damage
- Swiftness: +0.1 Speed

**Uncommon:**
- Warrior: +2 Damage, -2 Max HP
- Stamina: +10 Max HP, Heal 10%
- Sprinter: +0.3 Speed, -1 Dmg

**Rare:**
- Vampire: Heal 30%, +1 Dmg
- Juggernaut: +20 Max HP, -0.1 Speed
- Assassin: +3 Damage, -1 Cooldown

**Epic:**
- Glass Cannon: +5 Damage, -10 Max HP
- Tank: +30 Max HP, -0.2 Speed
- Berserker: +4 Dmg, +0.2 Spd, -5 HP

**Legendary:**
- God of War: +5 Dmg, +20 HP, +0.3 Spd
- Time Weaver: Cooldown -3, +0.5 Spd
- Immortal: +50 Max HP, Heal 100%

### Skóre a Progrese
- **Za zabití nepřítele**: +10 bodů do skóre, padá XP Orb a s 30% šancí zlatá mince (1–3)
- **Level up**: Při dosažení hranice potřebných XP získá hráč novou úroveň, čímž se zdvihne množství XP potřebné pro další úroveň (×1.5) a otevře se speciální menu s výběrem 1 ze 3 upgradů.
- **Smrt**: Zobrazí se death screen s možností "Retry" (restart hry) nebo "Main Menu" (návrat do menu)

## Technické detaily

### Grafika a animace
- **Rozlišení**: Borderless fullscreen (nativní rozlišení monitoru)
- **Zoom**: 1.5× přiblížení (renderování na zmenšené plátno, pak škálování na fullscreen)
- **FPS**: 60 snímků za sekundu
- **Animace hráče**: Idle (2 framy s dýcháním), Walk (4 framy s pohybem nohou), Attack (1 frame s mečem), Death (10 framů s rotací a fade-out)
- **Efekt útoku**: Srpkovitý arc/slash s barevnou září (cyan normálně, oranžová při damage boostu) a bílým středem
- **Hit efekty**: Červené blikání hráče, bílý flash nepřátel
- **Textury**: Procedurálně generované bloky (stone, dirt, grass, wood)

### Audio
- **Aktuální**: Žádný zvuk (pouze vizuální efekty)

### Kódová struktura
- **Hlavní třídy**:
  - `Camera`: Systém kamery se zoomem a sledováním hráče
  - `Block`: Herní bloky s procedurálními texturami
  - `Item`: Sběratelné předměty a orby (XP, peníze, health, damage boost, klíče)
  - `Player`: Hráč s animacemi, útokem, level systémem a mechanikami
  - `Enemy`: Nepřátelé s 5 různými typy, knockbackem a hit flashem
- **Pomocné funkce**:
  - `generate_dungeon()`: Generátor otevřené arény s kamennými stěnami
  - `spawn_at_screen_edge()`: Spawn nepřátel za okrajem kamery
  - `show_death_screen()`: Death screen s výběrem Retry/Main Menu
  - `main()`: Hlavní herní smyčka
  - `main_menu()`: Hlavní menu s částicovým pozadím

### Konstanty
```python
# Okno
WINDOW_WIDTH = <nativní šířka monitoru>
WINDOW_HEIGHT = <nativní výška monitoru>
ZOOM = 1.5
FPS = 60

# Bloky a dungeon
BLOCK_SIZE = 32
DUNGEON_SIZE = 5
ROOM_MIN_SIZE = 5
ROOM_MAX_SIZE = 10

# Hráč
PLAYER_WIDTH = 28
PLAYER_HEIGHT = 28
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_HIT_COOLDOWN = 30

# Útok
ATTACK_DURATION = 10
ATTACK_SIZE = 40
ATTACK_DAMAGE = 10
BASE_ATTACK_COOLDOWN = 40

# Nepřátelé
ENEMY_SIZE = 28
ENEMY_SPEED = 2
FLYING_ENEMY_SPEED = 1
ENEMY_SPAWN_INTERVAL = 60
ENEMY_SPAWN_RADIUS_MIN = 300
ENEMY_SPAWN_ACCELERATION = 0.985
ENEMY_WAVE_BASE = 1
ENEMY_WAVE_GROWTH = 0.05
ENEMY_MAX_PER_WAVE = 10
ENEMY_MAX_ON_MAP = 40
WAVE_DURATION = 7200

# Předměty
ITEM_SIZE = 24
HEAL_AMOUNT = 2
DAMAGE_BOOST = 2
DAMAGE_BOOST_DURATION = 300
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
- [x] Upgrade systém s raritami
- [x] Wave systém s časovačem
- [x] Death screen s Retry/Main Menu
- [x] Knockback systém
- [x] Hit efekty (flash)
- [ ] Upgrade systém pomocí klíčů

### Optimalizace
- [ ] Lepší kolizní detekce
- [ ] Chunk loading systém
- [ ] Particle efekty
- [ ] Smooth animace

## Autoři a verze

**Verze**: 2.0
**Poslední aktualizace**: Duben 2026
**Jazyk**: Python s Pygame
**Platforma**: Windows, Linux, macOS

## Licence

Tento projekt je open-source a může být volně používán a upravován.
