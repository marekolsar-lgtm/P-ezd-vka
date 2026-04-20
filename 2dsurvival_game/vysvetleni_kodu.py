# =============================================================================
# VYSVETLENI KODU – 2D SURVIVAL GAME
# Tento soubor obsahuje KOMPLETNÍ kód hry s podrobným komentářem ke každému řádku.
# Soubor NESPOUŠTĚJTE – slouží pouze jako dokumentace.
# =============================================================================

# ---- IMPORTY ----
import pygame                                  # Pygame – hlavní herní knihovna pro 2D grafiku, zvuk, ovládání okna a vstup z klávesnice/myši
import random                                  # Random – generátor náhodných čísel (pro spawn nepřátel, generování dungeonu, drop předmětů)
import math                                    # Math – matematické funkce (sin, cos, atan2, hypot) – používá se pro výpočet úhlů útoku a vzdáleností
import sys                                     # Sys – systémové funkce, hlavně sys.exit() pro úplné ukončení programu
from typing import TypedDict, List, Tuple      # Typing – typové anotace pro lepší čitelnost kódu (TypedDict pro strukturu místnosti)

# ---- TYPOVÁ DEFINICE PRO MÍSTNOST ----
class RoomDict(TypedDict):                     # Definuje tvar slovníku pro jednu místnost v dungeonu
    x: int                                     # x-ová souřadnice místnosti ve světě (v pixelech)
    y: int                                     # y-ová souřadnice místnosti ve světě (v pixelech)
    width: int                                 # šířka místnosti v pixelech
    height: int                                # výška místnosti v pixelech
    grid_x: int                                # pozice místnosti v mřížce (sloupec)
    grid_y: int                                # pozice místnosti v mřížce (řádek)
    doors: List[Tuple[int, int]]               # seznam dveří – každá dveře jsou (x, y) souřadnice

# ---- INICIALIZACE PYGAME ----
pygame.init()                                  # Spustí všechny moduly Pygame (grafiku, zvuk, fonty atd.) – musí být voláno před čímkoli dalším

# ---- KONSTANTY PRO OKNO ----
infoObject = pygame.display.Info()             # Získá informace o aktuálním monitoru (rozlišení, barevná hloubka atd.)
WINDOW_WIDTH = infoObject.current_w            # Šířka okna = šířka monitoru (pro borderless fullscreen)
WINDOW_HEIGHT = infoObject.current_h           # Výška okna = výška monitoru
TITLE = "Survival Game"                        # Titulek okna zobrazený v záhlaví
FPS = 60                                       # Počet snímků za sekundu – hra běží 60× za sekundu
ZOOM = 1.5                                     # Míra přiblížení kamery – 1.5× zvětšuje vykreslovanou oblast

# ---- BARVY RARIT PRO UPGRADE KARTY ----
RARITY_COLORS = {                              # Slovník mapující název rarity na RGB barvu
    "Common": (200, 200, 200),                 # Common = šedá
    "Uncommon": (50, 205, 50),                 # Uncommon = zelená
    "Rare": (30, 144, 255),                    # Rare = modrá
    "Epic": (138, 43, 226),                    # Epic = fialová
    "Legendary": (255, 215, 0)                 # Legendary = zlatá
}

# ---- ZÁKLADNÍ BARVY ----
BLACK = (0, 0, 0)                              # Černá – pozadí, okraje
WHITE = (255, 255, 255)                        # Bílá – texty, okraje tlačítek
RED = (255, 0, 0)                              # Červená – poškození, zdraví
GREEN = (0, 255, 0)                            # Zelená – XP, léčení
BLUE = (0, 0, 255)                             # Modrá – záložní barva
BROWN = (139, 69, 19)                          # Hnědá – dřevo, zem
GRAY = (128, 128, 128)                         # Šedá – kámen
YELLOW = (255, 255, 0)                         # Žlutá – efekty, zvýraznění
PURPLE = (128, 0, 128)                         # Fialová – speciální nepřátelé
ORANGE = (255, 165, 0)                         # Oranžová – vlnový text
CYAN = (0, 255, 255)                           # Tyrkysová – level text

# ---- VELIKOST BLOKU ----
BLOCK_SIZE = 32                                # Velikost jednoho bloku (stěny) v pixelech – 32×32 px

# ---- ROZMĚRY DUNGEONU ----
DUNGEON_SIZE = 5                               # Mřížka dungeonu je 5×5 místností
ROOM_MIN_SIZE = 5                              # Minimální velikost místnosti v blocích (5 bloků = 160 px)
ROOM_MAX_SIZE = 10                             # Maximální velikost místnosti v blocích (10 bloků = 320 px)

# ---- HRÁČ ----
PLAYER_WIDTH = 28                              # Šířka hráče v pixelech
PLAYER_HEIGHT = 28                             # Výška hráče v pixelech
PLAYER_SPEED = 5                               # Rychlost pohybu hráče v pixelech za snímek

# ---- NEPŘÁTELÉ ----
ENEMY_SIZE = 28                                # Velikost nepřítele v pixelech (28×28)
ENEMY_SPEED = 2                                # Základní rychlost chodícího nepřítele
FLYING_ENEMY_SPEED = 1                         # Rychlost létajícího nepřítele (pomalejší)
ENEMY_SPAWN_INTERVAL = 60                      # Počet snímků mezi spawnem nové vlny nepřátel (60 = 1 sekunda)
ENEMY_SPAWN_RADIUS_MIN = 300                   # Minimální vzdálenost od hráče při spawnu (aby se neobjevili přímo na hráči)
ENEMY_SPAWN_ACCELERATION = 0.985               # Koeficient zrychlování spawnu – interval se každou vlnou zkracuje o 1.5%
ENEMY_WAVE_BASE = 1                            # Počáteční počet nepřátel na vlnu
ENEMY_WAVE_GROWTH = 0.05                       # O kolik se zvyšuje počet nepřátel za spawn (každých ~20 spawnů +1 nepřítel)
ENEMY_MAX_PER_WAVE = 10                        # Maximální počet nepřátel v jednom spawnu
ENEMY_MAX_ON_MAP = 40                          # Maximální celkový počet nepřátel na mapě najednou
WAVE_DURATION = 7200                           # Délka jedné vlny v snímcích (7200 / 60 = 120 sekund = 2 minuty)

# ---- ÚTOK ----
ATTACK_DURATION = 10                           # Délka trvání útoku v snímcích
ATTACK_SIZE = 40                               # Velikost oblast útoku (dosah meče) v pixelech
ATTACK_DAMAGE = 10                             # Základní poškození útoku
BASE_ATTACK_COOLDOWN = 40                      # Počet snímků mezi útoky (cooldown)

# ---- ZDRAVÍ HRÁČE ----
PLAYER_MAX_HEALTH = 100                        # Maximální zdraví hráče na začátku
PLAYER_HIT_COOLDOWN = 30                       # Počet snímků imunity po zásahu (0.5 sekundy)

# ---- PŘEDMĚTY ----
ITEM_SIZE = 24                                 # Velikost ikony předmětu v pixelech
HEAL_AMOUNT = 2                                # Kolik zdraví doplní health pickup
DAMAGE_BOOST = 2                               # Násobič poškození při damage boostu
DAMAGE_BOOST_DURATION = 300                    # Délka damage boostu v snímcích (5 sekund)


# =============================================================================
# TŘÍDA CAMERA (HERNÍ KAMERA SE ZOOMEM)
# Kamera sleduje hráče a zajišťuje, že je vždy uprostřed obrazovky.
# Podporuje zoom – vykresluje menší oblast, která se pak zvětší na celé okno.
# =============================================================================
class Camera:
    def __init__(self, width, height):          # Konstruktor – přijímá šířku a výšku celého herního světa
        self.rect = pygame.Rect(0, 0, width, height)  # Obdélník kamery – pokrývá celý svět
        self.width = width                     # Šířka světa v pixelech
        self.height = height                   # Výška světa v pixelech
        self.view_w = int(WINDOW_WIDTH / ZOOM) # Skutečná šířka viditelné oblasti po zoomu (okno / zoom)
        self.view_h = int(WINDOW_HEIGHT / ZOOM)# Skutečná výška viditelné oblasti po zoomu

    def apply(self, entity):                   # Vrátí posunutý obdélník entity tak, aby odpovídal pozici kamery
        if hasattr(entity, 'rect'):            # Pokud má entita atribut 'rect' (hráč, nepřítel, blok...)
            return entity.rect.move(self.rect.x, self.rect.y)  # Posune rect o offset kamery
        else:                                  # Jinak jde o samostatný Rect (útok)
            return entity.move(self.rect.x, self.rect.y)       # Posune rect o offset kamery

    def update(self, target):                  # Aktualizuje pozici kamery tak, aby cíl (hráč) byl uprostřed
        target_x = -target.rect.centerx + self.view_w // 2    # Cílový X offset – centruje hráče horizontálně
        target_y = -target.rect.centery + self.view_h // 2    # Cílový Y offset – centruje hráče vertikálně

        x = target_x                          # Nastavení X pozice kamery
        y = target_y                          # Nastavení Y pozice kamery

        # Omezení kamery na hranice světa (horizontálně)
        if self.width > self.view_w:           # Pokud je svět širší než viditelná oblast
            x = min(0, x)                      # Kamera nemůže jít za levý okraj (x nesmí být kladné)
            x = max(-(self.width - self.view_w), x)  # Kamera nemůže jít za pravý okraj
        else:                                  # Svět je menší než okno
            x = 0                              # Kamera zůstává na pozici 0

        # Omezení kamery na hranice světa (vertikálně)
        if self.height > self.view_h:          # Pokud je svět vyšší než viditelná oblast
            y = min(0, y)                      # Kamera nemůže jít za horní okraj
            y = max(-(self.height - self.view_h), y)  # Kamera nemůže jít za dolní okraj
        else:                                  # Svět je menší než okno
            y = 0                              # Kamera zůstává na pozici 0

        self.rect.x = x                        # Uloží konečnou X pozici kamery
        self.rect.y = y                        # Uloží konečnou Y pozici kamery


# =============================================================================
# TŘÍDA BLOCK (BLOK – STĚNA / TEXTURA)
# Pygame sprite tvořící stěny a okraje herní arény.
# Každý blok má procedurálně generovanou texturu (dirt, stone, grass, wood).
# =============================================================================
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type='dirt'):       # Konstruktor – pozice a typ bloku
        super().__init__()                             # Volání konstruktoru nadřazené třídy Sprite
        self.block_type = block_type                   # Uloží typ bloku ('dirt', 'stone', 'grass', 'wood')
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))  # Vytvoří Surface (obrázek) o velikosti bloku
        self.rect = self.image.get_rect(topleft=(x, y))        # Nastaví pozici bloku ve světě
        self.draw_texture()                            # Zavolá metodu pro vykreslení textury

    def draw_texture(self):                            # Procedurální generování textury bloku
        if self.block_type == 'dirt':                  # Typ: hlína
            self.image.fill((120, 82, 45))             # Vyplní hnědou barvou
            for _ in range(8):                         # Přidá 8 náhodných kamínků
                dx = random.randint(0, BLOCK_SIZE-4)   # Náhodná X pozice kamínku
                dy = random.randint(0, BLOCK_SIZE-4)   # Náhodná Y pozice kamínku
                pygame.draw.rect(self.image, (90, 50, 20), (dx, dy, 4, 3))  # Vykreslí tmavší obdélníček

        elif self.block_type == 'stone':               # Typ: kámen
            self.image.fill((100, 100, 105))           # Šedý základ
            pygame.draw.rect(self.image, (140, 140, 145), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 2)  # Světlejší okraj (3D efekt)
            pygame.draw.polygon(self.image, (70, 70, 75), [(0, BLOCK_SIZE), (BLOCK_SIZE, BLOCK_SIZE), (BLOCK_SIZE, 0)])  # Tmavší trojúhelník (stín)
            pygame.draw.rect(self.image, (100, 100, 105), (2, 2, BLOCK_SIZE-4, BLOCK_SIZE-4))  # Vnitřní plocha
            for _ in range(3):                         # 3 náhodné praskliny
                dx = random.randint(4, BLOCK_SIZE-6)   # X pozice praskliny
                dy = random.randint(4, BLOCK_SIZE-6)   # Y pozice praskliny
                pygame.draw.rect(self.image, (80, 80, 85), (dx, dy, 4, 4))  # Tmavší čtvereček

        elif self.block_type == 'grass':               # Typ: tráva
            self.image.fill((120, 82, 45))             # Hnědý základ (hlína pod trávou)
            pygame.draw.rect(self.image, (34, 139, 34), (0, 0, BLOCK_SIZE, 12))  # Zelený pruh nahoře
            pygame.draw.rect(self.image, (0, 100, 0), (0, 10, BLOCK_SIZE, 3))    # Tmavší linka oddělující trávu od hlíny
            for i in range(5):                         # 5 stébel trávy
                x = i * 6 + 2                          # Rovnoměrné rozložení stébel
                h = random.randint(3, 6)               # Náhodná výška stébla
                pygame.draw.line(self.image, (50, 200, 50), (x, 10), (x+random.randint(-1, 1), 10-h), 2)  # Zelená linka nahoru

        elif self.block_type == 'wood':                # Typ: dřevo
            self.image.fill((139, 69, 19))             # Hnědý základ
            pygame.draw.rect(self.image, (101, 33, 0), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 2)  # Tmavší okraj
            for i in range(4):                         # 4 letokruhy (vodorovné čáry)
                y = i * 8 + 4                          # Rovnoměrné rozložení
                pygame.draw.line(self.image, (101, 33, 0), (0, y), (BLOCK_SIZE, y), 2)  # Tmavší čára

        else:                                          # Neznámý typ – záložní bílý blok
            self.image.fill(WHITE)                     # Bílá výplň

        # Jemný černý okraj kolem každého bloku
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 1)


