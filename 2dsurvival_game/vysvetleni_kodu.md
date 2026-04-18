# Vysvětlení kódu – 2D Survival Game

Tento dokument obsahuje podrobný popis všech importů, tříd, metod a funkcí použitých v souboru `2dsurvival_game.py`.

---

## Importy

```python
import pygame       # Herní engine pro 2D grafiku, zvuk a vstup
import random       # Generování náhodných čísel (dungeon, spawn, loot)
import math         # Matematické funkce (trigonometrie pro útok, vzdálenosti)
import sys          # Systémové operace (ukončení programu)
from typing import TypedDict, List, Tuple  # Typové anotace pro lepší čitelnost
```

---

## Konstanty a nastavení

V horní části souboru jsou definovány všechny herní konstanty, které řídí vlastnosti celé hry. Klíčové skupiny:

- **Okno**: `WINDOW_WIDTH/HEIGHT` se nastavují dynamicky podle monitoru (borderless fullscreen), `ZOOM = 1.5` řídí míru přiblížení.
- **Dungeon**: `DUNGEON_SIZE = 5` (5×5 mřížka místností), `BLOCK_SIZE = 32`, `ROOM_MIN/MAX_SIZE`.
- **Hráč**: `PLAYER_SPEED = 5`, `PLAYER_MAX_HEALTH = 100`, `PLAYER_HIT_COOLDOWN = 30`.
- **Útok**: `ATTACK_DURATION = 10`, `ATTACK_SIZE = 40`, `ATTACK_DAMAGE = 10`, `BASE_ATTACK_COOLDOWN = 40`.
- **Nepřátelé**: `ENEMY_SPEED = 2`, `ENEMY_SPAWN_INTERVAL = 60`, `ENEMY_MAX_ON_MAP = 40`, `WAVE_DURATION = 7200` (2 minuty).
- **Předměty**: `ITEM_SIZE = 24`, `HEAL_AMOUNT = 2`, `DAMAGE_BOOST = 2`, `DAMAGE_BOOST_DURATION = 300`.
- **Rarity barvy**: Slovník `RARITY_COLORS` definuje barvy pro Common, Uncommon, Rare, Epic a Legendary upgrade karty.

---

## Třídy

### 1. Třída `Camera` (Herní kamera se zoomem)

Ovládá pohled na herní svět, včetně zoom efektu.

- **`__init__(self, width, height)`**: Inicializuje obdélník kamery podle velikosti světa. Vypočítá `view_w` a `view_h` – skutečnou zobrazovanou oblast po aplikaci zoomu (`WINDOW_WIDTH / ZOOM`).
- **`apply(self, entity)`**: Vrátí posunutý `Rect` entity podle pozice kamery – používá se ke konverzi ze světových souřadnic na souřadnice obrazovky.
- **`update(self, target)`**: Přímo sleduje hráče (cíl) tak, aby byl vždy uprostřed obrazovky. Omezuje posunutí kamery na hranice herního světa, aby nebylo vidět za okraj arény.

### 2. Třída `Block` (Jednotkový blok – stěna/textura)

Pygame sprite tvořící okraje herní arény.

- **`__init__(self, x, y, block_type)`**: Tvoří čtvercový Surface na pozici (x, y) s příslušným typem bloku (`dirt`, `stone`, `grass`, `wood`).
- **`draw_texture(self)`**: Procedurálně generuje texturu bloku pomocí Pygame geometrie (polygon, linky, kruhy, obdélníky) místo načítání `.png` souborů. Každý typ má unikátní vzhled:
  - `dirt` – hnědý povrch s náhodnými kamínky
  - `stone` – šedý s 3D efektem a prasklinami
  - `grass` – zelený povrch s trávou nahoře
  - `wood` – hnědý se suky

### 3. Třída `Item` (Předmět a sběrné orby)

Jakýkoli drobný objekt ležící na ploše (health packy, damage boost meče, klíče, XP krystaly a zlaté mince).

- **`__init__(self, x, y, item_type, xp_value)`**: Vytváří průhledný Surface s ikonou předmětu. Parametr `xp_value` se používá pro XP orby i peníze (u peněz udává počet mincí).
- **`draw_item(self)`**: Každému typu předmětu kreslí jinou ikonu:
  - `health` – červený kříž
  - `damage_boost` – žlutý meč
  - `key` – zlatý klíč
  - `xp` – zelená zářící kulička
  - `money` – zlatá mince s detaily
