# Vysvětlení kódu hry Survival Game

Tento soubor obsahuje podrobný popis všech importů, tříd a funkcí použitých ve hře `2dsurvival_game.py`. Slouží k lepší orientaci v logice projektu a mechanismu celé hry.

## Použité Importy (Knihovny)
Na začátku souboru se importuje několik důležitých knihoven, které zpřístupňují potřebné funkce:

- **`import pygame`**: Hlavní knihovna celé hry. Zajišťuje renderování grafiky, tvoření herního okna, zjišťování kolizí, přehrávání zvuků a snímání vstupu z klávesnice/myši.
- **`import random`**: Modul používaný na náhodné generování čísel. Využívá se k získávání náhodného tvaru síně, typu nepřítele (např. 70 % šance na chození a 30 % na lítajícího jedince) a posunu textur na blocích, aby herní útvary nepůsobily zcela unifikovaně.
- **`import math`**: Matematická knihovna použitá např. pro výpočet goniometrických funkcí úhlů (rotace kruhového "seku" mečem), nebo zjištění přepony a určování vzdálenostní dráhy mezi hráčem, XP orby nebo nepřáteli.
- **`import sys`**: Systémový import umožňující čisté přerušení chodu programu a vrácení se zpět do operačního systému (např. v menu po stisknutí _Quit_ za využití `sys.exit()`).
- **`from typing import TypedDict, List, Tuple, cast`**: Rozšíření na tzv. type hinting (vysvětlování typů). Umožňuje definovat předpisy pro slovníky (zde např. vlastní třída `RoomDict`) a listové struktury, takže Python (nebo editor) lépe odhaluje syntaktické chyby ještě před spuštěním.

---

## Třídy a Funkce

### 1. Třída `Camera` (Objektivní rozhraní kamery)
Základní nástroj zajišťující to, že hráč vždy vidí "sebe" a posouvající se okolí, i když je herní svět mnohonásobně větší než okno.

- **`__init__(self, width, height)`**: Vytvoří logickou kameru se známými rozměry šířky a výšky (které obvykle kopírují hranice herního světa). 
- **`apply(self, entity)`**: Velmi důležitá funkce. Berla se u vykreslování v paměti: vezme pozici herního objektu ve světě a zpětně ji "posune" podle toho, kde teď kamera na svět kouká. Díky tomu je všechno namalováno na správném místě na obrazovce monitoru.
- **`update(self, target)`**: Přesouvá samotnou osu kamery podle pozice cíle (hráče). Obsahuje mechanismus tvz. *Deadzone*. Kamera "dýchá" a nepohybuje osou pro každý maličnatý posun hráče, jen v případě, že vyjde na daný okraj její hlídací zóny. Brání také tomu, aby sledovala černé místo mimo hraniční bloky světa.

### 2. Třída `Block` (Jednotkový čtvereční blok - stěna či textury)
Hrací prvky, tvořící okraje herní "arény".

- **`__init__(self, x, y, block_type)`**: Tvoří čtvercový Surface na ose X a Y mapy s příslušným tagem bloku (`dirt`, `stone`, `grass`, aj.).
- **`draw_texture(self)`**: Namísto načítání `.png` souborů si hra interně přes Pygame geometrii (polygon, linky a kruhy) maluje různé vizuální odchylky na bloky z barev tak, aby vypadaly jako kámen nebo hlína. Random funkce zajištuje rozmanité drážky na kamenech.

### 3. Třída `Item` (Předmět a sběrné orby)
Jakýkoli drobný objekt ležící na ploše (health packy, damage boost mečečky, klíče či XP krystaly a zlaté mince padající ze zabitých nepřátel).

- **`__init__(...)`**: Vytváří neviditelný prostor, do kterého umístí specifický povrch, pozici středu obdélníku a zapamatuje síly/xp zkušenosti daného lotu.
- **`draw_item(self)`**: Každému typu předmětu kreslí jinou ikonu s průsvitným modřinatým podkladem (kříž, zářicí zelený orb z XP kuličky, zlatá mince s `money` apod.)
- **`apply(self, player)`**: Spustí proceduru ve chvíli, kdy byl zjištěn překryv bounding obdélníku `Item`u s hráčovým `Player`. Předmět samotný doplní zdraví, boost nebo XP a hned nato sám ze hrací plochy zmizí pomocí funkce `self.kill()`.
- **`update(self, player=None)`**: Kontroluje, jestli je hráč v okruhu např. 150 pixelů a aplikuje "Magnet" tah XP a peněžních předmětů (čímž se XP/peníze samy pohybují/padají k hráči z určité dálky, jako v tradičních survivor idle hrách).

### 4. Třída `Player` (Hráč a jeho schopnosti)
Jedná se o nejrobustnější třídu. Hýbe vaší modrou postavičkou na scéně, útočí, přijímá expy.