# =============================================================================
# TŘÍDA ITEM (PŘEDMĚT – HEALTH, DAMAGE BOOST, KLÍČ, XP, PENÍZE)
# Předměty ležící na zemi, které hráč může sebrat.
# XP a money mají magnetický efekt – přitahují se k hráči.
# =============================================================================
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type='health', xp_value=0):  # Konstruktor – pozice, typ a hodnota
        super().__init__()                             # Volání konstruktoru nadřazené třídy Sprite
        self.item_type = item_type                     # Typ předmětu ('health', 'damage_boost', 'key', 'xp', 'money')
        self.xp_value = xp_value                       # Hodnota předmětu (pro XP orby = množství XP, pro peníze = počet mincí)
        self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA)  # Průhledný Surface
        self.rect = self.image.get_rect(center=(x + BLOCK_SIZE//2, y + BLOCK_SIZE//2))  # Centruje na pozici bloku
        self.draw_item()                               # Vykreslí ikonu předmětu

    def draw_item(self):                               # Vykreslí grafiku předmětu podle typu
        self.image.fill((0, 0, 0, 0))                  # Vyčistí – průhledné pozadí
        pygame.draw.circle(self.image, (255, 255, 255, 50), (12, 12), 10)  # Lehký bílý záblesk (glow efekt)

        if self.item_type == 'health':                 # Zdravotní balíček – červený kříž
            pygame.draw.rect(self.image, (150, 0, 0), (6, 10, 12, 4))     # Vodorovná čára kříže (tmavě červená)
            pygame.draw.rect(self.image, (150, 0, 0), (10, 6, 4, 12))     # Svislá čára kříže (tmavě červená)
            pygame.draw.rect(self.image, (255, 50, 50), (7, 11, 10, 2))   # Vodorovný proužek (světle červená)
            pygame.draw.rect(self.image, (255, 50, 50), (11, 7, 2, 10))   # Svislý proužek (světle červená)

        elif self.item_type == 'damage_boost':         # Damage boost – žlutý meč
            pygame.draw.polygon(self.image, (200, 100, 0), [(12, 3), (22, 13), (18, 17), (8, 7)])   # Čepel meče (tmavá)
            pygame.draw.polygon(self.image, (255, 215, 0), [(13, 4), (20, 11), (17, 14), (10, 7)])   # Čepel meče (světlá)
            pygame.draw.rect(self.image, (139, 69, 19), (6, 15, 6, 6))    # Rukojeť meče (hnědá)

        elif self.item_type == 'key':                  # Klíč – zlatý
            pygame.draw.circle(self.image, (255, 215, 0), (8, 12), 5, 2)  # Kroužek klíče (obrys)
            pygame.draw.rect(self.image, (255, 215, 0), (13, 11, 8, 2))   # Dřík klíče
            pygame.draw.rect(self.image, (255, 215, 0), (17, 13, 2, 3))   # Zuby klíče 1
            pygame.draw.rect(self.image, (255, 215, 0), (20, 13, 2, 2))   # Zuby klíče 2

        elif self.item_type == 'xp':                   # XP orb – zelená zářící kulička
            pygame.draw.circle(self.image, (0, 255, 100), (12, 12), 6)    # Vnější zelený kruh
            pygame.draw.circle(self.image, (200, 255, 200), (12, 12), 3)  # Vnitřní světlý střed

        elif self.item_type == 'money':                # Zlatá mince
            pygame.draw.circle(self.image, (255, 215, 0), (12, 12), 6)    # Tělo mince (zlaté)
            pygame.draw.circle(self.image, (218, 165, 32), (12, 12), 6, 2)# Okraj mince (tmavší)
            pygame.draw.rect(self.image, (218, 165, 32), (11, 8, 2, 8))   # Svislý proužek uprostřed (detail)

    def apply(self, player):                           # Aplikuje efekt předmětu na hráče
        if self.item_type == 'health':                 # Zdravotní balíček
            player.heal(HEAL_AMOUNT)                   # Doplní hráči HEAL_AMOUNT zdraví
        elif self.item_type == 'damage_boost':         # Damage boost
            player.damage_boost = DAMAGE_BOOST         # Nastaví násobič poškození
            player.damage_boost_timer = DAMAGE_BOOST_DURATION  # Spustí časovač boostu
        elif self.item_type == 'key':                  # Klíč
            player.keys += 1                           # Přidá 1 klíč do inventáře
        elif self.item_type == 'xp':                   # XP orb
            player.add_xp(self.xp_value)               # Přidá XP (může způsobit level up)
        elif self.item_type == 'money':                # Peníze
            player.money += self.xp_value              # Přidá počet mincí (uložen v xp_value)
        self.kill()                                    # Odstraní předmět ze všech sprite groups (zmizí z mapy)

    def update(self, player=None):                     # Aktualizace každý snímek – magnetický efekt
        if player and self.item_type in ['xp', 'money']:  # Magnetismus funguje jen pro XP a peníze
            dx = player.rect.centerx - self.rect.centerx   # Vzdálenost k hráči na ose X
            dy = player.rect.centery - self.rect.centery   # Vzdálenost k hráči na ose Y
            dist = math.hypot(dx, dy)                      # Přímá vzdálenost (Pythagorova věta)
            if 0 < dist < 150:                             # Pokud je hráč v dosahu 150 pixelů
                speed = 4.0                                # Rychlost přitahování
                self.rect.x += int((dx / dist) * speed)    # Posun směrem k hráči (X)
                self.rect.y += int((dy / dist) * speed)    # Posun směrem k hráči (Y)


# =============================================================================
# TŘÍDA PLAYER (HRÁČ)
# Nejrozsáhlejší třída – řídí pohyb, útok, animace, level systém,
# damage boost, knockback a veškeré herní mechaniky hráče.
# =============================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):                          # Konstruktor – počáteční pozice hráče
        super().__init__()                             # Volání konstruktoru Sprite
        self.width = PLAYER_WIDTH                      # Šířka hráče
        self.height = PLAYER_HEIGHT                    # Výška hráče
        self.rect = pygame.Rect(x, y, self.width, self.height)  # Obdélník hráče (pozice + velikost)
        self.vel_x = 0                                 # Aktuální horizontální rychlost
        self.vel_y = 0                                 # Aktuální vertikální rychlost
        self.max_health = PLAYER_MAX_HEALTH            # Maximální zdraví
        self.health = self.max_health                  # Aktuální zdraví (začíná na max)
        self.attacking = False                         # Zda právě probíhá útok
        self.attack_timer = 0                          # Zbývající snímky útoku
        self.attack_cooldown = 0                       # Zbývající snímky do dalšího útoku
        self.attack_damage = ATTACK_DAMAGE             # Základní poškození útoku
        self.money = 0                                 # Počet nasbíraných mincí
        self.attack_hitbox = pygame.Rect(0, 0, ATTACK_SIZE, ATTACK_SIZE)  # Obdélník zásahu útoku
        self.facing_right = True                       # Směr otočení hráče (True = doprava)
        self.attack_angle = 0                          # Úhel útoku ve stupních
        self.damage_boost = 1                          # Násobič poškození (1 = normální, 2 = boost)
        self.damage_boost_timer = 0                    # Zbývající čas damage boostu
        self.keys = 0                                  # Počet sebraných klíčů
        self.hit_cooldown = 0                          # Zbývající snímky imunity po zásahu
        self.knockback_timer = 0                       # Zbývající snímky knockbacku (odskok)
        self.xp = 0                                    # Aktuální zkušenostní body
        self.level = 1                                 # Aktuální level
        self.max_xp = 10                               # XP potřebné pro další level
        self.hit_enemies = set()                       # Množina nepřátel zasažených aktuálním útokem (aby jeden švih nezasáhl dvakrát)
        self.level_up_pending = 0                      # Počet čekajících level-upů (zobrazí se upgrade menu)

        # Příprava animačních framů pro všechny stavy
        self.animation_frames = {                      # Slovník s framy pro každý stav animace
            'idle': self.create_idle_frames(),         # Stání – 2 framy (efekt dýchání)
            'walk': self.create_walk_frames(),         # Chůze – 4 framy (pohyb nohou)
            'attack': self.create_attack_frames(),     # Útok – 1 frame (meč v ruce)
            'death': self.create_death_frames()        # Smrt – 10 framů (rotace + fade out)
        }
        self.current_animation = 'idle'                # Výchozí animace = stání
        self.frame_index = 0                           # Aktuální index framu v animaci
        self.animation_speed = 0.2                     # Rychlost přepínání framů (0.2 = každých 5 snímků)
        self.image = self.animation_frames['idle'][0]  # Aktuální obrázek = první frame stání

    # ---- VYKRESLENÍ POSTAVY ----
    def draw_player_base(self, surf, is_walking=False, step=0):  # Kreslí kompletní postavu pixel po pixelu
        surf.fill((0, 0, 0, 0))                        # Vyčistí surface (průhledné pozadí)

        # Stín pod postavou
        shadow_w = 20 if not is_walking else 22        # Při chůzi je stín trochu širší
        shadow_x = 4 if not is_walking else 3          # Při chůzi je stín posunutý
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (shadow_x, 23, shadow_w, 5))  # Černý poloprůhledný ovál

        # Nohy s animací chůze
        leg_y = 19                                     # Základní Y pozice nohou
        leg1_y = leg_y - (2 if is_walking and step in [0, 1] else 0)  # Levá noha se zvedne v krocích 0 a 1
        leg2_y = leg_y - (2 if is_walking and step in [2, 3] else 0)  # Pravá noha se zvedne v krocích 2 a 3

        # Levá noha
        pygame.draw.rect(surf, (20, 20, 80), (8, leg1_y, 4, 7))       # Tmavě modré kalhoty
        pygame.draw.rect(surf, (50, 50, 50), (7, leg1_y + 5, 6, 3), border_radius=1)  # Šedá bota

        # Pravá noha
        pygame.draw.rect(surf, (20, 20, 80), (16, leg2_y, 4, 7))      # Tmavě modré kalhoty
        pygame.draw.rect(surf, (50, 50, 50), (15, leg2_y + 5, 6, 3), border_radius=1)  # Šedá bota

        # Zadní ruka (za tělem)
        arm1_y = 12 - (1 if is_walking and step in [2, 3] else 0)     # Ruka se zvedne s opační nohou
        pygame.draw.rect(surf, (0, 80, 180), (4, arm1_y, 4, 7), border_radius=2)      # Rukáv (modrý)
        pygame.draw.rect(surf, (255, 224, 189), (4, arm1_y + 5, 4, 3), border_radius=1)  # Ruka (kůže)

        # Tělo
        pygame.draw.rect(surf, (0, 100, 220), (6, 10, 16, 10), border_radius=3)       # Modrá košile
        pygame.draw.rect(surf, (0, 80, 180), (6, 15, 16, 5), border_bottom_left_radius=3, border_bottom_right_radius=3)  # Stín na košili

        # Opasek
        pygame.draw.rect(surf, (90, 45, 0), (6, 17, 16, 3))           # Hnědý pásek
        pygame.draw.rect(surf, (255, 215, 0), (12, 16, 4, 5), border_radius=1)  # Zlatá spona
        pygame.draw.rect(surf, (200, 150, 0), (13, 17, 2, 3))         # Detail spony

        # Hlava
        pygame.draw.rect(surf, (255, 224, 189), (7, 2, 14, 11), border_radius=4)      # Obličej (barva kůže)
        pygame.draw.rect(surf, (230, 190, 150), (7, 9, 14, 4), border_bottom_left_radius=4, border_bottom_right_radius=4)  # Stín na tváři

        # Vlasy
        pygame.draw.rect(surf, (80, 40, 0), (6, 0, 16, 4), border_top_left_radius=5, border_top_right_radius=5)  # Tmavě hnědé vlasy nahoře
        pygame.draw.rect(surf, (80, 40, 0), (6, 3, 3, 5))             # Vlasy vlevo
        pygame.draw.rect(surf, (80, 40, 0), (19, 3, 3, 4))            # Vlasy vpravo
        pygame.draw.rect(surf, (100, 50, 0), (8, 0, 12, 2), border_radius=1)  # Světlejší odlesk na vlasech

        # Oči
        pygame.draw.rect(surf, (255, 255, 255), (9, 6, 4, 4), border_radius=1)   # Levé bělmo
        pygame.draw.rect(surf, (255, 255, 255), (15, 6, 4, 4), border_radius=1)  # Pravé bělmo
        pygame.draw.rect(surf, (20, 20, 30), (10, 7, 2, 2))           # Levá zornička
        pygame.draw.rect(surf, (20, 20, 30), (16, 7, 2, 2))           # Pravá zornička

        # Přední ruka (před tělem)
        arm2_y = 12 - (1 if is_walking and step in [0, 1] else 0)     # Přední ruka se pohybuje opačně k zadní
        pygame.draw.rect(surf, (0, 120, 255), (20, arm2_y, 4, 7), border_radius=2)    # Rukáv (světle modrý)
        pygame.draw.rect(surf, (255, 224, 189), (20, arm2_y + 5, 4, 3), border_radius=1)  # Ruka (kůže)

    # ---- VYTVOŘENÍ ANIMAČNÍCH FRAMŮ ----
    def create_idle_frames(self):                      # Vytvoří 2 framy pro stojící postavu
        frames = []                                    # Prázdný seznam framů
        for i in range(2):                             # 2 framy
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Průhledná surface
            self.draw_player_base(surf)                # Vykreslí základní postavu
            if i == 1:                                 # Druhý frame
                surf.scroll(0, 1)                      # Posune o 1 pixel dolů – simulace dýchání
            frames.append(surf)                        # Přidá frame do seznamu
        return frames                                  # Vrátí seznam framů

    def create_walk_frames(self):                      # Vytvoří 4 framy pro chůzi
        frames = []                                    # Prázdný seznam framů
        for i in range(4):                             # 4 kroky animace
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Průhledná surface
            self.draw_player_base(surf, is_walking=True, step=i)  # Vykreslí postavu v daném kroku chůze
            frames.append(surf)                        # Přidá frame
        return frames                                  # Vrátí 4 framy

    def create_attack_frames(self):                    # Vytvoří 1 frame pro útok
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Průhledná surface
        self.draw_player_base(surf)                    # Základní postava
        # Meč – čepel
        pygame.draw.line(surf, (160, 160, 170), (16, 16), (27, 2), 4)   # Tmavá čepel (šedá šikmá čára)
        pygame.draw.line(surf, (255, 255, 255), (16, 16), (26, 3), 2)   # Bílý odlesk na čepeli
        # Záštita meče (křížový kus)
        pygame.draw.polygon(surf, (218, 165, 32), [(14, 13), (18, 17), (16, 19), (12, 15)])  # Zlatý polygon
        # Rukojeť
        pygame.draw.line(surf, (139, 69, 19), (15, 16), (11, 20), 3)    # Hnědá čára
        # Hlavice meče
        pygame.draw.circle(surf, (255, 215, 0), (11, 20), 2)            # Zlatý kroužek na konci rukojeti
        return [surf]                                  # Vrátí seznam s 1 framem

    def create_death_frames(self):                     # Vytvoří 10 framů pro animaci smrti
        frames = []                                    # Prázdný seznam
        base_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Základní surface
        self.draw_player_base(base_surf)               # Základní postava
        for i in range(10):                            # 10 kroků animace
            surf = base_surf.copy()                    # Kopie základní postavy
            # Překryje oči černou
            pygame.draw.rect(surf, (0, 0, 0), (9, 6, 4, 4))    # Levé oko – černé
            pygame.draw.rect(surf, (0, 0, 0), (15, 6, 4, 4))   # Pravé oko – černé
            # Křížky místo očí (červené X)
            pygame.draw.line(surf, (255, 0, 0), (9, 6), (12, 9), 2)     # Levý křížek \
            pygame.draw.line(surf, (255, 0, 0), (12, 6), (9, 9), 2)     # Levý křížek /
            pygame.draw.line(surf, (255, 0, 0), (15, 6), (18, 9), 2)    # Pravý křížek \
            pygame.draw.line(surf, (255, 0, 0), (18, 6), (15, 9), 2)    # Pravý křížek /
            surf = pygame.transform.rotate(surf, -i * 10)  # Postupná rotace (0°, -10°, -20°, ... -90°)
            surf.set_alpha(max(0, 255 - i * 20))       # Postupné průhlednutí (255 → 75)
            frames.append(surf)                        # Přidá frame
        return frames                                  # Vrátí 10 framů

    # ---- OVLÁDÁNÍ HRÁČE ----
    def handle_input(self, camera=None):               # Zpracování vstupu z klávesnice a myši
        keys = pygame.key.get_pressed()                # Získá stav všech kláves (True = stisknuta)

        if self.knockback_timer > 0:                   # Pokud právě probíhá knockback (odskok)
            self.knockback_timer -= 1                  # Snížení časovače knockbacku
            self.vel_x *= 0.85                         # Zpomalení X rychlosti (tření)
            self.vel_y *= 0.85                         # Zpomalení Y rychlosti (tření)
        else:                                          # Normální ovládání (žádný knockback)
            self.vel_x = 0                             # Resetuje horizontální rychlost
            self.vel_y = 0                             # Resetuje vertikální rychlost

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:    # Šipka doleva nebo A
                self.vel_x = -PLAYER_SPEED             # Pohyb doleva
                if not self.attacking:                 # Neotáčíme se během útoku
                    self.facing_right = False           # Otočení doleva
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:   # Šipka doprava nebo D
                self.vel_x = PLAYER_SPEED              # Pohyb doprava
                if not self.attacking:                 # Neotáčíme se během útoku
                    self.facing_right = True            # Otočení doprava
            if keys[pygame.K_UP] or keys[pygame.K_w]:      # Šipka nahoru nebo W
                self.vel_y = -PLAYER_SPEED             # Pohyb nahoru
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:    # Šipka dolů nebo S
                self.vel_y = PLAYER_SPEED              # Pohyb dolů

            # Normalizace diagonálního pohybu
            if self.vel_x != 0 and self.vel_y != 0:    # Pokud se hráč pohybuje diagonálně
                inv = 1 / math.sqrt(2)                 # Koeficient pro normalizaci (1/√2 ≈ 0.707)
                self.vel_x *= inv                      # Zpomalení X (aby diagonální rychlost nebyla √2× větší)
                self.vel_y *= inv                      # Zpomalení Y

        # Automatický útok (spouští se sám, pokud cooldown vypršel)
        if self.attack_cooldown <= 0:                  # Pokud cooldown skončil
            self.attacking = True                      # Začne útok
            self.attack_timer = ATTACK_DURATION        # Nastaví délku útoku
            self.attack_cooldown = BASE_ATTACK_COOLDOWN  # Resetuje cooldown
            self.hit_enemies.clear()                   # Vyčistí seznam zasažených nepřátel

            if camera:                                 # Pokud máme referenci na kameru
                mx, my = pygame.mouse.get_pos()        # Získá pozici myši na obrazovce
                # Přepočet pozice myši na světové souřadnice (s korekcí na zoom)
                world_mx = (mx / ZOOM) - camera.rect.x    # Světová X pozice myši
                world_my = (my / ZOOM) - camera.rect.y    # Světová Y pozice myši
                dx = world_mx - self.rect.centerx      # Rozdíl X od hráče k myši
                dy = world_my - self.rect.centery      # Rozdíl Y od hráče k myši
                self.attack_angle = math.degrees(math.atan2(dy, dx))  # Úhel útoku ve stupních (atan2 vrací radiány → převod)
                self.facing_right = dx >= 0            # Otočení hráče podle myši
            else:                                      # Bez kamery
                self.attack_angle = 0 if self.facing_right else 180  # Útok doprava (0°) nebo doleva (180°)

    # ---- POHYB A KOLIZE ----
    def move(self, blocks):                            # Pohyb hráče s detekcí kolizí
        self.rect.x += self.vel_x                      # Posun po ose X
        self.collide(self.vel_x, 0, blocks)            # Kontrola kolize na ose X
        self.rect.y += self.vel_y                      # Posun po ose Y
        self.collide(0, self.vel_y, blocks)            # Kontrola kolize na ose Y

    def collide(self, vel_x, vel_y, blocks):           # Řeší kolizi se stěnami
        for block in blocks:                           # Projde všechny bloky (stěny)
            if self.rect.colliderect(block.rect):      # Pokud se hráč překrývá s blokem
                if vel_x > 0:                          # Pohyb doprava → narazil pravou stranou
                    self.rect.right = block.rect.left  # Zastaví na levé hraně bloku
                    self.vel_x = 0                     # Vynuluje horizontální rychlost
                elif vel_x < 0:                        # Pohyb doleva → narazil levou stranou
                    self.rect.left = block.rect.right  # Zastaví na pravé hraně bloku
                    self.vel_x = 0                     # Vynuluje horizontální rychlost
                if vel_y > 0:                          # Pohyb dolů → narazil spodkem
                    self.rect.bottom = block.rect.top  # Zastaví na horní hraně bloku
                    self.vel_y = 0                     # Vynuluje vertikální rychlost
                elif vel_y < 0:                        # Pohyb nahoru → narazil vrchu
                    self.rect.top = block.rect.bottom  # Zastaví na dolní hraně bloku
                    self.vel_y = 0                     # Vynuluje vertikální rychlost

    # ---- HLAVNÍ UPDATE HRÁČE ----
    def update(self, blocks, camera=None):             # Hlavní update volaný každý snímek
        if self.is_dead():                             # Pokud je hráč mrtvý
            self.vel_x = 0                             # Zastaví pohyb X
            self.vel_y = 0                             # Zastaví pohyb Y
            self.current_animation = 'death'           # Přepne na animaci smrti
            frames = self.animation_frames[self.current_animation]  # Získá framy smrti
            if int(self.frame_index) < len(frames) - 1:    # Pokud ještě není na posledním framu
                self.frame_index += self.animation_speed   # Posune animaci dál
            self.image = frames[int(self.frame_index)] # Nastaví aktuální obrázek
            return                                     # Ukončí update (mrtvý hráč nic jiného nedělá)

        self.handle_input(camera)                      # Zpracuje vstup z klávesnice/myši
        self.move(blocks)                              # Provede pohyb s kolizemi

        # Aktualizace útoku a cooldownu
        if self.attacking:                             # Pokud probíhá útok
            self.attack_timer -= 1                     # Sníží časovač útoku
            if self.attack_timer <= 0:                 # Pokud útok skončil
                self.attacking = False                 # Ukončí útok
        if self.attack_cooldown > 0:                   # Pokud běží cooldown
            self.attack_cooldown -= 1                  # Sníží cooldown

        if self.hit_cooldown > 0:                      # Pokud běží imunita po zásahu
            self.hit_cooldown -= 1                     # Sníží imunitu

        # Damage boost timer
        if self.damage_boost_timer > 0:                # Pokud je aktivní damage boost
            self.damage_boost_timer -= 1               # Sníží timer
            if self.damage_boost_timer <= 0:           # Pokud boost vypršel
                self.damage_boost = 1                  # Resetuje násobič na 1 (normální)

        # Výběr animace podle stavu
        if self.attacking:                             # Útok má prioritu
            self.current_animation = 'attack'          # Animace útoku
        elif self.vel_x != 0 or self.vel_y != 0:      # Pokud se hráč pohybuje
            self.current_animation = 'walk'            # Animace chůze
        else:                                          # Stojí na místě
            self.current_animation = 'idle'            # Animace stání (dýchání)

        # Aktualizace animačního framu
        frames = self.animation_frames[self.current_animation]  # Získá framy aktuální animace
        self.frame_index = (self.frame_index + self.animation_speed) % len(frames)  # Cyklické procházení framů
        self.image = frames[int(self.frame_index)]     # Nastaví aktuální obrázek

        # Otočení sprite podle směru
        if not self.facing_right:                      # Pokud hráč míří doleva
            self.image = pygame.transform.flip(self.image, True, False)  # Horizontální převrácení obrázku

    # ---- KONTROLA ZASAŽENÍ ÚTOKEM ----
    def point_in_swing(self, px, py):                  # Zkontroluje, zda bod (px, py) je v oblouku švihu
        ox, oy = self.rect.center                      # Střed hráče (počátek švihu)
        dx = px - ox                                   # Rozdíl X od hráče k bodu
        dy = py - oy                                   # Rozdíl Y od hráče k bodu
        dist = math.hypot(dx, dy)                      # Vzdálenost bod od hráče
        if dist > ATTACK_SIZE * 2:                     # Pokud je bod příliš daleko
            return False                               # Není v dosahu
        ang = math.degrees(math.atan2(dy, dx))         # Úhel od hráče k bodu (ve stupních)
        diff = (ang - self.attack_angle + 180) % 360 - 180  # Rozdíl úhlů (-180 až +180)
        return abs(diff) <= 90                         # True pokud je rozdíl do ±90° (polokruh švihu)

    def attack_hits(self, enemy):                      # Zkontroluje, zda útok zasáhl nepřítele
        if not self.attacking:                         # Pokud neútočíme
            return False                               # Nemůže zasáhnout
        ox, oy = self.rect.center                      # Střed hráče
        ex, ey = enemy.rect.center                     # Střed nepřítele
        dist = math.hypot(ex - ox, ey - oy)            # Vzdálenost hráč-nepřítel
        if dist > ATTACK_SIZE * 2:                     # Pokud je nepřítel moc daleko
            return False                               # Mimo dosah
        return self.point_in_swing(ex, ey)             # Zkontroluje úhel švihu

    # ---- VYKRESLENÍ EFEKTU ÚTOKU ----
    def draw_attack(self, screen, camera):             # Vykreslí srpkovitý slash efekt na obrazovku
        if self.attacking:                             # Pouze pokud probíhá útok
            center = camera.apply(self).center         # Střed hráče na obrazovce (po aplikaci kamery)
            arc_radius = ATTACK_SIZE * 1.5             # Poloměr oblouku útoku (60 px)

            surf_size = int(arc_radius * 3)            # Velikost surface pro vykreslení (180×180)
            swoosh_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)  # Průhledná surface

            progress = 1.0 - (self.attack_timer / ATTACK_DURATION)  # Průběh útoku (0.0 → 1.0)

            visual_attack_angle = -self.attack_angle   # Invertovaný úhel (pygame Y osa je opačně)
            start_deg = visual_attack_angle - 100      # Počáteční úhel oblouku

            swing_extent = 200                         # Celkový rozsah švihu ve stupních
            current_extent = swing_extent * progress   # Aktuální rozsah podle průběhu
            end_deg = start_deg + current_extent       # Koncový úhel

            points_outer = []                          # Body vnějšího oblouku
            points_inner = []                          # Body vnitřního oblouku

            scx = surf_size // 2                       # X střed surface
            scy = surf_size // 2                       # Y střed surface

            segments = max(5, int(current_extent / 10))    # Počet segmentů oblouku (min 5)
            if segments > 0 and current_extent > 0:        # Pokud je co kreslit
                for i in range(segments + 1):              # Pro každý segment + koncový bod
                    t = i / segments                       # Parametr t od 0 do 1
                    angle_deg = start_deg + t * current_extent  # Aktuální úhel
                    angle_rad = math.radians(angle_deg)    # Převod na radiány

                    thickness_factor = math.sin(t * math.pi)   # Sin profil – tloušťka se rozšiřuje uprostřed a zužuje na koncích

                    current_thickness = arc_radius * 0.4 * thickness_factor  # Skutečná tloušťka srpku

                    # Vnější oblouk
                    ox = scx + math.cos(angle_rad) * arc_radius     # X bod vnějšího oblouku
                    oy = scy + math.sin(angle_rad) * arc_radius     # Y bod vnějšího oblouku
                    points_outer.append((ox, oy))                   # Přidá bod

                    # Vnitřní oblouk
                    ix = scx + math.cos(angle_rad) * (arc_radius - current_thickness)  # X bod vnitřního oblouku
                    iy = scy + math.sin(angle_rad) * (arc_radius - current_thickness)  # Y bod vnitřního oblouku
                    points_inner.append((ix, iy))                   # Přidá bod

                points_inner.reverse()                 # Obrátí pořadí vnitřních bodů (polygon musí být uzavřený)
                slash_polygon = points_outer + points_inner  # Spojí vnější + vnitřní body do polygonu

                # Barva podle stavu damage boostu
                base_color = (100, 200, 255)           # Normální barva: cyan/modrá
                if getattr(self, 'damage_boost_timer', 0) > 0:  # Pokud je aktivní boost
                    base_color = (255, 100, 50)        # Boost barva: oranžová/zlatá

                alpha_glow = max(0, int(200 * (1 - progress)))  # Průhlednost záře (fade out s průběhem)
                pygame.draw.polygon(swoosh_surf, (*base_color, alpha_glow), slash_polygon)  # Vykreslí hlavní slash polygon

                # Bílý střed srpku – ostřejší hrana
                points_core_outer = []                 # Vnější body jádra
                points_core_inner = []                 # Vnitřní body jádra
                for i in range(segments + 1):          # Stejný počet segmentů
                    t = i / segments                   # Parametr 0-1
                    angle_deg = start_deg + t * current_extent  # Úhel
                    angle_rad = math.radians(angle_deg)          # Radiány
                    thickness_factor = math.sin(t * math.pi)     # Sin profil

                    core_thickness = arc_radius * 0.15 * thickness_factor  # Tenčí jádro (15% vs 40%)

                    ox = scx + math.cos(angle_rad) * (arc_radius - 2)  # Vnější bod (o 2 px menší)
                    oy = scy + math.sin(angle_rad) * (arc_radius - 2)
                    ix = scx + math.cos(angle_rad) * (arc_radius - 2 - core_thickness)  # Vnitřní bod
                    iy = scy + math.sin(angle_rad) * (arc_radius - 2 - core_thickness)

                    points_core_outer.append((ox, oy))     # Přidá vnější bod jádra
                    points_core_inner.insert(0, (ix, iy))  # Přidá vnitřní bod na začátek (obrácené pořadí)

                core_polygon = points_core_outer + points_core_inner  # Polygon jádra
                alpha_core = max(0, min(255, int(255 * (1.2 - progress))))  # Průhlednost jádra
                pygame.draw.polygon(swoosh_surf, (255, 255, 255, alpha_core), core_polygon)  # Bílé jádro

            screen.blit(swoosh_surf, swoosh_surf.get_rect(center=center))  # Vykreslí slash na obrazovku (centrovaný na hráče)

    # ---- ZDRAVÍ ----
    def take_damage(self, amount):                     # Hráč dostane poškození
        self.health -= amount                          # Odečte životy
        if self.health < 0:                            # Životy nesmí být záporné
            self.health = 0                            # Minimum je 0

    def heal(self, amount):                            # Hráč se vyléčí
        self.health = min(self.health + amount, self.max_health)  # Přidá životy, max je max_health

    # ---- XP A LEVEL UP ----
    def add_xp(self, amount):                          # Přidá zkušenostní body
        self.xp += amount                              # Zvýší XP
        while self.xp >= self.max_xp:                  # Cyklus – může přeskočit víc levelů najednou
            self.xp -= self.max_xp                     # Odečte potřebné XP
            self.level += 1                            # Zvýší level
            self.max_xp = int(self.max_xp * 1.5)      # Další level potřebuje 1.5× více XP
            self.level_up_pending += 1                 # Přidá čekající level-up (zobrazí upgrade menu)

    def is_dead(self):                                 # Kontrola, zda je hráč mrtvý
        return self.health <= 0                        # True pokud zdraví je 0 nebo méně