- **`apply(self, player)`**: Spustí se při překryvu s hráčem. Předmět aplikuje efekt (doplní zdraví, aktivuje boost, přidá XP/peníze/klíč) a poté zmizí pomocí `self.kill()`.
- **`update(self, player)`**: Pro `xp` a `money` předměty implementuje magnetický efekt – pokud je hráč v okruhu 150 pixelů, předmět se k němu přitahuje rychlostí 4 px/snímek.

### 4. Třída `Player` (Hráč a jeho schopnosti)

Nejrozsáhlejší třída. Řídí pohyb, útok, animace, level systém a veškeré herní mechaniky hráče.

- **`__init__(self, x, y)`**: Připraví proměnné životů, souřadnic, zátěžových časovačů pro útok `attack_cooldown`, damage boost, knockback, XP/level systém a generování grafických framů pro cyklus animace.

#### Grafika a animace

- **`draw_player_base(self, surf, is_walking, step)`**: Funkce kreslící kompletní postavu hráče pixel po pixelu – včetně stínu, nohou s animací chůze, paží, těla s opaskem a sponou, hlavy s vlasy a očima. Parametry `is_walking` a `step` řídí pozici nohou a paží pro animaci chůze.
- **`create_idle_frames()`**: Vytvoří 2 framy pro stojící postavu (druhý posunuto o 1 px = efekt dýchání).
- **`create_walk_frames()`**: Vytvoří 4 framy s různým rozložením nohou pro simulaci chůze.
- **`create_attack_frames()`**: Vytvoří 1 frame s mečem (čepel, záštita, rukojeť, hlavice).
- **`create_death_frames()`**: Vytvoří 10 framů – postava s křížky místo očí, postupná rotace a fade-out.

#### Vstup a pohyb

- **`handle_input(self, camera)`**: Zpracovává klávesy WASD/šipky pro pohyb. Normalizuje diagonální pohyb (1/√2). Automaticky spouští útok pokud cooldown vypršel – směr útoku se počítá z pozice myši přes `math.atan2()` s korekcí na ZOOM. Při knockbacku postupně zpomaluje rychlost (×0.85 za snímek).
- **`move(self, blocks)`** a **`collide(self, vel_x, vel_y, blocks)`**: Pohyb nejprve po ose X, pak Y. Při kolizi se zdí se hráč zastaví a rychlost se vynuluje.

#### Update a boj

- **`update(self, blocks, camera)`**: Hlavní update za snímek. Zpracuje vstup, pohyb, cooldowny (útok, imunita, damage boost), vybere správnou animaci a otočí sprite podle směru.
- **`point_in_swing(self, px, py)`** a **`attack_hits(self, enemy)`**: Trigonometrické funkce vyhodnocující, zda oblouk švihu meče zasahuje daného nepřítele (kontrola vzdálenosti + úhel ±90° od směru útoku).
- **`draw_attack(self, screen, camera)`**: Vykresluje srpkovitý slash efekt – polygon s proměnnou tloušťkou (sin profil), barvou podle stavu (cyan normálně, oranžová při damage boostu) a bílým středovým jádrem. Postupný fade-out podle průběhu útoku.

#### Zdraví a XP

- **`take_damage(self, amount)`**: Odečte životy, minimum 0.
- **`heal(self, amount)`**: Přidá životy, maximum `max_health`.
- **`add_xp(self, amount)`**: Přidá XP. Pokud přetečou `max_xp`, level se zvýší, `max_xp` vzroste na 1.5× a nastaví se `level_up_pending` pro zobrazení upgrade menu.
- **`is_dead(self)`**: Vrátí `True` pokud zdraví ≤ 0.

### 5. Třída `Enemy` (Nepřátelé)

Rodičovská třída pro všech 5 typů nepřátel (walker, flying, tank, fast, boss).

- **`__init__(self, x, y, enemy_type)`**: Konfiguruje jednoho z 5 archetypů – liší se zdravím, XP hodnotou, rychlostí a poškozením. Boss má 2× větší velikost (56×56 px).
- **`draw_enemy(self)`**: Pygame kreslící metoda. Maluje rozdílnou ikonku pro každý typ (slime, netopýr, golem, oko, boss). Také vytváří bílou masku (`flash_image`) pro blikající efekt při zranění.
- **`move(self, blocks)`** a **`collide(self, vel_x, vel_y, blocks)`**: Pohyb s kolizí – na rozdíl od hráče, nepřítel se při nárazu do zdi *odrazí* (obrátí směr rychlosti) místo zastavení.
- **`update(self, blocks, player)`**: „Mozek" nepřítele. Snižuje knockback timer (útlum ×0.85), pak podle typu:
  - `walker`, `tank`, `fast`, `boss`: Pronásledují hráče přímočaře (`math.hypot` pro normalizaci směru)
  - `flying`: Samostatný chase s přímým letem
  - Bez hráče: walker se pohybuje horizontálně a odráží se od zdí