- **`__init__(self, x, y)`**: Připraví proměnné životů, souřadnic, zátěžových časovačů pro útok `attack_cooldown` a generování grafických framů pro cyklus animace.
- **`draw_player_base(self, ...)`**: Zjednodušená ruční renderovací obalující metoda pro kostru postavičky (čepice, tělo, oči, stín apod.).
- **Metody `create_idle_frames`, `create_walk_frames`, ...**: Vratí např. 4 odlišně posunuté stopy Surface ploch tvz. sprite formát postavičky. Postupně v cyklech za sebou tvoří iluzi, že postava pohybuje nohama.
- **`handle_input(self, camera)`**: Klíčová funkce starající se o sbírání toho, zda mačkáte klávesy WASD nebo šipky, abyste provedl posuvy po rovině pixelů. Současně se orientuje podle snímače polohy myši (skrz argument `camera`), a dojde k uložení úhlu pro sek, pokud se provádí attack loop a cooldown klesne v dalším updatu. Pohnutí čte trigonometrii myši (`math.atan2(...)`) pro správný polohovací rozptyl.
- **`move(self, blocks)`** a **`collide(self, vel_x, vel_y, blocks)`**: Tyto dvě spojené funkce se prohánějí cyklem při stisku tlačítka. Pohyb na X osu, doraz, jestli náhodou nezasahuje kolizní obdélník do stěny. Následně pohyb na Y, opět sraz do plných kamenů. Posouvá vnitřní stěnu herního rozložení při nárazu těsnejíc.
- **`update(self, ...)`**: Koordinující metoda hráče per snímek. Redukuje imunitu hráče po napadení, resetuje poškození posbíraného předmětu, zajišťuje promítání rotací spritů a odrážecí efekty po hranicích neviditelného polského obrubníku na mapě.
- **`point_in_swing(self)` a `attack_hits(self, enemy)`**: Vzorce vyhodnocující, jestli rozkroju obloukovitá vzdálenost seče opravdu prolínla obvodem nepřátel ("zásahová hitbox kružnice").
- **`draw_attack(self, screen, camera)`**: Graficky znázorňuje (z render oblouků) velkou zbraň-červenou stuhu obloučkovým způsobem s fade-out přechody, díky čemuž je útok čitelný.
- **Health / Healing a XP (`take_damage`, `add_xp`,...)**: Správa metrik. Při přetečení maxima XP posunou `level` o cifru dál a vytvoří událost, na kterou později zareaguje menu nabídek.

### 5. Třída `Enemy` (Generátor zloduchů)
Rodičovská třída pro chodící i létající nepřátele a poskoky útočící na charakter.

- **`__init__(...)`**: Konfiguruje jednoho z 5 mobích archetypů (`walker`, `flying`, `tank`, `fast`, `boss`) - liší se zdravím, zkušenostmi posmrtného lootu a rychlostmi pohybu i poškozením.
- **`draw_enemy(self)`**: Opět pygame kreslící metoda. Maluje rozdílnou ikonku (např. golem vs stín plášť, boss). Také si přesunou Mask image (bílý maskovaný duplikát určený pro blikající zranění `flash_image`).
- **`collide(...)`, `move(...)`**: Identické principy neprostoupení zdí odvozené z hráče s jedním defacto drobným rozdílem - `Enemy` má automatické chování, kdy mu náraz zeď převrací logiku pohybu do odrazu namísto čirého zastavení.
- **`update(self, blocks, player)`**: Mozek protivníka. Snižuje se mu knockback z blikajícího efektu a aplikuje orientační zjišťování `math.hypot(dx, dy)`. Jestli je nablízko `player`, natankuje k němu svůj vektor rychlosti podle svého mobového chování (letec ignoruje záseky a plynulounce míří zkratou k cíli).

### 6. Architektonické sjednocovací Funkce

**`generate_dungeon(size)`**
- Namísto složité mapové matrice vytváří z definovaného grid bloku seznam "Room"ů (místnosti - `RoomDict` objektů). Posléze je obkreslí po obvodě jako obrovský sál kamenem (`block_map[_] = 'stone'`). Vrací listové kolekce bloků na zdi a `rooms` koordinátorů pro inicializační body. Zabraňuje tomu, aby byl hrací pole plochou k prázdnu a ohraničí jej na určitou pixelovou mapu chránící vnitřní "arénu".

**`main()`**
- Vrcholový koordinační cyklus, který uvádí do logického celku a chodu "srdeční tep" hry s reálnými parametry:
  1. Spouští Pygame grafiku a hodiny (`pygame.time.Clock()`).
  2. Generuje a ukládá bloky. Respawnuje hráče do spravné místnosti.
  3. Spouští hlavní vnější `while running:` cyklus (tvz. `Game Loop`), jenž běží 60x za vteřinu dokud nenastane smrt či vypnutí křížkem. Tady uvnitř proběhne vše zásadní:
    - Vyhodnocování inputů event.
    - Kontrola `Level UP!` obrazovky (Zpomalí hru pro případ, že máte zvolit `Max Health +20` , `Damage` apod.).
    - Volá zástupům mobů, itemům a kameře posílat jejich iterované `update()` up-to-date funkce.
    - Zvyšuje tzv. Timer wave časovače (který dělá hordu mobů intenzivnější a agresivnější díky přidávání intervalů tvz. Spawn pointů). Při re-startu timeru po ukončení Wave pošle do scény Bosse.
    - Definuje ošetření kolizních nárazů (Pokud zbranˇ `player` hitne stvůru - ubere hp nepříteli - přičemž pokud HP stvůry <= 0 zanechá list pro Item 'XP' orbu, popř. s 30% šancí peníze a zemře) a podobně se vyhodnotí na zemi spadené item buffy.
    - Po proběhnutém updatování logiky přichází podbarvení pozadí a kreslicí vrstva `screen.blit().` UI se nanese na displej přes vše a pak se celé okénko vizuální grafiky zobrazí uživateli.

**`main_menu()`**
- Jednodušší "Welcome-screen" cyklus, který nese nekonečnou smyčku vykreslovacího pole na černém plátně a provádí navigaci tlačítek před předáním klíčů do funkce `main()`, pro faktické zahájení logiky a instancí hraní.

---
*Pokud budete hru jakkoli modifikovat (změnit rychlost, HP nebo poškození), stačí jít do `2dsurvival_game.py` pod horní "Konstanty". Pravidla ve třídách zajistí zbylý matematický chod podle jejich vysvětlení výše.*