# =============================================================================
# TŘÍDA ENEMY (NEPŘÍTEL)
# Rodičovská třída pro 5 typů nepřátel: walker, flying, tank, fast, boss.
# Každý typ má jiné zdraví, rychlost, poškození a vizuál.
# =============================================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type='walker'):     # Konstruktor – pozice a typ nepřítele
        super().__init__()                             # Volání konstruktoru Sprite
        self.enemy_type = enemy_type                   # Typ nepřítele ('walker', 'flying', 'tank', 'fast', 'boss')
        self.width = ENEMY_SIZE * 2 if enemy_type == 'boss' else ENEMY_SIZE    # Boss je 2× větší (56 px)
        self.height = ENEMY_SIZE * 2 if enemy_type == 'boss' else ENEMY_SIZE   # Boss je 2× větší
        self.rect = pygame.Rect(x, y, self.width, self.height)  # Obdélník nepřítele ve světě
        self.vel_x = 0                                 # Horizontální rychlost
        self.vel_y = 0                                 # Vertikální rychlost

        # Statistiky podle typu nepřítele
        if self.enemy_type == 'walker':                # Walker – slime/zombie
            self.health = 30                           # 30 HP
            self.xp_value = 5                          # Dá 5 XP při zabití
            self.speed = ENEMY_SPEED                   # Normální rychlost (2)
            self.damage = 15                           # Udělí 15 poškození
        elif self.enemy_type == 'flying':              # Flying – netopýr
            self.health = 20                           # 20 HP (méně)
            self.xp_value = 5                          # Dá 5 XP
            self.speed = FLYING_ENEMY_SPEED            # Pomalejší (1)
            self.damage = 10                           # 10 poškození
        elif self.enemy_type == 'tank':                # Tank – golem
            self.health = 100                          # 100 HP (hodně)
            self.xp_value = 15                         # Dá 15 XP (více)
            self.speed = ENEMY_SPEED * 0.6             # Pomalý (1.2)
            self.damage = 30                           # 30 poškození (hodně)
        elif self.enemy_type == 'fast':                # Fast – duch/oko
            self.health = 10                           # 10 HP (málo)
            self.xp_value = 5                          # Dá 5 XP
            self.speed = ENEMY_SPEED * 1.5             # Rychlý (3)
            self.damage = 5                            # 5 poškození (málo)
        elif self.enemy_type == 'boss':                # Boss – velký nepřítel
            self.health = 500                          # 500 HP (extrémně)
            self.xp_value = 150                        # Dá 150 XP (hodně)
            self.speed = ENEMY_SPEED * 0.8             # Mírně pomalejší (1.6)
            self.damage = 40                           # 40 poškození
        else:                                          # Záložní hodnoty (nikdy by nemělo nastat)
            self.health = 30                           # Default 30 HP
            self.xp_value = 5                          # Default 5 XP
            self.speed = ENEMY_SPEED                   # Default rychlost
            self.damage = 15                           # Default poškození

        self.facing_right = random.choice([True, False])   # Náhodný počáteční směr
        self.hit_flash = 0                             # Časovač blikání při zásahu (snímky)
        self.knockback_timer = 0                       # Časovač knockbacku (odskok)

        # Vytvoření vizuálu
        self.image = pygame.Surface((self.width, self.height))     # Surface pro obrázek
        self.draw_enemy()                              # Vykreslí tvar nepřítele

    def draw_enemy(self):                              # Vykreslí grafiku nepřítele podle typu
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Průhledná surface
        self.image.fill((0, 0, 0, 0))                  # Průhledné pozadí
        pygame.draw.ellipse(self.image, (0, 0, 0, 80), (4, 24, 20, 6))  # Stín pod nepřítelem

        if self.enemy_type == 'walker':                # Walker – zelený slime
            pygame.draw.rect(self.image, (34, 139, 34), (4, 8, 20, 18), border_radius=6)      # Zelené tělo
            pygame.draw.rect(self.image, (0, 100, 0), (4, 8, 20, 18), 2, border_radius=6)     # Tmavší okraj
            pygame.draw.circle(self.image, (255, 0, 0), (10, 14), 3)   # Levé červené oko
            pygame.draw.circle(self.image, (255, 0, 0), (18, 14), 3)   # Pravé červené oko
            pygame.draw.rect(self.image, (0, 0, 0), (10, 20, 8, 2))    # Ústa (černý obdélníček)

        elif self.enemy_type == 'flying':              # Flying – fialový netopýr
            pygame.draw.circle(self.image, (75, 0, 130), (14, 14), 8)  # Tělo (fialový kruh)
            pygame.draw.polygon(self.image, (138, 43, 226), [(6, 14), (-4, 4), (2, 20)])    # Levé křídlo
            pygame.draw.polygon(self.image, (138, 43, 226), [(22, 14), (32, 4), (26, 20)])  # Pravé křídlo
            pygame.draw.circle(self.image, YELLOW, (11, 12), 2)        # Levé žluté oko
            pygame.draw.circle(self.image, YELLOW, (17, 12), 2)        # Pravé žluté oko

        elif self.enemy_type == 'tank':                # Tank – šedý golem
            pygame.draw.rect(self.image, (105, 105, 105), (2, 4, 24, 24), border_radius=4)    # Šedé tělo
            pygame.draw.rect(self.image, (50, 50, 50), (2, 4, 24, 24), 3, border_radius=4)    # Tmavší okraj
            pygame.draw.circle(self.image, (255, 165, 0), (10, 10), 4)  # Levé oranžové oko
            pygame.draw.circle(self.image, (255, 165, 0), (18, 10), 4)  # Pravé oranžové oko
            pygame.draw.rect(self.image, (0, 0, 0), (8, 18, 12, 4))    # Ústa

        elif self.enemy_type == 'fast':                # Fast – průsvitný duch/oko
            pygame.draw.circle(self.image, (200, 200, 255, 180), (14, 14), 10)  # Světle modrý kruh (poloprůhledný)
            pygame.draw.circle(self.image, (255, 0, 0), (14, 14), 4)   # Červená duhovka
            pygame.draw.circle(self.image, (0, 0, 0), (14, 14), 2)     # Černá zornička

        elif self.enemy_type == 'boss':                # Boss – velký červený nepřítel
            pygame.draw.rect(self.image, (150, 0, 0), (4, 4, self.width-8, self.height-8), border_radius=8)   # Červené tělo
            pygame.draw.rect(self.image, (50, 0, 0), (4, 4, self.width-8, self.height-8), 4, border_radius=8)  # Tmavší okraj
            pygame.draw.circle(self.image, (255, 255, 0), (self.width//3, self.height//3), 6)    # Levé žluté oko
            pygame.draw.circle(self.image, (255, 255, 0), (2*self.width//3, self.height//3), 6)  # Pravé žluté oko
            pygame.draw.rect(self.image, (0, 0, 0), (self.width//4, 2*self.height//3, self.width//2, 8))  # Ústa

        # Vytvoření bílé masky pro hit flash efekt
        mask = pygame.mask.from_surface(self.image)    # Vytvoří masku z obrázku (pixely vs. průhlednost)
        self.flash_image = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))  # Bílá verze pro blikání

    # ---- POHYB A KOLIZE NEPŘÍTELE ----
    def move(self, blocks):                            # Pohyb nepřítele
        self.rect.x += self.vel_x                      # Posun X
        self.collide(self.vel_x, 0, blocks)            # Kolize X
        self.rect.y += self.vel_y                      # Posun Y
        self.collide(0, self.vel_y, blocks)            # Kolize Y

    def collide(self, vel_x, vel_y, blocks):           # Kolize nepřítele se stěnami
        for block in blocks:                           # Projde všechny bloky
            if self.rect.colliderect(block.rect):      # Pokud se překrývají
                if vel_x > 0:                          # Šel doprava
                    self.rect.right = block.rect.left  # Zastaví
                    self.vel_x = -self.speed            # OBRÁTÍ SMĚR (nepřítel se odrazí, na rozdíl od hráče!)
                    self.facing_right = False           # Otočí se doleva
                elif vel_x < 0:                        # Šel doleva
                    self.rect.left = block.rect.right  # Zastaví
                    self.vel_x = self.speed             # Obrátí směr
                    self.facing_right = True            # Otočí se doprava
                if vel_y > 0:                          # Šel dolů
                    self.rect.bottom = block.rect.top  # Zastaví
                    self.vel_y = -self.speed            # Obrátí směr
                elif vel_y < 0:                        # Šel nahoru
                    self.rect.top = block.rect.bottom  # Zastaví
                    self.vel_y = self.speed             # Obrátí směr

    # ---- UPDATE NEPŘÍTELE ----
    def update(self, blocks, player=None):             # Hlavní update nepřítele
        if self.hit_flash > 0:                         # Pokud běží hit flash efekt
            self.hit_flash -= 1                        # Sníží časovač blikání

        if self.knockback_timer > 0:                   # Pokud běží knockback
            self.knockback_timer -= 1                  # Sníží časovač
            self.vel_x *= 0.85                         # Zpomalení X (tření)
            self.vel_y *= 0.85                         # Zpomalení Y (tření)
        elif self.enemy_type in ['walker', 'tank', 'fast', 'boss']:  # Pozemní nepřátelé
            if player:                                 # Pokud existuje hráč
                dx = player.rect.centerx - self.rect.centerx   # Vzdálenost X k hráči
                dy = player.rect.centery - self.rect.centery   # Vzdálenost Y k hráči
                dist = math.hypot(dx, dy)              # Přímá vzdálenost (Pythagoras)
                if dist != 0:                          # Ochrana proti dělení nulou
                    self.vel_x = (dx / dist) * self.speed  # Normalizovaný směr × rychlost (X)
                    self.vel_y = (dy / dist) * self.speed  # Normalizovaný směr × rychlost (Y)
                else:                                  # Stojí přímo na hráči
                    self.vel_x, self.vel_y = 0, 0      # Nehýbe se
            else:                                      # Bez hráče – patrola
                if self.facing_right:                  # Jde doprava
                    self.vel_x = self.speed            # Pohyb doprava
                else:                                  # Jde doleva
                    self.vel_x = -self.speed           # Pohyb doleva
                self.vel_y = 0                         # Žádný vertikální pohyb

        elif self.enemy_type == 'flying':              # Létající nepřítel
            if player:                                 # Pokud existuje hráč
                dx = player.rect.centerx - self.rect.centerx   # Vzdálenost X
                dy = player.rect.centery - self.rect.centery   # Vzdálenost Y
                dist = math.hypot(dx, dy)              # Přímá vzdálenost
                if dist != 0:                          # Ochrana proti dělení nulou
                    self.vel_x = (dx / dist) * self.speed  # Směr k hráči (X)
                    self.vel_y = (dy / dist) * self.speed  # Směr k hráči (Y)
                else:                                  # Na hráči
                    self.vel_x = 0                     # Stojí
                    self.vel_y = 0                     # Stojí

        self.move(blocks)                              # Provede pohyb s kolizemi

    # ---- POŠKOZENÍ A KNOCKBACK ----
    def take_damage(self, amount):                     # Nepřítel dostane poškození
        self.health -= amount                          # Odečte zdraví
        self.hit_flash = 6                             # Zapne blikající bílý efekt na 6 snímků

    def apply_knockback(self, source_rect):            # Aplikuje odskok od zdroje poškození
        dx = self.rect.centerx - source_rect.centerx   # Směr odskoku X (od hráče)
        dy = self.rect.centery - source_rect.centery   # Směr odskoku Y (od hráče)
        dist = math.hypot(dx, dy)                      # Vzdálenost
        if dist != 0:                                  # Ochrana proti dělení nulou
            kb_strength = 12.0                         # Výchozí síla knockbacku
            if self.enemy_type == 'tank':              # Tank je odolný
                kb_strength = 4.0                      # Menší knockback
            elif self.enemy_type == 'fast':            # Fast je lehký
                kb_strength = 16.0                     # Větší knockback
            elif self.enemy_type == 'boss':            # Boss je těžký
                kb_strength = 1.0                      # Minimální knockback
            self.vel_x = (dx / dist) * kb_strength     # Rychlost odskoku (X)
            self.vel_y = (dy / dist) * kb_strength     # Rychlost odskoku (Y)
            self.knockback_timer = 15                  # Knockback trvá 15 snímků

    def is_dead(self):                                 # Kontrola smrti nepřítele
        return self.health <= 0                        # True pokud HP ≤ 0


# =============================================================================
# GENERÁTOR DUNGEONU
# Vytváří herní svět – mřížku místností s kamennými stěnami po obvodu.
# =============================================================================
def generate_dungeon(size):                            # Parametr size = velikost mřížky (5 = 5×5 místností)
    rooms: List[RoomDict] = []                         # Prázdný seznam místností
    for i in range(size):                              # Pro každý sloupec mřížky
        for j in range(size):                          # Pro každý řádek mřížky
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)   # Náhodná šířka místnosti (v blocích)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)   # Náhodná výška místnosti (v blocích)
            x = i * (ROOM_MAX_SIZE + 2) * BLOCK_SIZE   # X pozice místnosti (s mezerami)
            y = j * (ROOM_MAX_SIZE + 2) * BLOCK_SIZE   # Y pozice místnosti (s mezerami)
            rooms.append({                             # Přidá místnost do seznamu
                'x': x, 'y': y,                       # Pozice
                'width': w * BLOCK_SIZE,               # Šířka v pixelech
                'height': h * BLOCK_SIZE,              # Výška v pixelech
                'grid_x': i, 'grid_y': j,             # Pozice v mřížce
                'doors': []                            # Prázdný seznam dveří
            })

    # Propojení místností – každá se připojí k pravému a dolnímu sousedovi
    for room in rooms:                                 # Pro každou místnost
        # Pravý soused
        right_room = next((r for r in rooms if r['grid_x'] == room['grid_x']+1 and r['grid_y'] == room['grid_y']), None)  # Hledá souseda vpravo
        if right_room:                                 # Pokud existuje
            door_y = room['y'] + ((room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE  # Y pozice dveří (uprostřed)
            door1 = (room['x'] + room['width'] - BLOCK_SIZE, door_y)   # Dveře v aktuální místnosti
            door2 = (right_room['x'], right_room['y'] + ((right_room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE)  # Dveře v sousedovi
            room['doors'].append(door1)                # Přidá dveře
            right_room['doors'].append(door2)          # Přidá dveře sousedovi

        # Dolní soused
        down_room = next((r for r in rooms if r['grid_x'] == room['grid_x'] and r['grid_y'] == room['grid_y']+1), None)  # Hledá souseda dole
        if down_room:                                  # Pokud existuje
            door_x = room['x'] + ((room['width'] // 2) // BLOCK_SIZE) * BLOCK_SIZE  # X pozice dveří (uprostřed)
            door1 = (door_x, room['y'] + room['height'] - BLOCK_SIZE)  # Dveře v aktuální místnosti
            door2 = (door_x, down_room['y'])           # Dveře v sousedovi
            room['doors'].append(door1)                # Přidá dveře
            down_room['doors'].append(door2)           # Přidá dveře sousedovi

    # Vytvoření kamenných stěn po obvodu herního světa
    blocks = pygame.sprite.Group()                     # Sprite group pro všechny bloky
    placed = set()                                     # Množina již umístěných pozic (prevence duplikátů)

    # Výpočet hranic světa
    min_x = min(room['x'] for room in rooms)           # Nejlevější bod
    min_y = min(room['y'] for room in rooms)           # Nejvyšší bod
    max_x = max(room['x'] + room['width'] for room in rooms)   # Nejpravější bod
    max_y = max(room['y'] + room['height'] for room in rooms)  # Nejnižší bod

    # Vodorovné stěny (horní a dolní okraj)
    y_top = min_y - BLOCK_SIZE                         # Pozice horní stěny (1 blok nad světem)
    y_bottom = max_y + BLOCK_SIZE                      # Pozice dolní stěny (1 blok pod světem)
    for bx in range(min_x - BLOCK_SIZE, max_x + 2*BLOCK_SIZE, BLOCK_SIZE):  # Od levé do pravé strany
        blocks.add(Block(bx, y_top, 'stone'))          # Horní stěna – kamenný blok
        placed.add((bx, y_top))                        # Zapamatuje pozici
        blocks.add(Block(bx, y_bottom, 'stone'))       # Dolní stěna – kamenný blok
        placed.add((bx, y_bottom))                     # Zapamatuje pozici

    # Svislé stěny (levý a pravý okraj)
    x_left = min_x - BLOCK_SIZE                        # Pozice levé stěny
    x_right = max_x + BLOCK_SIZE                       # Pozice pravé stěny
    for by in range(min_y - BLOCK_SIZE, max_y + 2*BLOCK_SIZE, BLOCK_SIZE):  # Od horní strany dolů
        blocks.add(Block(x_left, by, 'stone'))         # Levá stěna
        placed.add((x_left, by))                       # Zapamatuje
        blocks.add(Block(x_right, by, 'stone'))        # Pravá stěna
        placed.add((x_right, by))                      # Zapamatuje

    # Doplnění případných mezer ve stěnách (pojistka)
    for bx in range(min_x - BLOCK_SIZE, max_x + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE):  # Vodorovné doplnění
        for by in [min_y - BLOCK_SIZE, max_y + BLOCK_SIZE]:  # Horní a dolní řada
            if (bx, by) not in placed:                 # Pokud tam ještě není blok
                blocks.add(Block(bx, by, 'stone'))     # Přidá kamenný blok
                placed.add((bx, by))                   # Zapamatuje

    for by in range(min_y - BLOCK_SIZE, max_y + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE):  # Svislé doplnění
        for bx in [min_x - BLOCK_SIZE, max_x + BLOCK_SIZE]:  # Levý a pravý sloupec
            if (bx, by) not in placed:                 # Pokud tam ještě není blok
                blocks.add(Block(bx, by, 'stone'))     # Přidá kamenný blok
                placed.add((bx, by))                   # Zapamatuje

    items = pygame.sprite.Group()                      # Prázdná sprite group pro předměty

    return blocks, items, rooms                        # Vrátí stěny, předměty a seznam místností


# =============================================================================
# FUNKCE SPAWN_AT_SCREEN_EDGE
# Vrátí náhodnou pozici za okrajem kamery pro spawn nepřátel.
# =============================================================================
def spawn_at_screen_edge(camera, offset):              # Parametr offset = vzdálenost za okrajem
    """Vrátí náhodnou pozici za okrajem kamery."""
    cam_x = -camera.rect.x                            # Levý okraj kamery ve světových souřadnicích
    cam_y = -camera.rect.y                            # Horní okraj kamery ve světových souřadnicích
    cam_w = int(WINDOW_WIDTH / ZOOM)                   # Šířka viditelné oblasti
    cam_h = int(WINDOW_HEIGHT / ZOOM)                  # Výška viditelné oblasti
    edge = random.randint(0, 3)                        # Náhodná hrana (0=horní, 1=pravá, 2=dolní, 3=levá)
    if edge == 0:                                      # Horní hrana
        sx = random.randint(cam_x - offset, cam_x + cam_w + offset)  # Náhodné X podél horní hrany
        sy = cam_y - offset                            # Y nad horní hranou
    elif edge == 1:                                    # Pravá hrana
        sx = cam_x + cam_w + offset                    # X za pravou hranou
        sy = random.randint(cam_y - offset, cam_y + cam_h + offset)  # Náhodné Y
    elif edge == 2:                                    # Dolní hrana
        sx = random.randint(cam_x - offset, cam_x + cam_w + offset)  # Náhodné X
        sy = cam_y + cam_h + offset                    # Y pod dolní hranou
    else:                                              # Levá hrana
        sx = cam_x - offset                            # X před levou hranou
        sy = random.randint(cam_y - offset, cam_y + cam_h + offset)  # Náhodné Y
    sx = max(BLOCK_SIZE, min(sx, WORLD_WIDTH_PX - BLOCK_SIZE))   # Omezení X na hranice světa
    sy = max(BLOCK_SIZE, min(sy, WORLD_HEIGHT_PX - BLOCK_SIZE))  # Omezení Y na hranice světa
    return sx, sy                                      # Vrátí souřadnice pro spawn


# =============================================================================
# FUNKCE SHOW_DEATH_SCREEN
# Zobrazí obrazovku po smrti s možností "Retry" nebo "Main Menu".
# =============================================================================
def show_death_screen(screen, score, wave, menu_font, info_font):  # Parametry: okno, skóre, vlna, fonty
    options = ["Retry", "Main Menu"]                   # Dvě možnosti
    selected = 0                                       # Aktuálně vybraná možnost (0 = Retry)
    clock = pygame.time.Clock()                        # Hodiny pro FPS
    btn_font = pygame.font.Font(None, 60)              # Font pro tlačítka

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)  # Poloprůhledný overlay
    overlay.fill((0, 0, 0, 150))                       # Černý s 60% průhledností
    screen.blit(overlay, (0, 0))                       # Vykreslí overlay

    while True:                                        # Smyčka death screenu
        mx, my = pygame.mouse.get_pos()                # Pozice myši
        clicked = False                                # Flag kliknutí

        for event in pygame.event.get():               # Zpracování eventů
            if event.type == pygame.QUIT:              # Zavření okna
                pygame.quit()                          # Ukončí pygame
                sys.exit()                             # Ukončí program
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Levé kliknutí
                clicked = True                         # Nastaví flag
            elif event.type == pygame.KEYDOWN:         # Stisk klávesy
                if event.key in (pygame.K_UP, pygame.K_w):     # Nahoru / W
                    selected = (selected - 1) % len(options)   # Přesune výběr nahoru (cyklicky)
                elif event.key in (pygame.K_DOWN, pygame.K_s): # Dolů / S
                    selected = (selected + 1) % len(options)   # Přesune výběr dolů (cyklicky)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):  # Enter / Space
                    return options[selected].lower()   # Vrátí vybranou možnost jako lowercase

        # Vykreslení titulku "YOU DIED"
        title_surf = menu_font.render("YOU DIED", True, (255, 50, 50))     # Červený text
        title_shadow = menu_font.render("YOU DIED", True, (0, 0, 0))      # Černý stín
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))  # Centrováno nahoře
        screen.blit(title_shadow, title_rect.move(4, 4))   # Stín posunutý o 4 px
        screen.blit(title_surf, title_rect)            # Text přes stín

        # Statistiky
        stats_surf = info_font.render(f"Score: {score}   |   Wave: {wave}", True, WHITE)  # Skóre a vlna
        stats_rect = stats_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4 + 70))  # Pod titulkem
        screen.blit(stats_surf, stats_rect)            # Vykreslí

        # Tlačítka
        button_width = 300                             # Šířka tlačítka
        button_height = 80                             # Výška tlačítka
        for idx, option in enumerate(options):          # Pro každou možnost
            btn_rect = pygame.Rect(0, 0, button_width, button_height)  # Obdélník tlačítka
            btn_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 110)  # Centrováno, rozestup 110 px

            if btn_rect.collidepoint(mx, my):          # Pokud myš je nad tlačítkem
                selected = idx                         # Zvýrazní tlačítko
                if clicked:                            # Pokud se kliklo
                    return options[selected].lower()   # Vrátí výběr

            color_bg = (150, 50, 50) if idx == selected else (80, 30, 30)      # Barva pozadí (vybraný/nevybraný)
            color_text = WHITE if idx == selected else (200, 200, 200)          # Barva textu

            pygame.draw.rect(screen, color_bg, btn_rect, border_radius=15)     # Pozadí tlačítka
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)     # Okraj tlačítka

            option_surf = btn_font.render(option, True, color_text)            # Text tlačítka
            option_rect = option_surf.get_rect(center=btn_rect.center)         # Centrováno v tlačítku
            screen.blit(option_surf, option_rect)      # Vykreslí text

        pygame.display.flip()                          # Překreslí obrazovku
        clock.tick(FPS)                                # Omezení na 60 FPS


# =============================================================================
# FUNKCE MAIN() – HLAVNÍ HERNÍ SMYČKA
# Toto je srdce celé hry. Inicializuje svět, spravuje nepřátele,
# řeší kolize a vykresluje vše na obrazovku.
# =============================================================================
def main():
    global WORLD_WIDTH_PX, WORLD_HEIGHT_PX             # Globální proměnné pro velikost světa
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)  # Vytvoří fullscreen borderless okno
    pygame.display.set_caption(TITLE)                  # Nastaví titulek okna
    clock = pygame.time.Clock()                        # Hodiny pro stabilní FPS

    # Cachované fonty (vytvoří se jednou, ne každý snímek – optimalizace)
    font_ui = pygame.font.Font(None, 36)               # Font pro UI text (36 px)
    font_lg = pygame.font.Font(None, 74)               # Velký font pro nadpisy (74 px)
    font_sm = pygame.font.Font(None, 36)               # Malý font pro jména upgradů
    font_rar = pygame.font.Font(None, 28)              # Font pro rarity text (28 px)
    font_desc = pygame.font.Font(None, 24)             # Font pro popisy upgradů (24 px)

    # Generování herního světa
    blocks, items, rooms = generate_dungeon(DUNGEON_SIZE)  # Vygeneruje dungeon (stěny, předměty, místnosti)
    max_x = max(room['x'] + room['width'] for room in rooms)   # Pravý okraj světa
    max_y = max(room['y'] + room['height'] for room in rooms)  # Dolní okraj světa
    WORLD_WIDTH_PX = max_x + BLOCK_SIZE                # Celková šířka světa v pixelech
    WORLD_HEIGHT_PX = max_y + BLOCK_SIZE               # Celková výška světa v pixelech

    # Spawn hráče do první místnosti
    start_room = rooms[0]                              # První místnost = start
    start_x = start_room['x'] + start_room['width'] // 2      # Střed místnosti X
    start_y = start_room['y'] + start_room['height'] // 2     # Střed místnosti Y
    player = Player(start_x, start_y)                  # Vytvoří hráče na startovní pozici

    # Spawn počátečních nepřátel v ostatních místnostech
    enemies = pygame.sprite.Group()                    # Sprite group pro nepřátele
    for room in rooms:                                 # Pro každou místnost
        if room == start_room:                         # Přeskoč startovní místnost (bez nepřátel)
            continue
        if random.random() < 0.7:                      # 70% šance na nepřítele
            ex = room['x'] + random.randint(2, (room['width']//BLOCK_SIZE)-3) * BLOCK_SIZE   # Náhodná X pozice v místnosti
            ey = room['y'] + random.randint(2, (room['height']//BLOCK_SIZE)-3) * BLOCK_SIZE  # Náhodná Y pozice
            enemy_type = random.choices(['walker', 'flying'], weights=[0.7, 0.3])[0]  # 70% walker, 30% flying
            enemy = Enemy(ex, ey, enemy_type)          # Vytvoří nepřítele
            enemies.add(enemy)                         # Přidá do skupiny

    # Inicializace kamery
    camera = Camera(WORLD_WIDTH_PX, WORLD_HEIGHT_PX)   # Kamera pokrývající celý svět

    # Proměnné pro wave systém
    spawn_timer = 0                                    # Časovač do dalšího spawnu
    current_spawn_interval = ENEMY_SPAWN_INTERVAL      # Aktuální interval spawnu (zrychluje se)
    wave_number = 1                                    # Číslo aktuální vlny
    wave_timer = 0                                     # Časovač aktuální vlny
    total_spawns = 0                                   # Celkový počet provedených spawnů

    # Herní proměnné
    running = True                                     # Flag pro běh herní smyčky
    score: int = 0                                     # Skóre hráče
    death_timer = 0                                    # Časovač po smrti (pro zpoždění death screenu)
    is_level_up_screen = False                         # Zda je zobrazeno upgrade menu
    upgrades_offered = []                              # Nabízené upgrady (3 karty)

    # Pool upgradů – 15 upgradů v 5 raritních stupních
    UPGRADES_POOL = [
        # Common (50% šance) – malé bonusy
        {"name": "Minor Vitality", "rarity": "Common", "desc": "+5 Max HP", "stats": {"max_health": 5}},       # +5 max. zdraví
        {"name": "Minor Strength", "rarity": "Common", "desc": "+1 Damage", "stats": {"damage": 1}},           # +1 poškození
        {"name": "Swiftness", "rarity": "Common", "desc": "+0.1 Speed", "stats": {"speed": 0.1}},              # +0.1 rychlost

        # Uncommon (25% šance) – smíšené bonusy s trade-offy
        {"name": "Warrior", "rarity": "Uncommon", "desc": "+2 Damage, -2 Max HP", "stats": {"damage": 2, "max_health": -2}},           # +2 dmg, -2 HP
        {"name": "Stamina", "rarity": "Uncommon", "desc": "+10 Max HP, Heal 10%", "stats": {"max_health": 10, "heal_pct": 0.1}},       # +10 HP, léčí 10%
        {"name": "Sprinter", "rarity": "Uncommon", "desc": "+0.3 Speed, -1 Dmg", "stats": {"speed": 0.3, "damage": -1}},               # +0.3 rychlost, -1 dmg

        # Rare (15% šance) – silné bonusy
        {"name": "Vampire", "rarity": "Rare", "desc": "Heal 30%, +1 Dmg", "stats": {"heal_pct": 0.3, "damage": 1}},                   # Léčí 30%, +1 dmg
        {"name": "Juggernaut", "rarity": "Rare", "desc": "+20 Max HP, -0.1 Speed", "stats": {"max_health": 20, "speed": -0.1}},        # +20 HP, -0.1 rychlost
        {"name": "Assassin", "rarity": "Rare", "desc": "+3 Damage, -1 Cooldown", "stats": {"damage": 3, "cooldown": 1}},               # +3 dmg, -1 cooldown

        # Epic (8% šance) – velmi silné, větší trade-offy
        {"name": "Glass Cannon", "rarity": "Epic", "desc": "+5 Damage, -10 Max HP", "stats": {"damage": 5, "max_health": -10}},        # +5 dmg, -10 HP
        {"name": "Tank", "rarity": "Epic", "desc": "+30 Max HP, -0.2 Speed", "stats": {"max_health": 30, "speed": -0.2}},              # +30 HP, -0.2 rychlost
        {"name": "Berserker", "rarity": "Epic", "desc": "+4 Dmg, +0.2 Spd, -5 HP", "stats": {"damage": 4, "speed": 0.2, "max_health": -5}},  # +4 dmg, +0.2 spd, -5 HP

        # Legendary (2% šance) – extrémně silné
        {"name": "God of War", "rarity": "Legendary", "desc": "+5 Dmg, +20 HP, +0.3 Spd", "stats": {"damage": 5, "max_health": 20, "speed": 0.3}},  # Všestranný boost
        {"name": "Time Weaver", "rarity": "Legendary", "desc": "Cooldown -3, +0.5 Spd", "stats": {"cooldown": 3, "speed": 0.5}},                    # Rychlejší útoky + pohyb
        {"name": "Immortal", "rarity": "Legendary", "desc": "+50 Max HP, Heal 100%", "stats": {"max_health": 50, "heal_pct": 1.0}}                  # +50 HP a plné vyléčení
    ]

    # ========== HLAVNÍ HERNÍ SMYČKA ==========
    while running:
        clock.tick(FPS)                                # Omezení na 60 FPS (čeká pokud je snímek příliš rychlý)

        # ---- ZPRACOVÁNÍ EVENTŮ ----
        for event in pygame.event.get():               # Projde všechny pygame eventy
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Levé kliknutí myší
                if is_level_up_screen:                 # Pokud je zobrazeno upgrade menu
                    mx, my = pygame.mouse.get_pos()    # Pozice myši
                    card_w, card_h, spacing = 250, 350, 50  # Rozměry karet a mezery
                    start_x = (WINDOW_WIDTH - (3*card_w + 2*spacing)) // 2  # X pozice první karty
                    start_y = (WINDOW_HEIGHT - card_h) // 2                  # Y pozice karet
                    for idx, upgrade in enumerate(upgrades_offered):          # Pro každou nabízenou kartu
                        rect = pygame.Rect(start_x + idx*(card_w+spacing), start_y, card_w, card_h)  # Obdélník karty
                        if rect.collidepoint(mx, my):  # Pokud hráč kliknul na kartu
                            # Aplikuje statistiky upgradu na hráče
                            for stat, val in upgrade["stats"].items():     # Pro každou statistiku
                                if stat == "max_health":                   # Max zdraví
                                    player.max_health = max(1, player.max_health + val)  # Zvýší/sníží (min 1)
                                    player.health += val                   # Přidá/odečte aktuální zdraví
                                elif stat == "damage":                     # Poškození
                                    player.attack_damage += val            # Zvýší/sníží útok
                                elif stat == "speed":                      # Rychlost
                                    global PLAYER_SPEED                    # Globální proměnná
                                    PLAYER_SPEED += val                    # Zvýší/sníží rychlost
                                elif stat == "heal_pct":                   # Léčení v procentech
                                    player.heal(int(player.max_health * val))  # Vyléčí procento max zdraví
                                elif stat == "cooldown":                   # Cooldown útoku
                                    global BASE_ATTACK_COOLDOWN            # Globální proměnná
                                    BASE_ATTACK_COOLDOWN = max(5, BASE_ATTACK_COOLDOWN - val)  # Sníží cooldown (min 5)

                            player.level_up_pending -= 1   # Sníží počet čekajících level-upů
                            is_level_up_screen = False     # Zavře upgrade menu
                            break                          # Přeruší smyčku (jen 1 výběr)

            if event.type == pygame.QUIT:              # Zavření okna (křížek)
                running = False                        # Ukončí herní smyčku
            elif event.type == pygame.KEYDOWN:         # Stisk klávesy
                if event.key == pygame.K_ESCAPE:       # ESC
                    running = False                    # Ukončí hru
                elif event.key == pygame.K_f:          # F – přepnutí fullscreenu
                    if screen.get_flags() & pygame.FULLSCREEN:     # Pokud je fullscreen
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Přepne na okno
                    else:                              # Pokud je okno
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)  # Přepne na fullscreen

        # ---- LEVEL UP MENU ----
        if player.level_up_pending > 0 and not is_level_up_screen:  # Pokud čeká level-up a menu ještě není zobrazeno
            is_level_up_screen = True                  # Zapne upgrade menu
            upgrades_offered = []                      # Vyčistí nabídku
            pool_copy = list(UPGRADES_POOL)            # Kopie poolu (aby se neopakoval upgrade v jednom výběru)
            weights_map = {"Common": 50, "Uncommon": 25, "Rare": 15, "Epic": 8, "Legendary": 2}  # Váhy rarit
            for _ in range(3):                         # Vybere 3 karty
                if not pool_copy: break                # Pokud už žádné nejsou
                w = [weights_map[u["rarity"]] for u in pool_copy]  # Váhy pro aktuální pool
                chosen = random.choices(pool_copy, weights=w, k=1)[0]  # Vážený náhodný výběr
                upgrades_offered.append(chosen)        # Přidá do nabídky
                pool_copy.remove(chosen)               # Odstraní z poolu (neopakuje se)

        # ---- HERNÍ LOGIKA (pouze pokud NENÍ level up menu) ----
        if not is_level_up_screen:
            player.update(blocks, camera)              # Aktualizace hráče (vstup, pohyb, animace)
            enemies.update(blocks, player)             # Aktualizace všech nepřátel (pohyb k hráči)
            items.update(player)                       # Aktualizace předmětů (magnetismus)

            # Wave timer – odpočet do konce vlny
            wave_timer += 1                            # Zvýší časovač
            if wave_timer >= WAVE_DURATION:            # Pokud vlna skončila (2 minuty)
                wave_timer = 0                         # Resetuje časovač
                wave_number += 1                       # Další vlna
                current_spawn_interval = ENEMY_SPAWN_INTERVAL  # Resetuje interval spawnu

                # Spawn bosse na konci vlny
                bx, by = spawn_at_screen_edge(camera, ENEMY_SIZE * 3)  # Pozice za okrajem
                boss = Enemy(bx, by, 'boss')           # Vytvoří bosse
                boss.health += (wave_number - 2) * 200 # Boss je silnější v pozdějších vlnách (+200 HP za vlnu)
                boss.damage += (wave_number - 2) * 10  # Boss dělá více poškození (+10 za vlnu)
                enemies.add(boss)                      # Přidá bosse na mapu

            # Spawn nepřátel průběžně
            spawn_timer += 1                           # Zvýší časovač spawnu
            if spawn_timer >= current_spawn_interval:  # Pokud je čas na spawn
                spawn_timer = 0                        # Resetuje časovač
                total_spawns += 1                      # Zvýší celkový počet spawnů
                current_spawn_interval = max(15, int(current_spawn_interval * ENEMY_SPAWN_ACCELERATION))  # Zkrátí interval (min 15 snímků)

                # Výpočet počtu nepřátel k spawnutí
                spawn_count = int(min(ENEMY_MAX_PER_WAVE, ENEMY_WAVE_BASE + (total_spawns - 1) * ENEMY_WAVE_GROWTH))  # Postupně rostoucí
                spawned = 0                            # Kolik se už spawnulo
                attempts = 0                           # Počet pokusů (ochrana proti nekonečné smyčce)

                while spawned < spawn_count and attempts < spawn_count * 8:  # Pokouší se spawn nepřátel
                    if len(enemies) >= ENEMY_MAX_ON_MAP:   # Pokud je na mapě maximum nepřátel
                        break                          # Přeruší spawning
                    attempts += 1                      # Zvýší počet pokusů

                    sx, sy = spawn_at_screen_edge(camera, ENEMY_SIZE + 20)  # Náhodná pozice za okrajem

                    if math.hypot(sx - player.rect.centerx, sy - player.rect.centery) < ENEMY_SPAWN_RADIUS_MIN:  # Příliš blízko hráči
                        continue                       # Zkusí jinou pozici

                    # Typ nepřítele se rotuje podle vlny
                    enemy_types = ['walker', 'flying', 'tank', 'fast']     # Seznam typů
                    wave_type_index = (wave_number - 1) % len(enemy_types) # Index podle čísla vlny
                    enemy_type = enemy_types[wave_type_index]              # Typ pro tuto vlnu
                    enemies.add(Enemy(sx, sy, enemy_type))                 # Vytvoří a přidá nepřítele
                    spawned += 1                       # Zvýší počet spawnutých

            # ---- SVĚTOVÉ HRANICE ----
            # Hráč nesmí opustit herní svět
            if player.rect.left < 0:                   # Levý okraj
                player.rect.left = 0                   # Zastaví
                player.vel_x = 0                       # Vynuluje rychlost
            if player.rect.right > WORLD_WIDTH_PX:     # Pravý okraj
                player.rect.right = WORLD_WIDTH_PX     # Zastaví
                player.vel_x = 0
            if player.rect.top < 0:                    # Horní okraj
                player.rect.top = 0                    # Zastaví
                player.vel_y = 0

            if player.rect.top > WORLD_HEIGHT_PX + 5*BLOCK_SIZE:  # Pokud hráč spadl hodně mimo mapu (zcela pod světem)
                player.rect.x = start_x               # Resetuje pozici na start
                player.rect.y = start_y
                player.vel_x = 0                       # Zastaví pohyb
                player.vel_y = 0

            # Odstranění nepřátel, kteří se dostali mimo svět
            for spr in list(enemies):                  # Kopie seznamu (kvůli bezpečnému mazání)
                if isinstance(spr, Enemy):             # Jen pro Enemy objekty
                    if (spr.rect.right < 0 or spr.rect.left > WORLD_WIDTH_PX or
                        spr.rect.top < 0 or spr.rect.bottom > WORLD_HEIGHT_PX + 5*BLOCK_SIZE):  # Mimo svět
                        spr.kill()                     # Odstraní ze všech skupin

            # ---- KOLIZE HRÁČ vs NEPŘÁTELÉ ----
            for spr in enemies:                        # Pro každého nepřítele
                if isinstance(spr, Enemy) and player.rect.colliderect(spr.rect):  # Pokud se hráč dotýká nepřítele
                    if player.hit_cooldown <= 0:       # Pokud nemá imunitu
                        player.take_damage(spr.damage) # Dostane poškození
                        player.hit_cooldown = PLAYER_HIT_COOLDOWN  # Zapne imunitu
                        # Knockback hráče (odskok od nepřítele)
                        if player.rect.centerx < spr.rect.centerx:    # Nepřítel je vpravo
                            player.vel_x = -PLAYER_SPEED * 1.5        # Odskok doleva
                        else:                          # Nepřítel je vlevo
                            player.vel_x = PLAYER_SPEED * 1.5         # Odskok doprava
                        if player.rect.centery < spr.rect.centery:    # Nepřítel je dole
                            player.vel_y = -PLAYER_SPEED * 1.5        # Odskok nahoru
                        else:                          # Nepřítel je nahoře
                            player.vel_y = PLAYER_SPEED * 1.5         # Odskok dolů
                        player.knockback_timer = 7     # Knockback trvá 7 snímků

            # ---- KOLIZE ÚTOK vs NEPŘÁTELÉ ----
            if player.attacking:                       # Pokud hráč útočí
                for spr in list(enemies):              # Pro každého nepřítele (kopie kvůli mazání)
                    if isinstance(spr, Enemy) and spr not in player.hit_enemies and player.attack_hits(spr):  # Zasažen a ještě nebyl v tomto švihu
                        player.hit_enemies.add(spr)    # Označí jako zasaženého (aby nedostal 2× dmg)
                        spr.take_damage(player.attack_damage * player.damage_boost)  # Udělí poškození (dmg × boost)
                        if hasattr(spr, 'apply_knockback'):    # Ověří, zda má knockback metodu
                            spr.apply_knockback(player.rect)   # Aplikuje knockback od hráče
                        if spr.is_dead():              # Pokud nepřítel zemřel
                            items.add(Item(spr.rect.x, spr.rect.y, 'xp', xp_value=spr.xp_value))  # Dropne XP orb
                            if random.random() < 0.3:  # 30% šance na drop peněz
                                items.add(Item(spr.rect.x + random.randint(-10, 10), spr.rect.y + random.randint(-10, 10), 'money', xp_value=random.randint(1, 3)))  # Dropne 1-3 mincí
                            spr.kill()                 # Odstraní nepřítele z mapy
                            score += 10                # Přidá 10 bodů do skóre

            # ---- KOLIZE HRÁČ vs PŘEDMĚTY ----
            item_hits = pygame.sprite.spritecollide(player, items, True)  # Najde všechny předměty překrývající hráče (True = smaže je)
            for item in item_hits:                     # Pro každý sebraný předmět
                item.apply(player)                     # Aplikuje efekt (heal, XP, boost atd.)

            # Aktualizace kamery – sleduje hráče
            camera.update(player)                      # Centruje kameru na hráče

        # ========== VYKRESLOVÁNÍ ==========

        # Vytvoření menšího plátna pro zoom efekt
        cam_w = int(WINDOW_WIDTH / ZOOM)               # Šířka plátna po zoomu
        cam_h = int(WINDOW_HEIGHT / ZOOM)              # Výška plátna po zoomu
        display_surface = pygame.Surface((cam_w, cam_h))  # Menší surface pro vykreslení hry

        # Travnaté pozadí – šachovnicový vzor v zelených odstínech
        display_surface.fill((34, 110, 34))            # Základní zelená
        bg_offset_x = camera.rect.x % 64              # Offset pozadí X (pro scrollování)
        bg_offset_y = camera.rect.y % 64              # Offset pozadí Y
        for i in range(-64, cam_w + 64, 64):           # Vodorovné dlaždice
            for j in range(-64, cam_h + 64, 64):       # Svislé dlaždice
                pygame.draw.rect(display_surface, (30, 100, 30), (i + bg_offset_x, j + bg_offset_y, 32, 32))              # Tmavší čtvereček
                pygame.draw.rect(display_surface, (30, 100, 30), (i + 32 + bg_offset_x, j + 32 + bg_offset_y, 32, 32))    # Tmavší čtvereček (diagonálně)

        # Culling obdélník – vykreslí se jen objekty na obrazovce
        screen_rect = pygame.Rect(0, 0, cam_w, cam_h)  # Oblast viditelná na obrazovce

        # Vykreslení bloků (stěn)
        for block in blocks:                           # Pro každý blok
            screen_pos = camera.apply(block)           # Pozice na obrazovce
            if screen_rect.colliderect(screen_pos):    # Pokud je viditelný (culling optimalizace)
                display_surface.blit(block.image, screen_pos)  # Vykreslí blok

        # Vykreslení předmětů
        for item in items:                             # Pro každý předmět
            display_surface.blit(item.image, camera.apply(item))  # Vykreslí na správné pozici

        # Vykreslení nepřátel
        for enemy in enemies:                          # Pro každého nepřítele
            if getattr(enemy, 'hit_flash', 0) > 0 and hasattr(enemy, 'flash_image'):  # Pokud bliká (právě dostal zásah)
                display_surface.blit(enemy.flash_image, camera.apply(enemy))  # Bílá verze (flash)
            else:                                      # Normální stav
                display_surface.blit(enemy.image, camera.apply(enemy))  # Normální obrázek

        # Vykreslení hráče
        if player.hit_cooldown > 0 and (player.hit_cooldown // 4) % 2 == 0:  # Pokud má imunitu a bliká (každé 4 snímky)
            mask = pygame.mask.from_surface(player.image)      # Vytvoří masku z obrázku
            flash_image = mask.to_surface(setcolor=(255, 50, 50, 255), unsetcolor=(0, 0, 0, 0))  # Červená verze
            display_surface.blit(flash_image, camera.apply(player))  # Vykreslí červeného hráče
        else:                                          # Normální stav
            display_surface.blit(player.image, camera.apply(player))  # Normální hráč

        # Vykreslení slash efektu útoku
        player.draw_attack(display_surface, camera)    # Vykreslí srpkovitý efekt

        # Zvětšení (zoom) – menší surface se zvětší na celé okno
        scaled_surf = pygame.transform.scale(display_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))  # Škálování na plnou velikost
        screen.blit(scaled_surf, (0, 0))               # Vykreslí na hlavní okno

        # ---- UI OVERLAY ----
        # Vlna a čas
        wave_time_left = (WAVE_DURATION - wave_timer) // FPS   # Zbývající čas vlny v sekundách
        minutes = wave_time_left // 60                 # Minuty
        seconds = wave_time_left % 60                  # Sekundy
        wave_text = font_ui.render(f"Wave: {wave_number} ({minutes}:{seconds:02d})", True, ORANGE)  # Text vlny (oranžový)
        screen.blit(wave_text, (WINDOW_WIDTH // 2 - wave_text.get_width() // 2, 10))  # Centrováno nahoře

        # Level a XP
        level_text = font_ui.render(f"Level: {player.level} ({player.xp}/{player.max_xp} XP)", True, CYAN)  # Tyrkysový text
        screen.blit(level_text, (10, 10))              # Vlevo nahoře

        # Zdraví
        health_text = font_ui.render(f"Health: {player.health}/{player.max_health}", True, WHITE)  # Bílý text
        screen.blit(health_text, (10, 50))             # Pod levelem

        # Skóre
        score_text = font_ui.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 90))              # Pod zdravím

        # Klíče
        key_text = font_ui.render(f"Keys: {player.keys}", True, WHITE)
        screen.blit(key_text, (10, 130))               # Pod skóre

        # Peníze
        money_text = font_ui.render(f"Money: {player.money}", True, (255, 215, 0))  # Zlatý text
        screen.blit(money_text, (10, 170))             # Pod klíči

        # Poškození
        dmg_val = player.attack_damage * player.damage_boost   # Aktuální poškození (základ × boost)
        damage_text = font_ui.render(f"Damage: {dmg_val}", True, RED)  # Červený text
        screen.blit(damage_text, (10, 210))            # Pod penězi

        # Damage boost indikátor (pokud je aktivní)
        if player.damage_boost > 1:                    # Pokud je boost aktivní
            boost_text = font_ui.render(f"Damage Boost: {player.damage_boost_timer//60}s", True, YELLOW)  # Zbývající sekundy
            screen.blit(boost_text, (10, 250))         # Pod poškozením

        # ---- LEVEL UP OVERLAY ----
        if is_level_up_screen:                         # Pokud je zobrazeno upgrade menu
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)  # Poloprůhledný overlay
            overlay.fill((0, 0, 0, 180))               # Černý s 70% průhledností
            screen.blit(overlay, (0, 0))               # Vykreslí overlay

            title = font_lg.render('LEVEL UP! Choose Upgrade:', True, WHITE)  # Bílý nadpis
            screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))  # Centrováno

            card_w, card_h, spacing = 250, 350, 50     # Rozměry karet a mezer
            start_x = (WINDOW_WIDTH - (3*card_w + 2*spacing)) // 2  # X pozice první karty (centrováno)
            start_y = (WINDOW_HEIGHT - card_h) // 2    # Y pozice karet (centrováno)
            mx, my = pygame.mouse.get_pos()            # Pozice myši

            for idx, upgrade in enumerate(upgrades_offered):   # Pro každou ze 3 karet
                rect = pygame.Rect(start_x + idx*(card_w+spacing), start_y, card_w, card_h)  # Obdélník karty
                base_col = RARITY_COLORS.get(upgrade["rarity"], WHITE)  # Barva podle rarity
                # Pozadí karty – tmavší, při hoveru myší světlejší
                bg_col = (base_col[0]//4, base_col[1]//4, base_col[2]//4) if not rect.collidepoint(mx, my) else (base_col[0]//3, base_col[1]//3, base_col[2]//3)

                pygame.draw.rect(screen, bg_col, rect, border_radius=10)          # Pozadí karty
                pygame.draw.rect(screen, base_col, rect, 4, border_radius=10)     # Okraj karty (raritní barva)

                name_surf = font_sm.render(upgrade['name'], True, WHITE)          # Jméno upgradu
                screen.blit(name_surf, (rect.centerx - name_surf.get_width()//2, rect.top + 30))  # Centrováno nahoře karty

                rar_surf = font_rar.render(upgrade['rarity'], True, base_col)     # Rarity text v raritní barvě
                screen.blit(rar_surf, (rect.centerx - rar_surf.get_width()//2, rect.top + 65))  # Pod jménem

                parts = upgrade['desc'].split(", ")    # Rozdělí popis na řádky podle čárek
                for i, part in enumerate(parts):       # Pro každou část popisu
                    d_surf = font_desc.render(part, True, (200, 200, 200))  # Šedý text
                    screen.blit(d_surf, (rect.centerx - d_surf.get_width()//2, rect.centery + (i * 25) - 20))  # Centrováno uprostřed karty

        pygame.display.flip()                          # Překreslí celou obrazovku (double buffering)

        # ---- SMRT HRÁČE ----
        if player.is_dead():                           # Pokud je hráč mrtvý
            death_timer += 1                           # Zvyšuje časovač smrti
            if death_timer > 90:                       # Po ~1.5 sekundě
                menu_font = pygame.font.Font(None, 100)    # Velký font pro death screen
                info_font = pygame.font.Font(None, 40)     # Menší font pro statistiky
                action = show_death_screen(screen, score, wave_number, menu_font, info_font)  # Zobrazí death screen
                if action == "retry":                  # Hráč zvolil Retry
                    return "retry"                     # Vrátí "retry" → hlavní smyčka restartuje hru
                else:                                  # Hráč zvolil Main Menu
                    return "menu"                      # Vrátí "menu" → vrátí se do hlavního menu

    return "quit"                                      # Pokud se herní smyčka ukončí normálně (ESC)


# =============================================================================
# FUNKCE MAIN_MENU – HLAVNÍ MENU
# Welcome screen s animovanými částicemi, titulkem a tlačítky.
# =============================================================================
def main_menu():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)  # Fullscreen borderless okno
    pygame.display.set_caption(TITLE)                  # Titulek okna
    clock = pygame.time.Clock()                        # FPS hodiny
    menu_font = pygame.font.Font(None, 100)            # Font pro titulek (100 px)
    info_font = pygame.font.Font(None, 40)             # Font pro nápovědu (40 px)
    btn_font = pygame.font.Font(None, 60)              # Font pro tlačítka (60 px)
    options = ["Start Game", "Quit"]                   # Dvě možnosti
    selected = 0                                       # Výchozí výběr (Start Game)

    # Vytvoření 50 plovoucích částic pro animaci pozadí
    particles = []                                     # Seznam částic
    for _ in range(50):                                # 50 částic
        particles.append([random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), random.uniform(0.5, 2.0)])  # [x, y, rychlost]

    while True:                                        # Smyčka hlavního menu
        mx, my = pygame.mouse.get_pos()                # Pozice myši
        clicked = False                                # Flag kliknutí

        for event in pygame.event.get():               # Zpracování eventů
            if event.type == pygame.QUIT:              # Zavření okna
                pygame.quit()                          # Ukončí pygame
                sys.exit()                             # Ukončí program
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Levé kliknutí
                clicked = True                         # Nastaví flag
            elif event.type == pygame.KEYDOWN:         # Stisk klávesy
                if event.key in (pygame.K_UP, pygame.K_w):     # Nahoru / W
                    selected = (selected - 1) % len(options)   # Přesune výběr nahoru
                elif event.key in (pygame.K_DOWN, pygame.K_s): # Dolů / S
                    selected = (selected + 1) % len(options)   # Přesune výběr dolů
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):  # Enter / Space
                    if options[selected] == "Start Game":      # Start Game
                        return "start"                 # Vrátí "start" → spustí hru
                    else:                              # Quit
                        pygame.quit()                  # Ukončí pygame
                        sys.exit()                     # Ukončí program

        # Aktualizace částic – pohyb nahoru
        for p in particles:                            # Pro každou částici
            p[1] -= p[2]                               # Posun nahoru (rychlost)
            if p[1] < -10:                             # Pokud vystoupala nad okraj
                p[1] = WINDOW_HEIGHT + 10              # Vrátí se dolů
                p[0] = random.randint(0, WINDOW_WIDTH) # Na náhodné X pozici

        screen.fill((20, 30, 20))                      # Tmavě zelené pozadí

        # Vykreslení částic
        for p in particles:                            # Pro každou částici
            pygame.draw.circle(screen, (50, 80, 50), (int(p[0]), int(p[1])), int(p[2]*2))  # Zelený kroužek

        # Titulek se stínem
        title_surf = menu_font.render(TITLE, True, (255, 215, 0))     # Zlatý text
        title_shadow = menu_font.render(TITLE, True, (0, 0, 0))       # Černý stín
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))  # Centrováno v horní třetině
        screen.blit(title_shadow, title_rect.move(4, 4))  # Stín posunutý o 4 px
        screen.blit(title_surf, title_rect)            # Text přes stín

        # Vykreslení tlačítek
        button_width = 300                             # Šířka tlačítka
        button_height = 80                             # Výška tlačítka
        for idx, option in enumerate(options):          # Pro každou možnost
            btn_rect = pygame.Rect(0, 0, button_width, button_height)  # Obdélník tlačítka
            btn_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 110)  # Centrováno, mezera 110 px

            # Detekce myši
            if btn_rect.collidepoint(mx, my):          # Pokud myš je nad tlačítkem
                selected = idx                         # Zvýrazní
                if clicked:                            # Pokud klik
                    if options[selected] == "Start Game":  # Start Game
                        return "start"                 # Spustí hru
                    else:                              # Quit
                        pygame.quit()                  # Ukončí pygame
                        sys.exit()                     # Ukončí program

            color_bg = (50, 150, 50) if idx == selected else (30, 80, 30)      # Zelení pozadí (vybraný/nevybraný)
            color_text = WHITE if idx == selected else (200, 200, 200)          # Barva textu

            pygame.draw.rect(screen, color_bg, btn_rect, border_radius=15)     # Pozadí tlačítka
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)     # Okraj tlačítka

            option_surf = btn_font.render(option, True, color_text)            # Text tlačítka
            option_rect = option_surf.get_rect(center=btn_rect.center)         # Centrováno v tlačítku
            screen.blit(option_surf, option_rect)      # Vykreslí text

        # Nápověda dole
        info_surf = info_font.render("Use W/S/Mouse to choose, Enter/Click to confirm", True, (100, 200, 100))  # Zelený text
        info_rect = info_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))  # Centrováno dole
        screen.blit(info_surf, info_rect)              # Vykreslí

        pygame.display.flip()                          # Překreslí obrazovku
        clock.tick(FPS)                                # 60 FPS


# =============================================================================
# HLAVNÍ SMYČKA PROGRAMU
# Vnořená smyčka: menu → hra → retry/menu/quit
# =============================================================================
if __name__ == "__main__":                             # Spustí se pouze pokud se soubor spouští přímo (ne importuje)
    while True:                                        # Vnější smyčka – opakuje menu
        action = main_menu()                           # Zobrazí hlavní menu (vrátí "start" nebo ukončí)
        if action == "quit":                           # Pokud hráč zvolil ukončení
            break                                      # Ukončí vnější smyčku

        while True:                                    # Vnitřní smyčka – opakuje hru
            action = main()                            # Spustí hru (vrátí "retry", "menu" nebo "quit")
            if action == "retry":                      # Retry – hráč chce hrát znovu
                continue                               # Spustí main() znovu
            elif action == "menu":                     # Menu – hráč chce zpět do menu
                break                                  # Vylítne z vnitřní smyčky do vnější (→ main_menu())
            elif action == "quit":                     # Quit – ukončení
                pygame.quit()                          # Ukončí pygame
                sys.exit()                             # Ukončí program