- **`take_damage(self, amount)`**: Odečte HP a aktivuje hit flash na 6 snímků.
- **`apply_knockback(self, source_rect)`**: Aplikuje odskok od zdroje poškození. Síla závisí na typu:
  - `walker`: 12 (standardní)
  - `tank`: 4 (odolný)
  - `fast`: 16 (výrazný)
  - `boss`: 1 (minimální)
  - Knockback trvá 15 snímků.
- **`is_dead(self)`**: Vrátí `True` pokud HP ≤ 0.

---

## Architektonické a pomocné funkce

### `generate_dungeon(size)`

Generátor herního světa. Vytváří mřížku `size × size` místností (`RoomDict` objekty) s různými velikostmi. Namísto složitého dungeonu vytváří otevřenou travnatou arénu s kamennými zdmi po obvodu. Vrací:
- `blocks` – sprite group se zdmi
- `items` – prázdná sprite group pro předměty
- `rooms` – seznam místností pro pozicování hráče a počátečních nepřátel

### `spawn_at_screen_edge(camera, offset)`

Vrátí náhodnou pozici za okrajem kamery pro spawn nepřátel. Vybere náhodnou hranu (horní/pravá/dolní/levá) a umístí spawn bod s daným offsetem za viditelnou oblast. Pozice je omezena na hranice herního světa.

### `show_death_screen(screen, score, wave, menu_font, info_font)`

Zobrazí death screen po smrti hráče. Obsahuje:
- Červený nápis "YOU DIED"
- Statistiky (skóre a vlna)
- Dvě tlačítka: "Retry" a "Main Menu"
- Navigace myší nebo klávesami (W/S + Enter)
- Vrací `"retry"` nebo `"main menu"` podle výběru hráče

### `main()` – Hlavní herní smyčka

Vrcholová koordinační funkce, která uvádí do chodu celou hru:

1. **Inicializace**: Vytvoří borderless fullscreen okno, cachuje fonty, generuje dungeon, spawne hráče do první místnosti a rozmístí počáteční nepřátele.
2. **Herní smyčka** (`while running:`), běží 60× za vteřinu:
   - **Eventy**: Zpracování kliknutí (výběr upgradu), ESC (konec), F (fullscreen toggle)
   - **Level Up screen**: Pokud hráč má `level_up_pending > 0`, zobrazí 3 upgrade karty s raritním systémem. Hráč kliknutím vybere 1 upgrade.
   - **Update**: Aktualizace hráče, nepřátel a předmětů
   - **Wave systém**: Timer vlny, spawn nepřátel (rotující typy), boss na konci vlny
   - **Kolize**: Hráč vs nepřátelé (poškození + knockback), útok vs nepřátelé (poškození + knockback + loot), hráč vs předměty (sbírání)
   - **Renderování**: Zelené travnaté pozadí → bloky → předměty → nepřátelé (s hit flash) → hráč (s damage flash) → útok efekt → ZOOM škálování → UI overlay → level up overlay
   - **Smrt**: Po 90 snímcích zobrazí death screen, vrátí `"retry"`, `"menu"` nebo `"quit"`
3. **Upgrade pool**: 15 upgradů v 5 raritních stupních (Common 50%, Uncommon 25%, Rare 15%, Epic 8%, Legendary 2%)

### `main_menu()` – Hlavní menu

Jednoduchý welcome-screen s:
- Tmavě zeleným pozadím s plovoucími částicemi (50 kruhů stoupajících vzhůru)
- Zlatým nápisem "Survival Game" se stínem
- Dvěma tlačítky: "Start Game" a "Quit"
- Navigace myší nebo klávesami (W/S + Enter/Space/Click)

---

## Hlavní smyčka programu (`if __name__ == "__main__":`)

```python
while True:
    action = main_menu()     # Zobrazí menu
    if action == "quit":
        break
    while True:
        action = main()      # Spustí hru
        if action == "retry":
            continue          # Restart hry
        elif action == "menu":
            break             # Zpět do menu
        elif action == "quit":
            pygame.quit()
            sys.exit()
```

Vnořená smyčka umožňuje plynulé přepínání mezi menu → hra → retry/menu bez zbytečného restartu celého programu.

---

*Pokud budete hru jakkoli modifikovat (změnit rychlost, HP nebo poškození), stačí jít do `2dsurvival_game.py` pod horní „Konstanty". Pravidla ve třídách zajistí zbylý matematický chod podle jejich vysvětlení výše.*
