import pygame                                                  # Pygame – hlavní herní knihovna pro 2D grafiku, zvuk, ovládání okna a vstup z klávesnice/myši
import random                                                  # Random – generátor náhodných čísel (pro spawn nepřátel, generování dungeonu, drop předmětů)
import math                                                    # Math – matematické funkce (sin, cos, atan2, hypot) – používá se pro výpočet úhlů útoku a vzdáleností
import sys                                                     # Sys – systémové funkce, hlavně sys.exit() pro úplné ukončení programu
from typing import TypedDict, List, Tuple                      # Typing – typové anotace pro lepší čitelnost kódu (TypedDict pro strukturu místnosti)

class RoomDict(TypedDict):                                     # Definuje tvar slovníku pro jednu místnost v dungeonu
    x: int                                                     # x-ová souřadnice místnosti ve světě (v pixelech)
    y: int                                                     # y-ová souřadnice místnosti ve světě (v pixelech)
    width: int                                                 # šířka místnosti v pixelech
    height: int                                                # výška místnosti v pixelech
    grid_x: int                                                # pozice místnosti v mřížce (sloupec)
    grid_y: int                                                # pozice místnosti v mřížce (řádek)
    doors: List[Tuple[int, int]]                               # seznam dveří – každá dveře jsou (x, y) souřadnice

# Inicializace Pygame                                           # Inicializace Pygame
pygame.init()                                                  # Spustí všechny moduly Pygame (grafiku, zvuk, fonty atd.) – musí být voláno před čímkoli dalším

# Konstanty pro borderless fullscreen                           # Konstanty pro borderless fullscreen
infoObject = pygame.display.Info()                             # Získá informace o aktuálním monitoru (rozlišení, barevná hloubka atd.)
WINDOW_WIDTH = infoObject.current_w                            # Šířka okna = šířka monitoru (pro borderless fullscreen)
WINDOW_HEIGHT = infoObject.current_h                           # Výška okna = výška monitoru
TITLE = "Survival Game"                                        # Titulek okna zobrazený v záhlaví
FPS = 60                                                       # Počet snímků za sekundu – hra běží 60× za sekundu
ZOOM = 1.5                                                     # Míra přiblížení kamery

RARITY_COLORS = {                                              # Slovník mapující název rarity na RGB barvu
    "Common": (200, 200, 200),                                 # Common = šedá
    "Uncommon": (50, 205, 50),                                 # Uncommon = zelená
    "Rare": (30, 144, 255),                                    # Rare = modrá
    "Epic": (138, 43, 226),                                    # Epic = fialová
    "Legendary": (255, 215, 0)                                 # Legendary = zlatá
}                                                              # Konec všech postav

# Barvy (použijeme pro textury, ale některé ponecháme pro záložní) # Barvy (použijeme pro textury, ale některé ponecháme pro záložní)
BLACK = (0, 0, 0)                                              # Černá – pozadí, okraje
WHITE = (255, 255, 255)                                        # Bílá – texty, okraje tlačítek
RED = (255, 0, 0)                                              # Červená – poškození, zdraví
GREEN = (0, 255, 0)                                            # Zelená – XP, léčení
BLUE = (0, 0, 255)                                             # Modrá – záložní barva
BROWN = (139, 69, 19)                                          # Hnědá – dřevo, zem
GRAY = (128, 128, 128)                                         # Šedá – kámen
YELLOW = (255, 255, 0)                                         # Žlutá – efekty, zvýraznění
PURPLE = (128, 0, 128)                                         # Fialová – speciální nepřátelé
ORANGE = (255, 165, 0)                                         # Oranžová – vlnový text
CYAN = (0, 255, 255)                                           # Tyrkysová – level text

# Velikost bloku                                                # Velikost bloku
BLOCK_SIZE = 32                                                # Velikost jednoho bloku (stěny) v pixelech – 32×32 px

# Rozměry dungeonu (počet místností v řadě/sloupci)             # Rozměry dungeonu (počet místností v řadě/sloupci)
DUNGEON_SIZE = 5                                               # Mřížka dungeonu je 5×5 místností
ROOM_MIN_SIZE = 5                                              # Minimální počet bloků na šířku/výšku místnosti
ROOM_MAX_SIZE = 10                                             # Maximální velikost místnosti v blocích (10 bloků = 320 px)

# Hráč                                                          # Hráč
PLAYER_WIDTH = 28                                              # Šířka hráče v pixelech
PLAYER_HEIGHT = 28                                             # Výška hráče v pixelech
PLAYER_SPEED = 5                                               # Rychlost pohybu hráče v pixelech za snímek

# Nepřátelé                                                     # Nepřátelé
ENEMY_SIZE = 28                                                # Velikost nepřítele v pixelech (28×28)
ENEMY_SPEED = 2                                                # Základní rychlost chodícího nepřítele
FLYING_ENEMY_SPEED = 1                                         # Rychlost létajícího nepřítele (pomalejší)
ENEMY_SPAWN_INTERVAL = 60                                      # Počet snímků mezi spawnem (1s při 60FPS)
ENEMY_SPAWN_RADIUS_MIN = 300                                   # Minimální vzdálenost od hráče při spawnu
ENEMY_SPAWN_ACCELERATION = 0.985                               # Zrychlování intervalu (max speed za cca 5 minut)
ENEMY_WAVE_BASE = 1                                            # Začátek spawnu po jednom
ENEMY_WAVE_GROWTH = 0.05                                       # Přidá nepřítele každých 20 vln (pomalejší škálování)
ENEMY_MAX_PER_WAVE = 10                                        # Do maxima 10 nepřátel na vlnu
ENEMY_MAX_ON_MAP = 40                                          # Maximální počet nepřátel najednou na mapě (lze změnit)
WAVE_DURATION = 7200                                           # Délka vlny 2 minuty při 60 FPS

# Útok                                                          # Útok
ATTACK_DURATION = 10                                           # Délka trvání útoku v snímcích
ATTACK_SIZE = 40                                               # Velikost oblast útoku (dosah meče) v pixelech
ATTACK_DAMAGE = 10                                             # Základní poškození útoku
BASE_ATTACK_COOLDOWN = 40                                      # Počet snímků mezi útoky

# Zdraví hráče                                                  # Zdraví hráče
PLAYER_MAX_HEALTH = 100                                        # Maximální zdraví hráče na začátku
PLAYER_HIT_COOLDOWN = 30                                       # Počet snímků imunity po zásahu

# Předměty                                                      # Předměty
ITEM_SIZE = 24                                                 # Velikost ikony předmětu v pixelech
HEAL_AMOUNT = 2                                                # Kolik zdraví doplní health pickup
DAMAGE_BOOST = 2                                               # Zvýšení útoku (násobič)
DAMAGE_BOOST_DURATION = 300                                    # Délka damage boostu v snímcích

# =============================================                 # =============================================
# MegaBonk-style Weapon & Tome Definitions                      # MegaBonk-style Weapon & Tome Definitions
# =============================================                 # =============================================
MAX_WEAPON_LEVEL = 5                                           # Maximální úroveň zbraně
MAX_WEAPON_SLOTS = 4                                           # Maximální počet slotů pro zbraně
REROLL_BASE_COST = 3                                           # Základní cena za přetočení nabídek

WEAPON_DEFS = {                                                # Definice zbraní
    "sword": {                                                 # Zbraň: Meč
        "name": "Sword",                                       # Název meče
        "icon_color": (200, 200, 220),                         # Barva ikony meče
        "type": "weapon",                                      # Typ je zbraň
        "levels": {                                            # Úrovně blesku
            1: {"damage": 10, "cooldown": 40, "size": 1.0, "desc": "Basic melee slash"}, # Úroveň 1
            2: {"damage": 15, "cooldown": 35, "size": 1.2, "desc": "+Damage, +Size"}, # Úroveň 2
            3: {"damage": 22, "cooldown": 28, "size": 1.4, "desc": "+Damage, Faster"}, # Úroveň 3
            4: {"damage": 30, "cooldown": 22, "size": 1.7, "desc": "+Damage, +Size"}, # Úroveň 4
            5: {"damage": 42, "cooldown": 16, "size": 2.0, "desc": "MAX: Massive Blade"}, # Úroveň 5
        }                                                      # Konec všech postav
    },                                                         # Konec definice Zloděje
    "shuriken": {                                              # Zbraň: Shuriken
        "name": "Shuriken",                                    # Název shurikenu
        "icon_color": (180, 180, 200),                         # Barva ikony shurikenu
        "type": "weapon",                                      # Typ je zbraň
        "levels": {                                            # Úrovně blesku
            1: {"damage": 8, "cooldown": 90, "count": 1, "speed": 5, "desc": "Throws 1 shuriken"}, # Úroveň 1
            2: {"damage": 11, "cooldown": 75, "count": 2, "speed": 5.5, "desc": "2 shurikens"}, # Úroveň 2
            3: {"damage": 15, "cooldown": 60, "count": 3, "speed": 6, "desc": "3 shurikens"}, # Úroveň 3
            4: {"damage": 20, "cooldown": 50, "count": 4, "speed": 6.5, "desc": "4 shurikens!"}, # Úroveň 4
            5: {"damage": 28, "cooldown": 35, "count": 6, "speed": 7, "desc": "MAX: Shuriken Storm"}, # Úroveň 5
        }                                                      # Konec všech postav
    },                                                         # Konec definice Zloděje
    "fire_ring": {                                             # Zbraň: Ohnivý kruh
        "name": "Fire Ring",                                   # Název ohnivého kruhu
        "icon_color": (255, 100, 30),                          # Barva ikony ohnivého kruhu
        "type": "weapon",                                      # Typ je zbraň
        "levels": {                                            # Úrovně blesku
            1: {"damage": 4, "cooldown": 180, "radius": 60, "duration": 40, "desc": "Fire burst around you"}, # Úroveň 1
            2: {"damage": 7, "cooldown": 150, "radius": 80, "duration": 45, "desc": "+Damage, +Radius"}, # Úroveň 2
            3: {"damage": 11, "cooldown": 120, "radius": 100, "duration": 50, "desc": "Bigger & stronger"}, # Úroveň 3
            4: {"damage": 16, "cooldown": 90, "radius": 120, "duration": 55, "desc": "Huge fire ring"}, # Úroveň 4
            5: {"damage": 24, "cooldown": 60, "radius": 150, "duration": 60, "desc": "MAX: Inferno"}, # Úroveň 5
        }                                                      # Konec všech postav
    },                                                         # Konec definice Zloděje
    "lightning": {                                             # Zbraň: Blesk
        "name": "Lightning",                                   # Název blesku
        "icon_color": (100, 180, 255),                         # Barva ikony blesku
        "type": "weapon",                                      # Typ je zbraň
        "levels": {                                            # Úrovně blesku
            1: {"damage": 20, "cooldown": 150, "targets": 1, "desc": "Strikes nearest enemy"}, # Úroveň 1
            2: {"damage": 28, "cooldown": 125, "targets": 2, "desc": "Chains to 2"}, # Úroveň 2
            3: {"damage": 38, "cooldown": 100, "targets": 3, "desc": "3 targets"}, # Úroveň 3
            4: {"damage": 50, "cooldown": 80, "targets": 4, "desc": "4 chain lightning"}, # Úroveň 4
            5: {"damage": 65, "cooldown": 55, "targets": 5, "desc": "MAX: Thunder Storm"}, # Úroveň 5
        }                                                      # Konec všech postav
    }                                                          # Konec všech postav
}                                                              # Konec všech postav

TOME_DEFS = {                                                  # Definice knih (pasivních vylepšení)
    "vitality": {                                              # Kniha vitality
        "name": "Vitality Tome",                               # Název knihy vitality
        "icon_color": (255, 80, 80),                           # Barva ikony knihy vitality
        "type": "tome",                                        # Typ nabídky: kniha
        "stat": "max_health",                                  # Zvyšuje maximální zdraví
        "per_level": 10,                                       # O 10 zdraví za úroveň
        "desc": "+10 Max HP",                                  # Popis knihy
        "max_level": 10,                                       # Maximální úroveň knihy
    },                                                         # Konec definice Zloděje
    "power": {                                                 # Kniha síly
        "name": "Power Tome",                                  # Název knihy síly
        "icon_color": (255, 165, 0),                           # Barva ikony knihy síly
        "type": "tome",                                        # Typ nabídky: kniha
        "stat": "damage_mult",                                 # Zvyšuje násobič poškození
        "per_level": 0.1,                                      # O 10 % za úroveň
        "desc": "+10% Damage",                                 # Popis knihy
        "max_level": 10,                                       # Maximální úroveň knihy
    },                                                         # Konec definice Zloděje
    "speed": {                                                 # Kniha rychlosti
        "name": "Speed Tome",                                  # Název knihy rychlosti
        "icon_color": (0, 200, 255),                           # Barva ikony knihy rychlosti
        "type": "tome",                                        # Typ nabídky: kniha
        "stat": "speed",                                       # Zvyšuje rychlost pohybu
        "per_level": 0.3,                                      # O 0.3 za úroveň
        "desc": "+0.3 Speed",                                  # Popis knihy
        "max_level": 8,                                        # Maximální úroveň knihy
    },                                                         # Konec definice Zloděje
    "haste": {                                                 # Kniha spěchu (rychlosti útoku)
        "name": "Haste Tome",                                  # Název knihy spěchu
        "icon_color": (255, 255, 100),                         # Barva ikony knihy spěchu
        "type": "tome",                                        # Typ nabídky: kniha
        "stat": "cooldown_mult",                               # Snižuje násobič cooldownu (zvyšuje rychlost střelby)
        "per_level": 0.05,                                     # O 5 % za úroveň
        "desc": "-5% Cooldown",                                # Popis knihy
        "max_level": 10,                                       # Maximální úroveň knihy
    },                                                         # Konec definice Zloděje
    "luck": {                                                  # Kniha štěstí
        "name": "Luck Tome",                                   # Název knihy štěstí
        "icon_color": (0, 255, 100),                           # Barva ikony knihy štěstí
        "type": "tome",                                        # Typ nabídky: kniha
        "stat": "luck",                                        # Zvyšuje štěstí
        "per_level": 1,                                        # O 1 za úroveň
        "desc": "+1 Luck (better rarity)",                     # Popis knihy
        "max_level": 5,                                        # Maximální úroveň knihy
    }                                                          # Konec všech postav
}                                                              # Konec všech postav

# =============================================                 # =============================================
# Helper funkce pro upgrade systém                              # Helper funkce pro upgrade systém
# =============================================                 # =============================================

def get_rarity_for_level(level):                               # Funkce vrátí raritu podle úrovně upgradu
    """Vrátí raritu podle úrovně upgradu."""                   # Docstring (dokumentace)
    if level <= 1:                                             # Pokud je úroveň 1
        return "Common"                                        # Vrátí Common (běžná)
    elif level == 2:                                           # Pokud je úroveň 2
        return "Uncommon"                                      # Vrátí Uncommon (neobvyklá)
    elif level == 3:                                           # Pokud je úroveň 3
        return "Rare"                                          # Vrátí Rare (vzácná)
    elif level == 4:                                           # Pokud je úroveň 4
        return "Epic"                                          # Vrátí Epic (epická)
    else:                                                      # Pokud se nevlezla
        return "Legendary"                                     # Vrátí Legendary (legendární)

def generate_upgrade_offers(player):                           # Funkce vygeneruje nabídky vylepšení pro hráče
    """Vygeneruje 3 náhodné nabídky upgradu z dostupných zbraní a tomů.""" # Docstring
    available = []                                             # Seznam dostupných vylepšení

    # Upgrady existujících zbraní (co ještě nejsou na maxu)     # Upgrady existujících zbraní (co ještě nejsou na maxu)
    for wid, level in player.weapons.items():                  # Prochází aktuální zbraně hráče
        if level < MAX_WEAPON_LEVEL:                           # Pokud zbraň ještě nedosáhla maximální úrovně
            next_level = level + 1                             # Určí další úroveň zbraně
            stats = WEAPON_DEFS[wid]["levels"][next_level]     # Získá statistiky další úrovně
            rarity = get_rarity_for_level(next_level)          # Určí raritu podle úrovně
            available.append({                                 # Přidá nabídku do dostupných
                "type": "weapon_upgrade",                      # Typ nabídky: vylepšení zbraně
                "id": wid,                                     # ID zbraně
                "name": WEAPON_DEFS[wid]["name"],              # Název zbraně
                "icon_color": WEAPON_DEFS[wid]["icon_color"],  # Barva ikony zbraně
                "rarity": rarity,                              # Rarita knihy
                "desc": stats["desc"],                         # Popis zbraně na úrovni 1
                "current_level": level,                        # Aktuální úroveň zbraně
                "next_level": next_level,                      # Nová úroveň knihy
            })                                                 # Konec přidání

    # Nové zbraně (pokud je slot volný)                         # Nové zbraně (pokud je slot volný)
    if len(player.weapons) < MAX_WEAPON_SLOTS:                 # Pokud má hráč volný slot pro zbraně
        for wid, wdef in WEAPON_DEFS.items():                  # Prochází všechny definované zbraně
            if wid not in player.weapons:                      # Pokud hráč zbraň ještě nemá
                stats = wdef["levels"][1]                      # Získá statistiky pro úroveň 1
                available.append({                             # Přidá nabídku do dostupných
                    "type": "weapon_new",                      # Typ nabídky: nová zbraň
                    "id": wid,                                 # ID zbraně
                    "name": wdef["name"],                      # Název zbraně
                    "icon_color": wdef["icon_color"],          # Barva ikony zbraně
                    "rarity": "Common",                        # Nové zbraně mají raritu Common
                    "desc": stats["desc"],                     # Popis zbraně na úrovni 1
                    "current_level": 0,                        # Aktuální úroveň (nemá)
                    "next_level": 1,                           # Nová úroveň je 1
                })                                             # Konec přidání

    # Tomy                                                      # Tomy
    for tid, tdef in TOME_DEFS.items():                        # Prochází všechny knihy (tomy)
        current = player.tomes.get(tid, 0)                     # Získá aktuální úroveň knihy u hráče (0 pokud nemá)
        if current < tdef["max_level"]:                        # Pokud kniha nedosáhla maximální úrovně
            next_level = current + 1                           # Určí další úroveň knihy
            rarity = get_rarity_for_level(next_level)          # Určí raritu podle úrovně
            available.append({                                 # Přidá nabídku do dostupných
                "type": "tome",                                # Typ nabídky: kniha
                "id": tid,                                     # ID knihy
                "name": tdef["name"],                          # Název knihy
                "icon_color": tdef["icon_color"],              # Barva ikony knihy
                "rarity": rarity,                              # Rarita knihy
                "desc": tdef["desc"],                          # Popis účinku knihy
                "current_level": current,                      # Aktuální úroveň knihy
                "next_level": next_level,                      # Nová úroveň knihy
            })                                                 # Konec přidání

    if not available:                                          # Pokud není žádná nabídka k dispozici
        return []                                              # Vrátí prázdný seznam

    # Váhy podle rarity a luck                                  # Váhy podle rarity a luck
    luck = player.luck                                         # Získá hodnotu štěstí od hráče
    weights = []                                               # Seznam vah pro pravděpodobnost výběru
    for offer in available:                                    # Prochází všechny dostupné nabídky
        base_w = {"Common": 50, "Uncommon": 30, "Rare": 15, "Epic": 7, "Legendary": 2} # Základní váhy podle rarity
        w = base_w.get(offer["rarity"], 10)                    # Získá základní váhu pro nabídku
        if offer["rarity"] in ["Rare", "Epic", "Legendary"]:   # Pokud je nabídka vzácná
            w += luck * 3                                      # Štěstí zvyšuje šanci na její padnutí
        weights.append(max(1, w))                              # Přidá váhu do seznamu (min 1)

    # Vyber 3 unikátní                                          # Vyber 3 unikátní
    offers = []                                                # Seznam vybraných nabídek
    avail_copy = list(available)                               # Kopie dostupných nabídek (pro odstraňování)
    w_copy = list(weights)                                     # Kopie vah
    for _ in range(min(3, len(avail_copy))):                   # Vybere až 3 unikátní nabídky
        if not avail_copy:                                     # Pokud už nejsou dostupné nabídky
            break                                              # Přeruší výběr
        chosen = random.choices(avail_copy, weights=w_copy, k=1)[0] # Náhodně vybere jednu podle vah
        idx = avail_copy.index(chosen)                         # Najde její index
        offers.append(chosen)                                  # Přidá ji do vybraných nabídek
        avail_copy.pop(idx)                                    # Odstraní z kopie dostupných
        w_copy.pop(idx)                                        # Odstraní i její váhu

    return offers                                              # Vrátí vybrané nabídky

def apply_upgrade(player, upgrade):                            # Funkce pro aplikování vylepšení na hráče
    """Aplikuje vybraný upgrade na hráče."""                   # Docstring
    if upgrade["type"] == "weapon_new":                        # Pokud je to nová zbraň
        player.weapons[upgrade["id"]] = 1                      # Přidá zbraň s úrovní 1
        player.weapon_timers[upgrade["id"]] = 0                # Inicializuje timer pro cooldown
    elif upgrade["type"] == "weapon_upgrade":                  # Pokud je to vylepšení zbraně
        player.weapons[upgrade["id"]] = upgrade["next_level"]  # Zvýší úroveň stávající zbraně
    elif upgrade["type"] == "tome":                            # Pokud je to kniha
        tid = upgrade["id"]                                    # ID knihy
        tdef = TOME_DEFS[tid]                                  # Definiční vlastnosti knihy
        player.tomes[tid] = upgrade["next_level"]              # Zvýší úroveň knihy
        if tdef["stat"] == "max_health":                       # Pokud kniha zvyšuje max zdraví
            player.max_health += tdef["per_level"]             # Zvýší maximální zdraví
            player.health += tdef["per_level"]                 # Také doplní aktuální zdraví o stejnou hodnotu
        elif tdef["stat"] == "damage_mult":                    # Pokud kniha zvyšuje poškození
            player.damage_mult += tdef["per_level"]            # Zvýší násobič poškození
        elif tdef["stat"] == "speed":                          # Pokud kniha zvyšuje rychlost
            global PLAYER_SPEED                                # Zpřístupní globální rychlost
            PLAYER_SPEED += tdef["per_level"]                  # Zvýší rychlost hráče
        elif tdef["stat"] == "cooldown_mult":                  # Pokud kniha snižuje cooldown
            player.cooldown_mult = max(0.3, player.cooldown_mult - tdef["per_level"]) # Sníží násobič cooldownu (max na 0.3)
        elif tdef["stat"] == "luck":                           # Pokud kniha zvyšuje štěstí
            player.luck += tdef["per_level"]                   # Přidá body do štěstí

def draw_upgrade_icon(surface, upgrade_id, cx, cy, size=1.0):  # Funkce pro vykreslení ikony zbraně/knihy
    """Vykreslí ikonu zbraně/tomu na kartě."""                 # Docstring
    s = size                                                   # Zkrácení proměnné pro velikost (škálování)
    if upgrade_id == "sword":                                  # Pokud jde o meč
        pygame.draw.line(surface, (200, 200, 220), (int(cx - 10*s), int(cy + 14*s)), (int(cx + 10*s), int(cy - 14*s)), max(1, int(4*s))) # Čepel (tmavá)
        pygame.draw.line(surface, (255, 255, 255), (int(cx - 9*s), int(cy + 13*s)), (int(cx + 9*s), int(cy - 13*s)), max(1, int(2*s))) # Lesk čepele
        pygame.draw.rect(surface, (218, 165, 32), (int(cx - 7*s), int(cy + 1*s), int(14*s), int(4*s))) # Záštita
        pygame.draw.line(surface, (139, 69, 19), (cx, int(cy + 5*s)), (cx, int(cy + 14*s)), max(1, int(3*s))) # Rukojeť
    elif upgrade_id == "shuriken":                             # Pokud jde o shuriken
        points = []                                            # Body pro vykreslení
        for i in range(8):                                     # Vytvoření hvězdice s 8 cípy
            a = math.radians(i * 45 - 22.5)                    # Úhel bodu
            r = 14*s if i % 2 == 0 else 7*s                    # Poloměr – sudé jsou dlouhé, liché krátké
            points.append((cx + math.cos(a) * r, cy + math.sin(a) * r)) # Přidání bodu
        pygame.draw.polygon(surface, (180, 180, 200), points)  # Vykreslí tělo shurikenu
        pygame.draw.circle(surface, (120, 120, 140), (cx, cy), max(1, int(3*s))) # Středová dírka shurikenu
    elif upgrade_id == "fire_ring":                            # Pokud jde o ohnivý kruh
        for i in range(8):                                     # Vytvoření hvězdice s 8 cípy
            a = math.radians(i * 45)                           # Úhel koulí v radiánech
            px = cx + int(math.cos(a) * 14*s)                  # Pozice X koule
            py = cy + int(math.sin(a) * 14*s)                  # Pozice Y koule
            c_val = 100 + (i * 20) % 100                       # Barva koule (střídání žluté a oranžové)
            pygame.draw.circle(surface, (255, c_val, 0), (px, py), max(1, int(4*s))) # Vykreslí ohnivou kouli
        pygame.draw.circle(surface, (255, 200, 50), (cx, cy), max(1, int(6*s))) # Středové jádro ohně
    elif upgrade_id == "lightning":                            # Pokud jde o blesk
        pts = [                                                # Body klikatého blesku
            (int(cx - 4*s), int(cy - 14*s)),                   # Začátek (nahoře)
            (int(cx + 3*s), int(cy - 4*s)),                    # 1. zlom
            (int(cx - 2*s), int(cy - 1*s)),                    # 2. zlom
            (int(cx + 7*s), int(cy + 14*s)),                   # 3. zlom (dole)
            (int(cx + 1*s), int(cy + 3*s)),                    # Návrat nahoru pro tloušťku
            (int(cx + 5*s), int(cy + 5*s)),                    # Konec
        ]                                                      # Konec polygonu záštity
        pygame.draw.lines(surface, (100, 180, 255), False, pts, max(1, int(3*s))) # Modrá záře blesku
        pygame.draw.lines(surface, (220, 240, 255), False, pts, max(1, int(1*s))) # Bílé jádro blesku
    elif upgrade_id == "vitality":                             # Pokud jde o knihu vitality (červený kříž)
        pygame.draw.rect(surface, (255, 50, 50), (int(cx - 9*s), int(cy - 3*s), int(18*s), int(6*s))) # Vodorovná část
        pygame.draw.rect(surface, (255, 50, 50), (int(cx - 3*s), int(cy - 9*s), int(6*s), int(18*s))) # Svislá část
    elif upgrade_id == "power":                                # Pokud jde o knihu síly (meč/trojúhelník nahoru)
        pygame.draw.polygon(surface, (255, 165, 0), [(cx, int(cy - 13*s)), (int(cx + 11*s), int(cy + 9*s)), (int(cx - 11*s), int(cy + 9*s))]) # Oranžový trojúhelník
        pygame.draw.polygon(surface, (255, 210, 80), [(cx, int(cy - 8*s)), (int(cx + 7*s), int(cy + 6*s)), (int(cx - 7*s), int(cy + 6*s))]) # Světlejší vnitřek
    elif upgrade_id == "speed":                                # Pokud jde o knihu rychlosti (křídlo/proužky)
        for i in range(3):                                     # 3 rychlostní pruhy
            pygame.draw.line(surface, (0, 200, 255), (int(cx - 10*s + i*5*s), int(cy + 8*s)), (int(cx + 6*s + i*5*s), int(cy - 8*s)), max(1, int(2*s))) # Modré zkosené čáry
    elif upgrade_id == "haste":                                # Pokud jde o knihu spěchu (hodiny)
        pygame.draw.circle(surface, (255, 255, 100), (cx, cy), max(1, int(11*s)), max(1, int(2*s))) # Žlutý kruh
        pygame.draw.line(surface, (255, 255, 100), (cx, cy), (int(cx + 7*s), int(cy - 9*s)), max(1, int(2*s))) # Velká ručička
        pygame.draw.line(surface, (255, 255, 100), (cx, cy), (int(cx + 9*s), int(cy + 2*s)), max(1, int(2*s))) # Malá ručička
    elif upgrade_id == "luck":                                 # Pokud jde o knihu štěstí (čtyřlístek)
        for a in [0, 90, 180, 270]:                            # 4 listy ve 4 úhlech
            lx = cx + int(math.cos(math.radians(a)) * 7*s)     # Pozice listu X
            ly = cy + int(math.sin(math.radians(a)) * 7*s)     # Pozice listu Y
            pygame.draw.circle(surface, (0, 255, 100), (lx, ly), max(1, int(5*s))) # Zelený list
        pygame.draw.line(surface, (0, 180, 50), (cx, int(cy + 5*s)), (cx, int(cy + 15*s)), max(1, int(2*s))) # Stonek


# =============================================                 # =============================================
# Projektilové třídy pro zbraně                                 # Projektilové třídy pro zbraně
# =============================================                 # =============================================

class ShurikenProjectile(pygame.sprite.Sprite):                # Třída pro projektil shurikenu
    def __init__(self, x, y, angle, speed, damage):            # Konstruktor
        super().__init__()                                     # Volání rodičovského konstruktoru Sprite
        self.damage = damage                                   # Poškození, které shuriken udělí
        self.speed = speed                                     # Rychlost letu
        self.angle_rad = math.radians(angle)                   # Směr letu v radiánech
        self.fx = float(x)                                     # Přesná pozice X (pro plynulý pohyb)
        self.fy = float(y)                                     # Přesná pozice Y
        self.vx = math.cos(self.angle_rad) * speed             # Složka rychlosti osy X
        self.vy = math.sin(self.angle_rad) * speed             # Složka rychlosti osy Y
        self.lifetime = 180                                    # Životnost projektilu ve snímcích (3s při 60FPS)
        self.hit_enemies = set()                               # Množina nepřátel, které už tento shuriken zasáhl
        self.rotation = 0                                      # Aktuální rotace shurikenu v stupních

        # Draw shuriken star                                    # Draw shuriken star
        self.base_image = pygame.Surface((14, 14), pygame.SRCALPHA) # Základní obrázek před rotací
        cx, cy = 7, 7                                          # Střed obrázku
        points = []                                            # Body pro vykreslení
        for i in range(8):                                     # Vytvoření hvězdice s 8 cípy
            a = math.radians(i * 45 - 22.5)                    # Úhel bodu
            r = 6 if i % 2 == 0 else 3                         # Liché/sudé poloměry (střídání hrotů)
            points.append((cx + math.cos(a) * r, cy + math.sin(a) * r)) # Přidání bodu
        pygame.draw.polygon(self.base_image, (180, 190, 210), points) # Vykreslení hvězdy
        pygame.draw.polygon(self.base_image, (140, 150, 170), points, 1) # Okraj hvězdy
        pygame.draw.circle(self.base_image, (100, 110, 130), (cx, cy), 2) # Dírka uprostřed

        self.image = self.base_image.copy()                    # Uložení počáteční otočené verze
        self.rect = self.image.get_rect(center=(x, y))         # Obdélník kolizí a pozice

    def update(self, **kwargs):                                # Aktualizace shurikenu každý snímek
        self.fx += self.vx                                     # Posun v ose X o rychlost
        self.fy += self.vy                                     # Posun v ose Y o rychlost
        self.rect.center = (int(self.fx), int(self.fy))        # Aplikace na obdélník
        self.lifetime -= 1                                     # Zkrácení života
        self.rotation = (self.rotation + 15) % 360             # Otočení o 15 stupňů pro rotaci
        self.image = pygame.transform.rotate(self.base_image, self.rotation) # Aplikace rotace na surface
        old_center = self.rect.center                          # Uložení starého středu (rotace mění velikost)
        self.rect = self.image.get_rect(center=old_center)     # Vycentrování nového obdélníku
        if self.lifetime <= 0:                                 # Pokud shuriken doletěl/dostal se nakonec
            self.kill()                                        # Smaže se


# Kamera                                                        # Kamera
class Camera:                                                  # TODO_COMMENT
    def __init__(self, width, height):                         # Konstruktor – přijímá šířku a výšku celého herního světa
        self.rect = pygame.Rect(0, 0, width, height)           # Obdélník kamery – pokrývá celý svět
        self.width = width                                     # Šířka světa v pixelech
        self.height = height                                   # Výška světa v pixelech
        self.view_w = int(WINDOW_WIDTH / ZOOM)                 # Skutečná šířka viditelné oblasti po zoomu (okno / zoom)
        self.view_h = int(WINDOW_HEIGHT / ZOOM)                # Skutečná výška viditelné oblasti po zoomu

    def apply(self, entity):                                   # Vrátí posunutý obdélník entity tak, aby odpovídal pozici kamery
        if hasattr(entity, 'rect'):                            # Pokud má entita atribut 'rect' (hráč, nepřítel, blok...)
            return entity.rect.move(self.rect.x, self.rect.y)  # Posune rect o offset kamery
        else:                                                  # Pokud se nevlezla
            # pro útok (rect)                                   # pro útok (rect)
            return entity.move(self.rect.x, self.rect.y)       # Posune rect o offset kamery

    def update(self, target):                                  # Aktualizuje pozici kamery tak, aby cíl (hráč) byl uprostřed
        # Sleduje hráče přesně - bez mrtvé zóny                 # Sleduje hráče přesně - bez mrtvé zóny
        target_x = -target.rect.centerx + self.view_w // 2     # Cílový X offset – centruje hráče horizontálně
        target_y = -target.rect.centery + self.view_h // 2     # Cílový Y offset – centruje hráče vertikálně

        x = target_x                                           # Nastavení X pozice kamery
        y = target_y                                           # Nastavení Y pozice kamery

        # horizontální posun kamery v rámci hranic světa        # horizontální posun kamery v rámci hranic světa
        if self.width > self.view_w:                           # Pokud je svět širší než viditelná oblast
            x = min(0, x)                                      # Kamera nemůže jít za levý okraj (x nesmí být kladné)
            x = max(-(self.width - self.view_w), x)            # Kamera nemůže jít za pravý okraj
        else:                                                  # Pokud se nevlezla
            x = 0                                              # Kamera zůstává na pozici 0

        # vertikální posun kamery v rámci hranic světa          # vertikální posun kamery v rámci hranic světa
        if self.height > self.view_h:                          # Pokud je svět vyšší než viditelná oblast
            y = min(0, y)                                      # Kamera nemůže jít za horní okraj
            y = max(-(self.height - self.view_h), y)           # Kamera nemůže jít za dolní okraj
        else:                                                  # Pokud se nevlezla
            y = 0                                              # Kamera zůstává na pozici 0

        self.rect.x = x                                        # Uloží konečnou X pozici kamery
        self.rect.y = y                                        # Uloží konečnou Y pozici kamery

# Třída pro blok s texturou                                     # Třída pro blok s texturou
class Block(pygame.sprite.Sprite):                             # TODO_COMMENT
    def __init__(self, x, y, block_type='dirt'):               # Konstruktor – pozice a typ bloku
        super().__init__()                                     # Volání rodičovského konstruktoru Sprite
        self.block_type = block_type                           # Uloží typ bloku ('dirt', 'stone', 'grass', 'wood')
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))  # Vytvoří Surface (obrázek) o velikosti bloku
        self.rect = self.image.get_rect(topleft=(x, y))        # Nastaví pozici bloku ve světě
        self.draw_texture()                                    # Zavolá metodu pro vykreslení textury

    def draw_texture(self):                                    # Procedurální generování textury bloku
        # Vytvoření textury podle typu bloku                    # Vytvoření textury podle typu bloku
        if self.block_type == 'dirt':                          # Typ: hlína
            self.image.fill((120, 82, 45))                     # Hnědý základ (hlína pod trávou)
            for _ in range(8):                                 # Přidá 8 náhodných kamínků
                dx = random.randint(0, BLOCK_SIZE-4)           # Náhodná X pozice kamínku
                dy = random.randint(0, BLOCK_SIZE-4)           # Náhodná Y pozice kamínku
                pygame.draw.rect(self.image, (90, 50, 20), (dx, dy, 4, 3)) # Vykreslí tmavší obdélníček
        elif self.block_type == 'stone':                       # Typ: kámen
            self.image.fill((100, 100, 105))                   # Šedý základ
            pygame.draw.rect(self.image, (140, 140, 145), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 2) # Světlejší okraj (3D efekt)
            pygame.draw.polygon(self.image, (70, 70, 75), [(0, BLOCK_SIZE), (BLOCK_SIZE, BLOCK_SIZE), (BLOCK_SIZE, 0)]) # Tmavší trojúhelník (stín)
            pygame.draw.rect(self.image, (100, 100, 105), (2, 2, BLOCK_SIZE-4, BLOCK_SIZE-4)) # Vnitřní plocha
            for _ in range(3):                                 # Vybere 3 karty
                dx = random.randint(4, BLOCK_SIZE-6)           # X pozice praskliny
                dy = random.randint(4, BLOCK_SIZE-6)           # Y pozice praskliny
                pygame.draw.rect(self.image, (80, 80, 85), (dx, dy, 4, 4)) # Tmavší čtvereček
        elif self.block_type == 'grass':                       # Typ: tráva
            self.image.fill((120, 82, 45))                     # Hnědý základ (hlína pod trávou)
            pygame.draw.rect(self.image, (34, 139, 34), (0, 0, BLOCK_SIZE, 12)) # Zelený pruh nahoře
            pygame.draw.rect(self.image, (0, 100, 0), (0, 10, BLOCK_SIZE, 3)) # Tmavší linka oddělující trávu od hlíny
            for i in range(5):                                 # 5 stébel trávy
                x = i * 6 + 2                                  # Rovnoměrné rozložení stébel
                h = random.randint(3, 6)                       # Náhodná výška stébla
                pygame.draw.line(self.image, (50, 200, 50), (x, 10), (x+random.randint(-1, 1), 10-h), 2) # Zelená linka nahoru
        elif self.block_type == 'wood':                        # Typ: dřevo
            self.image.fill((139, 69, 19))                     # Hnědý základ
            pygame.draw.rect(self.image, (101, 33, 0), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 2) # Tmavší okraj
            for i in range(4):                                 # 4 kroky animace
                y = i * 8 + 4                                  # Rovnoměrné rozložení
                pygame.draw.line(self.image, (101, 33, 0), (0, y), (BLOCK_SIZE, y), 2) # Tmavší čára
        else:                                                  # Pokud se nevlezla
            self.image.fill(WHITE)                             # Bílá výplň

        # Subtle border for all blocks                          # Subtle border for all blocks
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 1) # TODO_COMMENT

# Třída pro předmět                                             # Třída pro předmět
class Item(pygame.sprite.Sprite):                              # TODO_COMMENT
    def __init__(self, x, y, item_type='health', xp_value=0):  # Konstruktor – pozice, typ a hodnota
        super().__init__()                                     # Volání rodičovského konstruktoru Sprite
        self.item_type = item_type                             # Typ předmětu ('health', 'damage_boost', 'key', 'xp', 'money')
        self.xp_value = xp_value                               # Hodnota předmětu (pro XP orby = množství XP, pro peníze = počet mincí)
        self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA) # Průhledný Surface
        self.rect = self.image.get_rect(center=(x + BLOCK_SIZE//2, y + BLOCK_SIZE//2)) # Centruje na pozici bloku
        self.draw_item()                                       # Vykreslí ikonu předmětu

    def draw_item(self):                                       # Vykreslí grafiku předmětu podle typu
        self.image.fill((0, 0, 0, 0))                          # Průhledné pozadí
        # Glowing shadow                                        # Glowing shadow
        pygame.draw.circle(self.image, (255, 255, 255, 50), (12, 12), 10) # Lehký bílý záblesk (glow efekt)

        if self.item_type == 'health':                         # Zdravotní balíček
            pygame.draw.rect(self.image, (150, 0, 0), (6, 10, 12, 4)) # Vodorovná čára kříže (tmavě červená)
            pygame.draw.rect(self.image, (150, 0, 0), (10, 6, 4, 12)) # Svislá čára kříže (tmavě červená)
            pygame.draw.rect(self.image, (255, 50, 50), (7, 11, 10, 2)) # Vodorovný proužek (světle červená)
            pygame.draw.rect(self.image, (255, 50, 50), (11, 7, 2, 10)) # Svislý proužek (světle červená)
        elif self.item_type == 'damage_boost':                 # Damage boost
            # žlutý meč                                         # žlutý meč
            pygame.draw.polygon(self.image, (200, 100, 0), [(12, 3), (22, 13), (18, 17), (8, 7)]) # Čepel meče (tmavá)
            pygame.draw.polygon(self.image, (255, 215, 0), [(13, 4), (20, 11), (17, 14), (10, 7)]) # Čepel meče (světlá)
            pygame.draw.rect(self.image, (139, 69, 19), (6, 15, 6, 6)) # Rukojeť meče (hnědá)
        elif self.item_type == 'key':                          # Klíč
            # klíč                                              # klíč
            pygame.draw.circle(self.image, (255, 215, 0), (8, 12), 5, 2) # Kroužek klíče (obrys)
            pygame.draw.rect(self.image, (255, 215, 0), (13, 11, 8, 2)) # Dřík klíče
            pygame.draw.rect(self.image, (255, 215, 0), (17, 13, 2, 3)) # Zuby klíče 1
            pygame.draw.rect(self.image, (255, 215, 0), (20, 13, 2, 2)) # Zuby klíče 2
        elif self.item_type == 'xp':                           # XP orb
            # XP orb = green glowing circle                     # XP orb = green glowing circle
            pygame.draw.circle(self.image, (0, 255, 100), (12, 12), 6) # Vnější zelený kruh
            pygame.draw.circle(self.image, (200, 255, 200), (12, 12), 3) # Vnitřní světlý střed
        elif self.item_type == 'money':                        # Peníze
            # Zlatá mince                                       # Zlatá mince
            pygame.draw.circle(self.image, (255, 215, 0), (12, 12), 6) # Tělo mince (zlaté)
            pygame.draw.circle(self.image, (218, 165, 32), (12, 12), 6, 2) # Okraj mince (tmavší)
            pygame.draw.rect(self.image, (218, 165, 32), (11, 8, 2, 8)) # Svislý proužek uprostřed (detail)

    def apply(self, player):                                   # Aplikuje efekt předmětu na hráče
        if self.item_type == 'health':                         # Zdravotní balíček
            player.heal(HEAL_AMOUNT)                           # Doplní hráči HEAL_AMOUNT zdraví
        elif self.item_type == 'damage_boost':                 # Damage boost
            player.damage_boost = DAMAGE_BOOST                 # Nastaví násobič poškození
            player.damage_boost_timer = DAMAGE_BOOST_DURATION  # Spustí časovač boostu
        elif self.item_type == 'key':                          # Klíč
            player.keys += 1                                   # Přidá 1 klíč do inventáře
        elif self.item_type == 'xp':                           # XP orb
            player.add_xp(self.xp_value)                       # Přidá XP (může způsobit level up)
        elif self.item_type == 'money':                        # Peníze
            player.money += self.xp_value                      # Přidá počet mincí (uložen v xp_value)
        self.kill()                                            # Smaže se

    def update(self, player=None):                             # Aktualizace každý snímek – magnetický efekt
        if player and self.item_type in ['xp', 'money']:       # Magnetismus funguje jen pro XP a peníze
            dx = player.rect.centerx - self.rect.centerx       # Vzdálenost X
            dy = player.rect.centery - self.rect.centery       # Vzdálenost Y
            dist = math.hypot(dx, dy)                          # Vzdálenost
            if 0 < dist < 150:                                 # Pokud je hráč v dosahu 150 pixelů
                speed = 4.0                                    # Rychlost přitahování
                self.rect.x += int((dx / dist) * speed)        # Posun směrem k hráči (X)
                self.rect.y += int((dy / dist) * speed)        # Posun směrem k hráči (Y)

# =============================================                 # =============================================
# Character Definitions                                         # Character Definitions
# =============================================                 # =============================================
CHARACTER_DEFS = {                                             # Definice jednotlivých herních postav
    "knight": {                                                # Postava: Rytíř
        "name": "Knight",                                      # Jméno: Knight
        "desc": "Balanced warrior with sturdy armor",          # Popis: Vyvážený válečník
        "skin": (255, 224, 189),                               # Barva pleti
        "skin_shadow": (230, 190, 150),                        # Barva pleti (stín)
        "hair": (80, 40, 0),                                   # Barva vlasů
        "hair_highlight": (100, 50, 0),                        # Barva odlesku vlasů
        "shirt": (30, 90, 200),                                # Barva košile/zbroje
        "shirt_dark": (20, 70, 160),                           # Barva stínu na košili
        "shirt_light": (50, 120, 255),                         # Světlejší část košile
        "pants": (20, 20, 80),                                 # Barva kalhot
        "boots": (50, 50, 50),                                 # Barva bot
        "belt": (90, 45, 0),                                   # Barva opasku
        "buckle": (255, 215, 0),                               # Barva přesky opasku
        "buckle_dark": (200, 150, 0),                          # Tmavá část přesky
        "eye_white": (255, 255, 255),                          # Bělmo oka
        "eye_pupil": (20, 20, 30),                             # Zornička oka
        "cape": None,                                          # Rytíř nemá kápi
    },                                                         # Konec definice Zloděje
    "mage": {                                                  # Postava: Mág
        "name": "Mage",                                        # Jméno: Mage
        "desc": "Mystical sorcerer with arcane power",         # Popis: Mystický čaroděj
        "skin": (240, 215, 195),                               # Barva pleti
        "skin_shadow": (210, 180, 160),                        # Barva pleti (stín)
        "hair": (200, 200, 220),                               # Barva vlasů
        "hair_highlight": (230, 230, 245),                     # Barva odlesku vlasů
        "shirt": (90, 40, 160),                                # Barva roucha
        "shirt_dark": (65, 25, 120),                           # Tmavá barva roucha
        "shirt_light": (120, 60, 200),                         # Světlá barva roucha
        "pants": (60, 30, 100),                                # Barva nohavic
        "boots": (40, 20, 60),                                 # Barva bot
        "belt": (70, 50, 90),                                  # Barva opasku
        "buckle": (180, 100, 255),                             # Barva přesky
        "buckle_dark": (140, 70, 200),                         # Tmavá část přesky
        "eye_white": (255, 255, 255),                          # Bělmo oka
        "eye_pupil": (100, 50, 180),                           # Zornička (fialová)
        "cape": (100, 50, 180),                                # Mág má kápi
    },                                                         # Konec definice Zloděje
    "rogue": {                                                 # Postava: Zloděj (Rogue)
        "name": "Rogue",                                       # Jméno: Rogue
        "desc": "Swift and deadly shadow striker",             # Popis: Rychlý útočník ze stínů
        "skin": (220, 195, 165),                               # Barva pleti
        "skin_shadow": (190, 160, 130),                        # Barva pleti (stín)
        "hair": (25, 25, 30),                                  # Barva vlasů
        "hair_highlight": (45, 45, 55),                        # Barva odlesku vlasů
        "shirt": (40, 50, 40),                                 # Barva oblečení
        "shirt_dark": (25, 35, 25),                            # Tmavá barva oblečení
        "shirt_light": (55, 70, 55),                           # Světlejší oblečení
        "pants": (30, 30, 30),                                 # Barva kalhot
        "boots": (35, 30, 25),                                 # Barva bot
        "belt": (50, 40, 30),                                  # Barva opasku
        "buckle": (150, 150, 150),                             # Barva přesky
        "buckle_dark": (100, 100, 100),                        # Tmavá část přesky
        "eye_white": (255, 255, 255),                          # Bělmo oka
        "eye_pupil": (30, 60, 30),                             # Zornička oka
        "cape": None,                                          # Rytíř nemá kápi
    },                                                         # Konec definice Zloděje
    "berserker": {                                             # Postava: Berserker
        "name": "Berserker",                                   # Jméno: Berserker
        "desc": "Savage fighter fueled by rage",               # Popis: Divoký bojovník
        "skin": (210, 170, 135),                               # Barva pleti
        "skin_shadow": (180, 140, 105),                        # Barva pleti (stín)
        "hair": (180, 50, 20),                                 # Barva vlasů (zrzavá)
        "hair_highlight": (210, 80, 40),                       # Odlesk vlasů
        "shirt": (160, 50, 30),                                # Oblečení (červené)
        "shirt_dark": (120, 35, 20),                           # Tmavé oblečení
        "shirt_light": (200, 70, 40),                          # Světlejší část oblečení
        "pants": (80, 50, 30),                                 # Barva kalhot
        "boots": (60, 40, 25),                                 # Barva bot
        "belt": (100, 60, 30),                                 # Barva opasku
        "buckle": (200, 180, 50),                              # Barva přesky
        "buckle_dark": (160, 140, 30),                         # Tmavá část přesky
        "eye_white": (255, 255, 255),                          # Bělmo oka
        "eye_pupil": (150, 30, 10),                            # Zornička oka
        "cape": None,                                          # Rytíř nemá kápi
    },                                                         # Konec definice Zloděje
}                                                              # Konec všech postav

def draw_character_sprite(surf, character_id, char_config, is_walking=False, step=0): # Vykreslí postavu podle ID a konfigurace
    """Standalone funkce pro vykreslení postavy podle char_config barev.""" # Docstring
    c = char_config                                            # Zkrácení proměnné pro snazší přístup
    surf.fill((0, 0, 0, 0))                                    # Vyčistí surface (průhledné pozadí)

    # Stín                                                      # Stín
    shadow_w = 20 if not is_walking else 22                    # Při chůzi je stín trochu širší
    shadow_x = 4 if not is_walking else 3                      # Při chůzi je stín posunutý
    pygame.draw.ellipse(surf, (0, 0, 0, 80), (shadow_x, 23, shadow_w, 5)) # Černý poloprůhledný ovál

    # Nohy                                                      # Nohy
    leg_y = 19                                                 # Základní Y pozice nohou
    leg1_y = leg_y - (2 if is_walking and step in [0, 1] else 0) # Levá noha se zvedne v krocích 0 a 1
    leg2_y = leg_y - (2 if is_walking and step in [2, 3] else 0) # Pravá noha se zvedne v krocích 2 a 3
    pygame.draw.rect(surf, c["pants"], (8, leg1_y, 4, 7))      # Levá nohavice
    pygame.draw.rect(surf, c["boots"], (7, leg1_y + 5, 6, 3), border_radius=1) # Levá bota
    pygame.draw.rect(surf, c["pants"], (16, leg2_y, 4, 7))     # Pravá nohavice
    pygame.draw.rect(surf, c["boots"], (15, leg2_y + 5, 6, 3), border_radius=1) # Pravá bota

    # Plášť (za tělem, pokud postava má)                        # Plášť (za tělem, pokud postava má)
    if c.get("cape"):                                          # Pokud má postava kápi (např. mág)
        sway = 1 if is_walking and step in [1, 3] else 0       # Kymácení kápě při chůzi
        pygame.draw.polygon(surf, c["cape"],                   # Kreslí světlou část kápě
                            [(6, 12), (22, 12), (23 + sway, 22), (5 - sway, 22)]) # Body kápě
        darker = tuple(max(0, v - 30) for v in c["cape"])      # Tmavší stín kápě
        pygame.draw.polygon(surf, darker,                      # Kreslí tmavou část kápě
                            [(8, 16), (20, 16), (21 + sway, 22), (7 - sway, 22)]) # Body stínu kápě

    # Zadní ruka                                                # Zadní ruka
    arm1_y = 12 - (1 if is_walking and step in [2, 3] else 0)  # Ruka se zvedne s opační nohou
    pygame.draw.rect(surf, c["shirt_dark"], (4, arm1_y, 4, 7), border_radius=2) # Levá paže
    pygame.draw.rect(surf, c["skin"], (4, arm1_y + 5, 4, 3), border_radius=1) # Levá dlaň

    # Tělo                                                      # Tělo
    pygame.draw.rect(surf, c["shirt"], (6, 10, 16, 10), border_radius=3) # Trup
    pygame.draw.rect(surf, c["shirt_dark"], (6, 15, 16, 5),    # Stín na spodní části trupu
                     border_bottom_left_radius=3, border_bottom_right_radius=3) # Zakulacení rohů
    pygame.draw.rect(surf, c["shirt_light"], (7, 10, 14, 3),   # Zesvětlení na horní části trupu
                     border_top_left_radius=3, border_top_right_radius=3) # Zakulacení rohů

    # Opasek                                                    # Opasek
    pygame.draw.rect(surf, c["belt"], (6, 17, 16, 3))          # Pásek
    pygame.draw.rect(surf, c["buckle"], (12, 16, 4, 5), border_radius=1) # Přeska pásku
    pygame.draw.rect(surf, c["buckle_dark"], (13, 17, 2, 3))   # Tmavý detail přesky

    # Hlava                                                     # Hlava
    pygame.draw.rect(surf, c["skin"], (7, 2, 14, 11), border_radius=4) # Hlava (obličej)
    pygame.draw.rect(surf, c["skin_shadow"], (7, 9, 14, 4),    # Stín pod bradou
                     border_bottom_left_radius=4, border_bottom_right_radius=4) # Zakulacení rohů

    # Vlasy (základ)                                            # Vlasy (základ)
    pygame.draw.rect(surf, c["hair"], (6, 0, 16, 4),           # Horní část vlasů
                     border_top_left_radius=5, border_top_right_radius=5) # Zakulacení rohů
    pygame.draw.rect(surf, c["hair"], (6, 3, 3, 5))            # Levé vlasy (kotlety)
    pygame.draw.rect(surf, c["hair"], (19, 3, 3, 4))           # Pravé vlasy (kotlety)
    pygame.draw.rect(surf, c["hair_highlight"], (8, 0, 12, 2), border_radius=1) # Odlesk vlasů

    # Unikátní detaily podle postavy                            # Unikátní detaily podle postavy
    if character_id == "knight":                               # Detail pro Rytíře
        # Helmice – kovový pásek přes čelo                      # Helmice – kovový pásek přes čelo
        pygame.draw.rect(surf, (160, 160, 170), (7, 0, 14, 2), # Helma (čelenka)
                         border_top_left_radius=3, border_top_right_radius=3) # Zakulacení rohů
        pygame.draw.rect(surf, (120, 120, 130), (9, 2, 10, 1)) # Detail na helmě
    elif character_id == "mage":                               # Detail pro Mága
        # Špičatý klobouk                                       # Špičatý klobouk
        pygame.draw.polygon(surf, c["shirt"], [(14, -4), (6, 4), (22, 4)]) # Čarodějnický klobouk
        pygame.draw.polygon(surf, c["shirt_light"], [(14, -3), (8, 3), (14, 3)]) # Světlo na klobouku
        pygame.draw.circle(surf, (255, 255, 150), (14, -1), 2) # Zlatá ozdoba (měsíc/hvězda)
    elif character_id == "rogue":                              # Detail pro Zloděje (Rogue)
        # Kapuce a maska                                        # Kapuce a maska
        pygame.draw.rect(surf, (20, 25, 20), (6, 0, 16, 3),    # Tmavá kapuce
                         border_top_left_radius=5, border_top_right_radius=5) # Zakulacení rohů
        pygame.draw.rect(surf, (30, 35, 30), (7, 9, 14, 4), border_radius=2) # Maska přes ústa
    elif character_id == "berserker":                          # Detail pro Berserkera
        # Válečný make-up                                       # Válečný make-up
        pygame.draw.line(surf, (180, 30, 10), (8, 5), (8, 10), 2) # Válečné malování (levé)
        pygame.draw.line(surf, (180, 30, 10), (19, 5), (19, 10), 2) # Válečné malování (pravé)
        # Trčící vlasy                                          # Trčící vlasy
        pygame.draw.polygon(surf, c["hair"], [(7, 0), (9, -3), (11, 0)]) # Vlasy (hrot vlevo)
        pygame.draw.polygon(surf, c["hair"], [(12, 0), (14, -4), (16, 0)]) # Vlasy (hrot uprostřed)
        pygame.draw.polygon(surf, c["hair"], [(17, 0), (19, -3), (21, 0)]) # Vlasy (hrot vpravo)

    # Oči                                                       # Oči
    pygame.draw.rect(surf, c["eye_white"], (9, 6, 4, 4), border_radius=1) # Levé oko (bělmo)
    pygame.draw.rect(surf, c["eye_white"], (15, 6, 4, 4), border_radius=1) # Pravé oko (bělmo)
    pygame.draw.rect(surf, c["eye_pupil"], (10, 7, 2, 2))      # Levá zornička
    pygame.draw.rect(surf, c["eye_pupil"], (16, 7, 2, 2))      # Pravá zornička
    # Odlesk v oku                                              # Odlesk v oku
    pygame.draw.rect(surf, (255, 255, 255), (11, 6, 1, 1))     # Lesk v levém oku
    pygame.draw.rect(surf, (255, 255, 255), (17, 6, 1, 1))     # Lesk v pravém oku

    # Ústa                                                      # Ústa
    if character_id != "rogue":                                # Pokud postava NENÍ zloděj (nemá masku)
        pygame.draw.line(surf, c["skin_shadow"], (11, 11), (16, 11), 1) # Pusa (stín úsměvu)

    # Přední ruka                                               # Přední ruka
    arm2_y = 12 - (1 if is_walking and step in [0, 1] else 0)  # Přední ruka se pohybuje opačně k zadní
    pygame.draw.rect(surf, c["shirt_light"], (20, arm2_y, 4, 7), border_radius=2) # Pravá paže
    pygame.draw.rect(surf, c["skin"], (20, arm2_y + 5, 4, 3), border_radius=1) # Pravá dlaň


# Třída pro hráče (s animacemi)                                 # Třída pro hráče (s animacemi)
class Player(pygame.sprite.Sprite):                            # Úprava třídy Player pro zohlednění nových vlastností
    def __init__(self, x, y, character_id="knight"):           # Přijímá navíc character_id
        super().__init__()                                     # Volání rodičovského konstruktoru Sprite
        self.character_id = character_id                       # Identifikátor postavy hráče
        self.char_config = CHARACTER_DEFS.get(character_id, CHARACTER_DEFS["knight"]) # Konfigurace barev hráče (fallback na rytíře)
        self.width = PLAYER_WIDTH                              # Šířka hráče
        self.height = PLAYER_HEIGHT                            # Výška hráče
        self.rect = pygame.Rect(x, y, self.width, self.height) # Obdélník nepřítele ve světě
        self.vel_x = 0                                         # Stojí
        self.vel_y = 0                                         # Stojí
        self.max_health = PLAYER_MAX_HEALTH                    # Maximální zdraví
        self.health = self.max_health                          # Aktuální zdraví (začíná na max)
        self.attacking = False                                 # Ukončí útok
        self.attack_timer = 0                                  # Zbývající snímky útoku
        self.attack_cooldown = 0                               # Zbývající snímky do dalšího útoku
        self.attack_damage = ATTACK_DAMAGE                     # Základní poškození útoku
        self.money = 0                                         # Počet nasbíraných mincí
        self.attack_hitbox = pygame.Rect(0, 0, ATTACK_SIZE, ATTACK_SIZE) # Obdélník zásahu útoku
        self.facing_right = True                               # Určuje směr pohledu pro animaci útoku
        self.attack_angle = 0                                  # Úhel útoku ve stupních
        self.damage_boost = 1                                  # Resetuje násobič na 1 (normální)
        self.damage_boost_timer = 0                            # Zbývající čas damage boostu
        self.keys = 0                                          # Počet sebraných klíčů
        self.hit_cooldown = 0                                  # Zbývající snímky imunity po zásahu
        self.knockback_timer = 0                               # Časovač knockbacku (odskok)
        self.xp = 0                                            # Aktuální zkušenostní body
        self.level = 1                                         # Aktuální level
        self.max_xp = 10                                       # XP potřebné pro další level
        self.hit_enemies = set()                               # Množina nepřátel, které už tento shuriken zasáhl
        self.level_up_pending = 0                              # Počet čekajících level-upů (zobrazí se upgrade menu)

        # Health regen                                          # Health regen
        self.health_regen_timer = 0                            # Resetuje timer
        self.health_regen_rate = 120                           # 120 snímků = 2 sekundy při 60 FPS (jak často doplní HP)
        self.health_regen_amount = 1                           # Množství doplněného HP jedním tickem

        # MegaBonk weapon/tome system                           # MegaBonk weapon/tome system
        self.weapons = {"sword": 1}                            # Slovník vlastněných zbraní: ID zbraně -> úroveň
        self.tomes = {}                                        # Slovník vlastněných knih: ID knihy -> úroveň
        self.damage_mult = 1.0                                 # Násobič poškození (z Power Tome)
        self.cooldown_mult = 1.0                               # Násobič cooldownu (z Haste Tome, nižší = rychlejší střelba)
        self.luck = 0                                          # Úroveň štěstí (z Luck Tome)
        self.weapon_timers = {}                                # Slovník timerů (cooldownů) pro každou automatickou zbraň
        self.fire_ring_active = 0                              # Čas, po který je ohnivý kruh ještě aktivní
        self.fire_ring_radius = 0                              # Aktuální poloměr ohnivého kruhu
        self.fire_ring_damage = 0                              # Poškození způsobované ohnivým kruhem
        self.fire_ring_max_duration = 1                        # Maximální délka trvání pro vizuální efekty (fade)
        self.lightning_bolts = []                              # Seznam blesků čekajících na vykreslení
        self.lightning_timer = 0                               # Timer po který se blesky zobrazují
        self.reroll_cost = REROLL_BASE_COST                    # Cena za přetočení nabídek (zvyšuje se při použití)

        # Animace                                               # Animace
        self.animation_frames = {                              # Slovník s framy pro každý stav animace
            'idle': self.create_idle_frames(),                 # Stání – 2 framy (efekt dýchání)
            'walk': self.create_walk_frames(),                 # Chůze – 4 framy (pohyb nohou)
            'attack': self.create_attack_frames(),             # Útok – 1 frame (meč v ruce)
            'death': self.create_death_frames()                # Smrt – 10 framů (rotace + fade out)
        }                                                      # Konec všech postav
        self.current_animation = 'idle'                        # Animace stání (dýchání)
        self.frame_index = 0                                   # Aktuální index framu v animaci
        self.animation_speed = 0.2                             # Rychlost přepínání framů (0.2 = každých 5 snímků)
        self.image = self.animation_frames['idle'][0]          # Aktuální obrázek = první frame stání

    def draw_player_base(self, surf, is_walking=False, step=0): # Kreslí kompletní postavu pixel po pixelu
        draw_character_sprite(surf, self.character_id, self.char_config, is_walking, step) # Využije globální funkci pro kreslení postavy

    def create_idle_frames(self):                              # Vytvoří 2 framy pro stojící postavu
        frames = []                                            # Prázdný seznam
        for i in range(2):                                     # 2 framy
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # Průhledná surface
            self.draw_player_base(surf)                        # Základní postava
            if i == 1:                                         # Druhý frame
                surf.scroll(0, 1)                              # Dýchání postavy (posun o pixel)
            frames.append(surf)                                # Přidá frame
        return frames                                          # Vrátí 10 framů

    def create_walk_frames(self):                              # Vytvoří 4 framy pro chůzi
        frames = []                                            # Prázdný seznam
        for i in range(4):                                     # 4 kroky animace
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # Průhledná surface
            self.draw_player_base(surf, is_walking=True, step=i) # Vykreslí postavu v daném kroku chůze
            frames.append(surf)                                # Přidá frame
        return frames                                          # Vrátí 10 framů

    def create_attack_frames(self):                            # Vytvoří 1 frame pro útok
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # Průhledná surface
        self.draw_player_base(surf)                            # Základní postava
        # vylepšený meč                                         # vylepšený meč
        pygame.draw.line(surf, (160, 160, 170), (16, 16), (27, 2), 4) # Tmavá čepel (šedá šikmá čára)
        pygame.draw.line(surf, (255, 255, 255), (16, 16), (26, 3), 2) # Bílý odlesk na čepeli
        pygame.draw.polygon(surf, (218, 165, 32), [(14, 13), (18, 17), (16, 19), (12, 15)]) # Záštita zbraně v klidu
        pygame.draw.line(surf, (139, 69, 19), (15, 16), (11, 20), 3) # Rukojeť zbraně
        pygame.draw.circle(surf, (255, 215, 0), (11, 20), 2)   # Hlavice zbraně
        return [surf]                                          # Vrátí seznam s 1 framem

    def create_death_frames(self):                             # Vytvoří 10 framů pro animaci smrti
        frames = []                                            # Prázdný seznam
        base_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # Základní surface
        self.draw_player_base(base_surf)                       # Základní postava
        for i in range(10):                                    # 10 kroků animace
            surf = base_surf.copy()                            # Kopie základní postavy
            # Překrytí očí                                      # Překrytí očí
            pygame.draw.rect(surf, (0, 0, 0), (9, 6, 4, 4))    # Levé oko – černé
            pygame.draw.rect(surf, (0, 0, 0), (15, 6, 4, 4))   # Pravé oko – černé
            # Křížky místo očí                                  # Křížky místo očí
            pygame.draw.line(surf, (255, 0, 0), (9, 6), (12, 9), 2) # Levý křížek \
            pygame.draw.line(surf, (255, 0, 0), (12, 6), (9, 9), 2) # Levý křížek /
            pygame.draw.line(surf, (255, 0, 0), (15, 6), (18, 9), 2) # Pravý křížek \
            pygame.draw.line(surf, (255, 0, 0), (18, 6), (15, 9), 2) # Pravý křížek /
            surf = pygame.transform.rotate(surf, -i * 10)      # Postupná rotace (0°, -10°, -20°, ... -90°)
            surf.set_alpha(max(0, 255 - i * 20))               # Postupné průhlednutí (255 → 75)
            frames.append(surf)                                # Přidá frame
        return frames                                          # Vrátí 10 framů

    def get_sword_reach(self):                                 # Vypočítá dosah meče
        """Vrátí efektivní dosah meče na základě úrovně zbraně.""" # Docstring
        level = self.weapons.get("sword", 0)                   # Zjistí úroveň meče
        if level == 0:                                         # Pokud nemá meč
            return ATTACK_SIZE                                 # Výchozí dosah
        return ATTACK_SIZE * WEAPON_DEFS["sword"]["levels"][level]["size"] # Zvětší dosah podle násobiče ve WEAPON_DEFS

    def get_sword_damage(self):                                # Vypočítá aktuální poškození meče
        """Vrátí celkový damage meče včetně multiplikátorů.""" # Docstring
        level = self.weapons.get("sword", 0)                   # Zjistí úroveň meče
        if level == 0:                                         # Pokud nemá meč
            return 0                                           # Nedává žádné poškození
        base = WEAPON_DEFS["sword"]["levels"][level]["damage"] # Základní poškození na dané úrovni
        return base * self.damage_mult * self.damage_boost     # Celkové poškození po aplikaci bonusů knihy a power-upu

    def handle_input(self, camera=None):                       # Zpracování vstupu z klávesnice a myši
        keys = pygame.key.get_pressed()                        # Získá stav všech kláves (True = stisknuta)

        if self.knockback_timer > 0:                           # Pokud běží knockback
            self.knockback_timer -= 1                          # Sníží časovač
            self.vel_x *= 0.85                                 # Zpomalení X (tření)
            self.vel_y *= 0.85                                 # Zpomalení Y (tření)
        else:                                                  # Pokud se nevlezla
            self.vel_x = 0                                     # Stojí
            self.vel_y = 0                                     # Stojí

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:        # Šipka doleva nebo A
                self.vel_x = -PLAYER_SPEED                     # Pohyb doleva
                if not self.attacking:                         # Pokud neútočíme
                    self.facing_right = False                  # Otočí se doleva
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:       # Šipka doprava nebo D
                self.vel_x = PLAYER_SPEED                      # Pohyb doprava
                if not self.attacking:                         # Pokud neútočíme
                    self.facing_right = True                   # Určuje směr pohledu pro animaci útoku
            if keys[pygame.K_UP] or keys[pygame.K_w]:          # Šipka nahoru nebo W
                self.vel_y = -PLAYER_SPEED                     # Pohyb nahoru
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:        # Šipka dolů nebo S
                self.vel_y = PLAYER_SPEED                      # Pohyb dolů

            # Normalizace diagonálního pohybu, aby nešel rychleji # Normalizace diagonálního pohybu, aby nešel rychleji
            if self.vel_x != 0 and self.vel_y != 0:            # Pokud se hráč pohybuje diagonálně
                inv = 1 / math.sqrt(2)                         # Koeficient pro normalizaci (1/√2 ≈ 0.707)
                self.vel_x *= inv                              # Zpomalení X (aby diagonální rychlost nebyla √2× větší)
                self.vel_y *= inv                              # Zpomalení Y

        # Neustále sleduj myš pro úhel útoku                    # Neustále sleduj myš pro úhel útoku
        if camera:                                             # Pokud máme referenci na kameru
            mx, my = pygame.mouse.get_pos()                    # Pozice kurzoru myši pro interakci
            # Zapracování ZOOMu do projekce myši                # Zapracování ZOOMu do projekce myši
            world_mx = (mx / ZOOM) - camera.rect.x             # Světová X pozice myši
            world_my = (my / ZOOM) - camera.rect.y             # Světová Y pozice myši
            dx = world_mx - self.rect.centerx                  # Rozdíl X od hráče k myši
            dy = world_my - self.rect.centery                  # Rozdíl Y od hráče k myši
            self.attack_angle = math.degrees(math.atan2(dy, dx)) # Úhel útoku ve stupních (atan2 vrací radiány → převod)
            if not self.attacking:                             # Pokud neútočíme
                self.facing_right = dx >= 0                    # Otočení hráče podle myši

        # Útok (automatický) - sword weapon z MegaBonk systému  # Útok (automatický) - sword weapon z MegaBonk systému
        sword_level = self.weapons.get("sword", 0)             # Zjistí úroveň meče pro útok
        if sword_level > 0 and self.attack_cooldown <= 0:      # Pokud má meč a vypršel cooldown
            sword_stats = WEAPON_DEFS["sword"]["levels"][sword_level] # Načte statistiky meče pro aplikaci rychlosti
            effective_cooldown = max(5, int(sword_stats["cooldown"] * self.cooldown_mult)) # Aplikuje Haste tome
            self.attacking = True                              # Začne útok
            self.attack_timer = ATTACK_DURATION                # Nastaví délku útoku
            self.attack_cooldown = effective_cooldown          # Nastaví nový cooldown do dalšího útoku
            self.hit_enemies.clear()                           # Vyčistí seznam zasažených nepřátel

            if not camera:                                     # TODO_COMMENT
                self.attack_angle = 0 if self.facing_right else 180 # Útok doprava (0°) nebo doleva (180°)

    def move(self, blocks):                                    # Pohyb nepřítele
        # X                                                     # X
        self.rect.x += self.vel_x                              # Posun X
        self.collide(self.vel_x, 0, blocks)                    # Kolize X
        # Y                                                     # Y
        self.rect.y += self.vel_y                              # Posun Y
        self.collide(0, self.vel_y, blocks)                    # Kolize Y

    def collide(self, vel_x, vel_y, blocks):                   # Kolize nepřítele se stěnami
        for block in blocks:                                   # Pro každý blok
            if self.rect.colliderect(block.rect):              # Pokud se překrývají
                if vel_x > 0:                                  # Šel doprava
                    self.rect.right = block.rect.left          # Zastaví
                    self.vel_x = 0                             # Stojí
                elif vel_x < 0:                                # Šel doleva
                    self.rect.left = block.rect.right          # Zastaví
                    self.vel_x = 0                             # Stojí
                if vel_y > 0:                                  # Šel dolů
                    self.rect.bottom = block.rect.top          # Zastaví
                    self.vel_y = 0                             # Stojí
                elif vel_y < 0:                                # Šel nahoru
                    self.rect.top = block.rect.bottom          # Zastaví
                    self.vel_y = 0                             # Stojí

    def update(self, blocks, camera=None):                     # Hlavní update volaný každý snímek
        if self.is_dead():                                     # Pokud je hráč mrtvý
            self.vel_x = 0                                     # Stojí
            self.vel_y = 0                                     # Stojí
            self.current_animation = 'death'                   # Přepne na animaci smrti
            frames = self.animation_frames[self.current_animation] # Získá framy aktuální animace
            if int(self.frame_index) < len(frames) - 1:        # Pokud ještě není na posledním framu
                self.frame_index += self.animation_speed       # Posune animaci dál
            self.image = frames[int(self.frame_index)]         # Nastaví aktuální obrázek
            return                                             # Ukončí update (mrtvý hráč nic jiného nedělá)

        self.handle_input(camera)                              # Zpracuje vstup z klávesnice/myši
        # top-down -> žádná gravitace ve hráči                  # top-down -> žádná gravitace ve hráči
        self.move(blocks)                                      # Provede pohyb s kolizemi

        # Aktualizace útoku a cooldownu                         # Aktualizace útoku a cooldownu
        if self.attacking:                                     # Pouze pokud probíhá útok
            self.attack_timer -= 1                             # Sníží časovač útoku
            if self.attack_timer <= 0:                         # Pokud útok skončil
                self.attacking = False                         # Ukončí útok
        if self.attack_cooldown > 0:                           # Pokud běží cooldown
            self.attack_cooldown -= 1                          # Sníží cooldown

        if self.hit_cooldown > 0:                              # Pokud běží imunita po zásahu
            self.hit_cooldown -= 1                             # Sníží imunitu

        # Health regen                                          # Health regen
        if self.health < self.max_health and not self.is_dead(): # Pokud hráč žije a nemá plné HP
            self.health_regen_timer += 1                       # Zvyšuje timer regenerace
            if self.health_regen_timer >= self.health_regen_rate: # Pokud timer dosáhl limitu
                self.heal(self.health_regen_amount)            # Doplní HP hráči
                self.health_regen_timer = 0                    # Resetuje timer
        else:                                                  # Pokud se nevlezla
            self.health_regen_timer = 0                        # Resetuje timer

        # Damage boost timer                                    # Damage boost timer
        if self.damage_boost_timer > 0:                        # Pokud je aktivní damage boost
            self.damage_boost_timer -= 1                       # Sníží timer
            if self.damage_boost_timer <= 0:                   # Pokud boost vypršel
                self.damage_boost = 1                          # Resetuje násobič na 1 (normální)

        # Fire ring timer                                       # Fire ring timer
        if self.fire_ring_active > 0:                          # Pokud běží timer ohnivého kruhu
            self.fire_ring_active -= 1                         # Zmenšuje ho o 1 každý snímek

        # Lightning visual timer                                # Lightning visual timer
        if self.lightning_timer > 0:                           # Pokud svítí blesk
            self.lightning_timer -= 1                          # Zkracuje dobu zobrazení o 1
            if self.lightning_timer <= 0:                      # TODO_COMMENT
                self.lightning_bolts = []                      # Seznam blesků čekajících na vykreslení

        # Animace                                               # Animace
        if self.attacking:                                     # Pouze pokud probíhá útok
            self.current_animation = 'attack'                  # Animace útoku
        elif self.vel_x != 0 or self.vel_y != 0:               # Pokud se hráč pohybuje
            self.current_animation = 'walk'                    # Animace chůze
        else:                                                  # Pokud se nevlezla
            self.current_animation = 'idle'                    # Animace stání (dýchání)

        frames = self.animation_frames[self.current_animation] # Získá framy aktuální animace
        self.frame_index = (self.frame_index + self.animation_speed) % len(frames) # Cyklické procházení framů
        self.image = frames[int(self.frame_index)]             # Nastaví aktuální obrázek

        # Otočení podle směru                                   # Otočení podle směru
        if not self.facing_right:                              # Pokud hráč míří doleva
            self.image = pygame.transform.flip(self.image, True, False) # Horizontální převrácení obrázku

        # Hraniční kontrola světa je v main()                   # Hraniční kontrola světa je v main()

    def point_in_swing(self, px, py):                          # Zkontroluje, zda bod (px, py) je v oblouku švihu
        ox, oy = self.rect.center                              # Střed hráče
        dx = px - ox                                           # Rozdíl X od hráče k bodu
        dy = py - oy                                           # Rozdíl Y od hráče k bodu
        dist = math.hypot(dx, dy)                              # Vzdálenost
        reach = self.get_sword_reach()                         # Použije dynamický dosah místo statické konstanty
        if dist > reach * 2:                                   # Výpočet kontroluje, jestli je cíl dostatečně blízko
            return False                                       # Mimo dosah
        ang = math.degrees(math.atan2(dy, dx))                 # Úhel od hráče k bodu (ve stupních)
        diff = (ang - self.attack_angle + 180) % 360 - 180     # Rozdíl úhlů (-180 až +180)
        return abs(diff) <= 90                                 # True pokud je rozdíl do ±90° (polokruh švihu)

    def attack_hits(self, enemy):                              # Zkontroluje, zda útok zasáhl nepřítele
        if not self.attacking:                                 # Pokud neútočíme
            return False                                       # Mimo dosah
        ox, oy = self.rect.center                              # Střed hráče
        ex, ey = enemy.rect.center                             # Střed nepřítele
        dist = math.hypot(ex - ox, ey - oy)                    # Vzdálenost hráč-nepřítel
        reach = self.get_sword_reach()                         # Použije dynamický dosah místo statické konstanty
        if dist > reach * 2:                                   # Výpočet kontroluje, jestli je cíl dostatečně blízko
            return False                                       # Mimo dosah
        return self.point_in_swing(ex, ey)                     # Zkontroluje úhel švihu

    def draw_attack(self, screen, camera):                     # Vykreslí srpkovitý slash efekt na obrazovku
        if self.attacking:                                     # Pouze pokud probíhá útok
            center = camera.apply(self).center                 # Střed hráče na obrazovce (po aplikaci kamery)
            reach = self.get_sword_reach()                     # Použije dynamický dosah místo statické konstanty
            arc_radius = reach * 1.8                           # Poloměr útočného švihu na základě reach
            blade_length = reach * 1.6                         # Délka čepele

            # Surface pro celý efekt                            # Surface pro celý efekt
            surf_size = int(arc_radius * 4)                    # Rozměry dočasné vrstvy pro nakreslení
            swoosh_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA) # Průhledná surface

            progress = 1.0 - (self.attack_timer / ATTACK_DURATION) # Průběh útoku (0.0 → 1.0)
            # Easing – zrychlení na začátku, zpomalení na konci # Easing – zrychlení na začátku, zpomalení na konci
            eased = 1.0 - (1.0 - progress) ** 2.5              # Easing funkce (rozjezd a zpomalení animace švihu)

            half_swing = 60                                    # Polovina úhlu švihu (celkem 120 stupňů)
            current_angle = self.attack_angle - half_swing + (half_swing * 2) * eased # Výpočet aktuálního úhlu

            scx = surf_size // 2                               # X střed surface
            scy = surf_size // 2                               # Y střed surface

            # Barva podle boostu                                # Barva podle boostu
            if getattr(self, 'damage_boost_timer', 0) > 0:     # Pokud je aktivní boost
                trail_color = (255, 140, 40)                   # Oranžová barva stopy švihu
                blade_color = (255, 200, 100)                  # Žlutá barva okraje čepele
                glow_color = (255, 100, 20)                    # Oranžovo-červená barva záře
            else:                                              # Pokud se nevlezla
                trail_color = (120, 200, 255)                  # Ledově modrá barva stopy
                blade_color = (200, 230, 255)                  # Bělavě-modrá barva čepele
                glow_color = (80, 160, 255)                    # Sytě modrá záře

            # ==========================================        # ==========================================
            # 1) SWOOSH TRAIL – vějířovitý trail za čepelí      # 1) SWOOSH TRAIL – vějířovitý trail za čepelí
            # ==========================================        # ==========================================
            trail_segments = 18                                # Počet úseků pro vyhlazení stopy švihu
            trail_start_angle = self.attack_angle - half_swing # Počáteční úhel, odkud stopa začíná
            trail_extent = (half_swing * 2) * eased            # Velikost vykreslené stopy v závislosti na postupu

            if trail_extent > 2:                               # Kreslí stopu, jen pokud je viditelná (rozmáchl se)
                # Vnější oblouk (ostrá hrana)                   # Vnější oblouk (ostrá hrana)
                for layer in range(3):                         # Stopa se skládá ze 3 vrstev pro plynulý průhledný okraj
                    pts_outer = []                             # Vnější body (horní oblouk stopy)
                    pts_inner = []                             # Vnitřní body (spodní oblouk stopy)
                    # Každá vrstva je tenčí a světlejší         # Každá vrstva je tenčí a světlejší
                    layer_radius = arc_radius - layer * 4      # Zmenšování poloměru pro vnitřní vrstvy
                    layer_thickness_max = (arc_radius * 0.35) * (1.0 - layer * 0.3) # Snižování tloušťky vrstev

                    for i in range(trail_segments + 1):        # Sestavení mnohoúhelníku (polygon) stopy
                        t = i / trail_segments                 # Procento aktuálního bodu úseku (0..1)
                        a_deg = trail_start_angle + t * trail_extent # Interpolovaný úhel v úseku
                        a_rad = math.radians(a_deg)            # Převod úhlu na radiány

                        # Tloušťka roste od nuly na začátku k maximu uprostřed a klesá # Tloušťka roste od nuly na začátku k maximu uprostřed a klesá
                        # ale přední hrana (kde je čepel) je silnější # ale přední hrana (kde je čepel) je silnější
                        shape = math.sin(t * math.pi) ** 0.6   # Kulatý tvar šířky stopy (rozšiřuje se uprostřed)
                        fade = t                               # Trail zesiluje směrem k čepeli
                        thickness = layer_thickness_max * shape * max(0.15, fade) # Výpočet tloušťky konkrétního bodu

                        ox = scx + math.cos(a_rad) * layer_radius # Výpočet vnější X souřadnice
                        oy = scy + math.sin(a_rad) * layer_radius # Výpočet vnější Y souřadnice
                        pts_outer.append((ox, oy))             # Přidání do pole

                        ix = scx + math.cos(a_rad) * (layer_radius - thickness) # Výpočet vnitřní X souřadnice
                        iy = scy + math.sin(a_rad) * (layer_radius - thickness) # Výpočet vnitřní Y souřadnice
                        pts_inner.append((ix, iy))             # Přidání do pole

                    pts_inner.reverse()                        # Otočení pořadí vnitřních bodů kvůli uzavření polygonu
                    poly = pts_outer + pts_inner               # Složení obvodu stopy

                    if len(poly) >= 3:                         # Nakreslení polygonu
                        # Vnější vrstva = trail_color, vnitřní = bílá # Vnější vrstva = trail_color, vnitřní = bílá
                        if layer == 0:                         # Nejširší (nejslabší) vrstva
                            a = max(0, int(130 * (1.0 - progress * 0.7))) # Vypočtení průhlednosti (mizení v čase)
                            col = (*trail_color, a)            # Namíchání barvy a alphy
                        elif layer == 1:                       # Prostřední vrstva
                            a = max(0, int(180 * (1.0 - progress * 0.6))) # Alpha pro tuto vrstvu
                            col = (*blade_color, a)            # Nastavení barvy
                        else:                                  # Pokud se nevlezla
                            a = max(0, int(220 * (1.0 - progress * 0.5))) # Alpha
                            col = (255, 255, 255, a)           # Střed úderu je bílý
                        pygame.draw.polygon(swoosh_surf, col, poly) # Kreslení samotného polygonu

            # ==========================================        # ==========================================
            # 2) MEČI / BLADE – vykreslení samotného meče       # 2) MEČI / BLADE – vykreslení samotného meče
            # ==========================================        # ==========================================
            blade_angle_rad = math.radians(current_angle)      # Úhel samotné zbraně (špička na konci švihu)

            # Pozice špičky a base meče                         # Pozice špičky a base meče
            tip_x = scx + math.cos(blade_angle_rad) * blade_length # Výpočet pozice X špičky
            tip_y = scy + math.sin(blade_angle_rad) * blade_length # Výpočet pozice Y špičky
            guard_x = scx + math.cos(blade_angle_rad) * (blade_length * 0.3) # X pozice záštity
            guard_y = scy + math.sin(blade_angle_rad) * (blade_length * 0.3) # Y pozice záštity
            pommel_x = scx + math.cos(blade_angle_rad) * (blade_length * 0.12) # X pozice hlavice na konci rukojeti
            pommel_y = scy + math.sin(blade_angle_rad) * (blade_length * 0.12) # Y pozice hlavice

            # Kolmý vektor pro šířku čepele                     # Kolmý vektor pro šířku čepele
            perp_x = -math.sin(blade_angle_rad)                # Směr kolmý k meči pro získání tloušťky (X)
            perp_y = math.cos(blade_angle_rad)                 # Kolmý směr (Y)

            blade_width = 4.0                                  # Tloušťka čepele
            guard_width = 8.0                                  # Šířka záštity

            # Čepel (lichoběžník – úzká u špičky, širší u záštity) # Čepel (lichoběžník – úzká u špičky, širší u záštity)
            blade_poly = [                                     # Vytvoření bodů pro tvar čepele meče
                (tip_x + perp_x * 1, tip_y + perp_y * 1),      # Konec na jedné straně špičky
                (tip_x - perp_x * 1, tip_y - perp_y * 1),      # Konec na druhé straně
                (guard_x - perp_x * blade_width, guard_y - perp_y * blade_width), # Spodek na jedné straně
                (guard_x + perp_x * blade_width, guard_y + perp_y * blade_width), # Spodek na druhé straně
            ]                                                  # Konec polygonu záštity
            # Stín čepele (tmavší)                              # Stín čepele (tmavší)
            pygame.draw.polygon(swoosh_surf, (140, 150, 170, 220), blade_poly) # Vykreslí tmavší základ čepele
            # Světlý lesk na čepeli                             # Světlý lesk na čepeli
            highlight_poly = [                                 # Vytvoření bodů pro lesk (vnitřní část) čepele
                (tip_x + perp_x * 0.5, tip_y + perp_y * 0.5),  # Špička (blíž středu)
                (tip_x - perp_x * 0.3, tip_y - perp_y * 0.3),  # Druhá špička
                (guard_x - perp_x * (blade_width * 0.4), guard_y - perp_y * (blade_width * 0.4)), # Zúžený spodek
                (guard_x + perp_x * (blade_width * 0.6), guard_y + perp_y * (blade_width * 0.6)), # Zúžený spodek z druhé strany
            ]                                                  # Konec polygonu záštity
            pygame.draw.polygon(swoosh_surf, (220, 230, 245, 240), highlight_poly) # Vykreslí světlejší část meče

            # Záštita (guard) – krátká příčka                   # Záštita (guard) – krátká příčka
            guard_pts = [                                      # Tvar záštity meče
                (guard_x + perp_x * guard_width, guard_y + perp_y * guard_width), # Jeden roh
                (guard_x - perp_x * guard_width, guard_y - perp_y * guard_width), # Druhý roh
                (guard_x - perp_x * guard_width - math.cos(blade_angle_rad) * 2, # Tloušťka dozadu
                 guard_y - perp_y * guard_width - math.sin(blade_angle_rad) * 2), # TODO_COMMENT
                (guard_x + perp_x * guard_width - math.cos(blade_angle_rad) * 2, # Tloušťka dozadu, druhý konec
                 guard_y + perp_y * guard_width - math.sin(blade_angle_rad) * 2), # TODO_COMMENT
            ]                                                  # Konec polygonu záštity
            pygame.draw.polygon(swoosh_surf, (200, 170, 50, 230), guard_pts) # Vykreslí zlatou záštitu

            # Rukojeť                                           # Rukojeť
            pygame.draw.line(swoosh_surf, (110, 70, 30, 220),  # Vykreslí hnědou rukojeť
                             (int(guard_x), int(guard_y)),     # Bod pod záštitou
                             (int(pommel_x), int(pommel_y)), 4) # Bod nad hlavicí a tloušťka
            # Hlavice                                           # Hlavice
            pygame.draw.circle(swoosh_surf, (200, 170, 50, 200), # Hlavice zbraně (koule)
                               (int(pommel_x), int(pommel_y)), 3) # Poloměr

            # ==========================================        # ==========================================
            # 3) GLOW na špičce čepele                          # 3) GLOW na špičce čepele
            # ==========================================        # ==========================================
            glow_alpha = max(0, int(160 * (1.0 - progress)))   # Zářič na špičce meče – alpha kanál slábne s časem
            glow_r = int(12 + 6 * math.sin(progress * math.pi)) # Poloměr záře osciluje uprostřed švihu
            if glow_r > 2:                                     # Pokud je záře dostatečně velká
                glow_s = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA) # Surface pro rozostřenou kuličku na špičce
                pygame.draw.circle(glow_s, (*glow_color, glow_alpha // 2), (glow_r * 2, glow_r * 2), glow_r * 2) # Širší a průhlednější záře
                pygame.draw.circle(glow_s, (255, 255, 255, glow_alpha), (glow_r * 2, glow_r * 2), glow_r) # Malé bílé jádro
                swoosh_surf.blit(glow_s, (int(tip_x) - glow_r * 2, int(tip_y) - glow_r * 2)) # Spojení se špičkou meče

            # ==========================================        # ==========================================
            # 4) JISKRY / sparks vyletující ze špičky           # 4) JISKRY / sparks vyletující ze špičky
            # ==========================================        # ==========================================
            if progress < 0.85:                                # Během většiny úderu vytváří jiskry
                num_sparks = 4                                 # Množství jisker generovaných na frame
                for s in range(num_sparks):                    # Generuje částice
                    spark_spread = random.uniform(-0.5, 0.5)   # Úhel rozptylu od hrany
                    spark_dist = random.uniform(4, 16)         # Vzdálenost odklonu jiskry od hrany
                    spark_a = blade_angle_rad + spark_spread   # Skutečný úhel výletu
                    sx = tip_x + math.cos(spark_a) * spark_dist # X pozice jiskry
                    sy = tip_y + math.sin(spark_a) * spark_dist # Y pozice jiskry
                    spark_alpha = random.randint(120, 220)     # Náhodná průhlednost
                    spark_size = random.randint(1, 3)          # Náhodná velikost
                    spark_col = (255, 255, random.randint(150, 255), spark_alpha) # Žlutobílá barva
                    pygame.draw.circle(swoosh_surf, spark_col, (int(sx), int(sy)), spark_size) # Nakreslí jiskru

            # ==========================================        # ==========================================
            # 5) IMPACT FLASH na konci švihu                    # 5) IMPACT FLASH na konci švihu
            # ==========================================        # ==========================================
            if progress > 0.8:                                 # Ke konci švihu (když čepel dopadne)
                impact_progress = (progress - 0.8) / 0.2       # Jak daleko jsme v tomto krátkém úseku dopadu (0..1)
                impact_alpha = max(0, int(100 * (1.0 - impact_progress))) # Průhlednost rázové vlny
                impact_r = int(20 + 30 * impact_progress)      # Poloměr rázové vlny se rychle zvětšuje
                if impact_alpha > 0 and impact_r > 0:          # Vykresluje vlnu na konci
                    imp_surf = pygame.Surface((impact_r * 2, impact_r * 2), pygame.SRCALPHA) # Plátno pro vlnu dopadu
                    pygame.draw.circle(imp_surf, (*trail_color, impact_alpha // 3), # Průhlednější široký kruh
                                       (impact_r, impact_r), impact_r) # TODO_COMMENT
                    pygame.draw.circle(imp_surf, (255, 255, 255, impact_alpha // 2), # Světlejší vnitřní okraj
                                       (impact_r, impact_r), impact_r // 2) # TODO_COMMENT
                    # Pozice impactu = konec švihu              # Pozice impactu = konec švihu
                    end_angle_rad = math.radians(self.attack_angle + half_swing) # Místo, kam meč "dopadl"
                    imp_x = scx + math.cos(end_angle_rad) * arc_radius * 0.7 # X souřadnice konce
                    imp_y = scy + math.sin(end_angle_rad) * arc_radius * 0.7 # Y souřadnice konce
                    swoosh_surf.blit(imp_surf, (int(imp_x) - impact_r, int(imp_y) - impact_r)) # Nakreslí ráz na cíl meče

            screen.blit(swoosh_surf, swoosh_surf.get_rect(center=center)) # Vykreslí slash na obrazovku (centrovaný na hráče)

    def draw_fire_ring(self, screen, camera):                  # Vykreslí prstenec ohně (pokud je aktivní zbraň Fire Ring)
        """Vykreslí fire ring efekt kolem hráče."""            # Docstring
        if self.fire_ring_active > 0:                          # Pokud běží timer ohnivého kruhu
            center = camera.apply(self).center                 # Střed hráče na obrazovce (po aplikaci kamery)
            max_dur = max(1, self.fire_ring_max_duration)      # Prevence dělení nulou
            progress = 1.0 - (self.fire_ring_active / max_dur) # Procento dokončení prstence, od 0 k 1 (mizí)
            expand = min(1.0, progress * 4)                    # Prstenec rychle naroste (ve 25% trvání dosáhne plné šířky)
            fr_radius = int(self.fire_ring_radius * expand)    # Aktuální velikost kruhu v pixelech
            alpha = int(180 * (self.fire_ring_active / max_dur)) # Rychlé zprůhledňování, jak hasne oheň

            if fr_radius > 5:                                  # Kreslí se, jen když je dostatečně velký
                fr_size = fr_radius * 2 + 30                   # Rozměr vrstvy (+30 na jiskry mimo oheň)
                fr_surf = pygame.Surface((fr_size, fr_size), pygame.SRCALPHA) # Plátno s průhledností
                cp = (fr_size // 2, fr_size // 2)              # Střed uvnitř této vrstvy

                # Vnější kruh                                   # Vnější kruh
                pygame.draw.circle(fr_surf, (255, 80, 0, max(0, alpha // 2)), cp, fr_radius, 5) # Vnější červený okraj (široký)
                # Vnitřní záře                                  # Vnitřní záře
                pygame.draw.circle(fr_surf, (255, 180, 50, max(0, alpha)), cp, max(0, fr_radius - 4), 3) # Vnitřní žlutý okraj (tenký)

                # Ohnivé částice kolem kruhu                    # Ohnivé částice kolem kruhu
                num_particles = 12                             # Počet létajících ohnivých částic prstence
                for i in range(num_particles):                 # Vytvoření částic po obvodu
                    angle = math.radians(i * (360 / num_particles) + self.fire_ring_active * 7) # Úhel závisí na čase a rotuje
                    px = cp[0] + int(math.cos(angle) * fr_radius) # Pozice X částice
                    py = cp[1] + int(math.sin(angle) * fr_radius) # Pozice Y částice
                    p_alpha = max(0, min(255, alpha + 30))     # Částice jsou méně průhledné než okraj
                    c_val = 120 + (i * 25) % 80                # Střídání barvy červená/oranžová
                    pygame.draw.circle(fr_surf, (255, c_val, 0, p_alpha), (px, py), 5) # Vykreslí plamínek
                    # Menší jiskra                              # Menší jiskra
                    px2 = cp[0] + int(math.cos(angle + 0.3) * (fr_radius - 8)) # O něco hlouběji a s jiným úhlem (vnitřní plamínky)
                    py2 = cp[1] + int(math.sin(angle + 0.3) * (fr_radius - 8)) # Vnitřní Y pozice
                    pygame.draw.circle(fr_surf, (255, 255, 100, max(0, p_alpha // 2)), (px2, py2), 2) # Žluté jádro plamínku

                screen.blit(fr_surf, (center[0] - fr_size // 2, center[1] - fr_size // 2)) # Spojení na herní obrazovku

    def draw_lightning(self, screen, camera):                  # Vykreslí blesky mezi hráčem a zasaženými cíli (zbraň Lightning)
        """Vykreslí blesky mezi hráčem a zasaženými nepřáteli.""" # Docstring
        if self.lightning_timer > 0 and self.lightning_bolts:  # Pokud je blesk v chodu
            alpha_factor = self.lightning_timer / 15.0         # Vypočítá slábnutí blesku v čase (15 snímků)
            for (sx, sy), (ex, ey) in self.lightning_bolts:    # Prochází seznam linií blesku (od hráče k nepříteli)
                # Převod na souřadnice kamery                   # Převod na souřadnice kamery
                s_screen = (int(sx + camera.rect.x), int(sy + camera.rect.y)) # Zohlední kameru pro zdroj (X,Y)
                e_screen = (int(ex + camera.rect.x), int(ey + camera.rect.y)) # Zohlední kameru pro cíl (X,Y)

                # Zubaté body blesku                            # Zubaté body blesku
                points = [s_screen]                            # Přidá počáteční bod do čar blesku
                segments = 6                                   # Blesk se "zlomí" 6krát po cestě
                for i in range(1, segments):                   # Rozdělení na menší segmenty
                    t = i / segments                           # Pozice podél linie (0..1)
                    mx = int(s_screen[0] + (e_screen[0] - s_screen[0]) * t + random.randint(-10, 10)) # Mezilehlý X bod (s náhodnou výchylkou)
                    my = int(s_screen[1] + (e_screen[1] - s_screen[1]) * t + random.randint(-10, 10)) # Mezilehlý Y bod (s výchylkou)
                    points.append((mx, my))                    # Vloží zlomený bod
                points.append(e_screen)                        # Přidá koncový cíl

                # Hlavní blesk                                  # Hlavní blesk
                width = max(1, int(3 * alpha_factor))          # Tloušťka se v průběhu bliknutí mění
                pygame.draw.lines(screen, (100, 180, 255), False, points, width) # Nakreslí modrou vrstvu blesku
                # Bílý střed                                    # Bílý střed
                pygame.draw.lines(screen, (220, 240, 255), False, points, max(1, width - 1)) # Nakreslí bílý středový pruh blesku

                # Záře kolem cíle                               # Záře kolem cíle
                glow_radius = int(12 * alpha_factor)           # Okolo koncového cíle udělá světelnou záři (rána bleskem)
                if glow_radius > 2:                            # Větší než bod
                    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA) # Plátno s podporou alfa pro záři
                    glow_alpha = int(100 * alpha_factor)       # Zeslabení alfa barvy
                    pygame.draw.circle(glow_surf, (100, 180, 255, glow_alpha), (glow_radius, glow_radius), glow_radius) # Vykreslení bleskové koule
                    screen.blit(glow_surf, (e_screen[0] - glow_radius, e_screen[1] - glow_radius)) # Aplikace na plátno

    def take_damage(self, amount):                             # uvnitř Enemy (__init__ atp)
        self.health -= amount                                  # Odečte zdraví
        if self.health < 0:                                    # Životy nesmí být záporné
            self.health = 0                                    # Minimum je 0

    def heal(self, amount):                                    # Hráč se vyléčí
        self.health = min(self.health + amount, self.max_health) # Přidá životy, max je max_health

    def add_xp(self, amount):                                  # Přidá zkušenostní body
        self.xp += amount                                      # Zvýší XP
        while self.xp >= self.max_xp:                          # Cyklus – může přeskočit víc levelů najednou
            self.xp -= self.max_xp                             # Odečte potřebné XP
            self.level += 1                                    # Zvýší level
            self.max_xp = int(self.max_xp * 1.5)               # Další level potřebuje 1.5× více XP
            self.level_up_pending += 1                         # Přidá čekající level-up (zobrazí upgrade menu)

    def is_dead(self):                                         # Kontrola smrti nepřítele
        return self.health <= 0                                # True pokud HP ≤ 0

# Základní třída pro nepřítele                                  # Základní třída pro nepřítele
class Enemy(pygame.sprite.Sprite):                             # Úprava třídy Enemy pro blikání po zásahu atd.
    def __init__(self, x, y, enemy_type='walker'):             # Konstruktor – pozice a typ nepřítele
        super().__init__()                                     # Volání rodičovského konstruktoru Sprite
        self.enemy_type = enemy_type                           # Typ nepřítele ('walker', 'flying', 'tank', 'fast', 'boss')
        self.width = ENEMY_SIZE * 2 if enemy_type == 'boss' else ENEMY_SIZE # Boss je 2× větší (56 px)
        self.height = ENEMY_SIZE * 2 if enemy_type == 'boss' else ENEMY_SIZE # Boss je 2× větší
        self.rect = pygame.Rect(x, y, self.width, self.height) # Obdélník nepřítele ve světě
        self.vel_x = 0                                         # Stojí
        self.vel_y = 0                                         # Stojí

        # Set different health based on enemy type              # Set different health based on enemy type
        if self.enemy_type == 'walker':                        # Walker – zelený slime
            self.health = 30                                   # default fallback                   # Fallback pokud enemy type není rozpoznán
            self.xp_value = 5                                  # Default 5 XP
            self.speed = ENEMY_SPEED                           # Default rychlost
            self.damage = 15                                   # Default poškození
        elif self.enemy_type == 'flying':                      # Létající nepřítel
            self.health = 20                                   # 20 HP (méně)
            self.xp_value = 5                                  # Default 5 XP
            self.speed = FLYING_ENEMY_SPEED                    # Pomalejší (1)
            self.damage = 10                                   # 10 poškození
        elif self.enemy_type == 'tank':                        # Tank – šedý golem
            self.health = 100                                  # 100 HP (hodně)
            self.xp_value = 15                                 # Dá 15 XP (více)
            self.speed = ENEMY_SPEED * 0.6                     # Pomalý (1.2)
            self.damage = 30                                   # 30 poškození (hodně)
        elif self.enemy_type == 'fast':                        # Fast je lehký
            self.health = 10                                   # 10 HP (málo)
            self.xp_value = 5                                  # Default 5 XP
            self.speed = ENEMY_SPEED * 1.5                     # Rychlý (3)
            self.damage = 5                                    # 5 poškození (málo)
        elif self.enemy_type == 'boss':                        # Boss je těžký
            self.health = 500                                  # 500 HP (extrémně)
            self.xp_value = 150                                # Dá 150 XP (hodně)
            self.speed = ENEMY_SPEED * 0.8                     # Mírně pomalejší (1.6)
            self.damage = 40                                   # 40 poškození
        else:                                                  # Pokud se nevlezla
            self.health = 30                                   # default fallback                   # Fallback pokud enemy type není rozpoznán
            self.xp_value = 5                                  # Default 5 XP
            self.speed = ENEMY_SPEED                           # Default rychlost
            self.damage = 15                                   # Default poškození

        self.facing_right = random.choice([True, False])       # Náhodný počáteční směr
        self.hit_flash = 0                                     # Časovač blikání při zásahu (snímky)
        self.knockback_timer = 0                               # Časovač knockbacku (odskok)

        # Vytvoření vzhledu                                     # Vytvoření vzhledu
        self.image = pygame.Surface((self.width, self.height)) # Surface pro obrázek
        self.draw_enemy()                                      # Vykreslí tvar nepřítele

    def draw_enemy(self):                                      # Vykreslí grafiku nepřítele podle typu
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # Průhledná surface
        self.image.fill((0, 0, 0, 0))                          # Průhledné pozadí
        # Shadow                                                # Shadow
        pygame.draw.ellipse(self.image, (0, 0, 0, 80), (4, 24, 20, 6)) # Stín pod nepřítelem

        if self.enemy_type == 'walker':                        # Walker – zelený slime
            # Slime / Zombie                                    # Slime / Zombie
            pygame.draw.rect(self.image, (34, 139, 34), (4, 8, 20, 18), border_radius=6) # Zelené tělo
            pygame.draw.rect(self.image, (0, 100, 0), (4, 8, 20, 18), 2, border_radius=6) # Tmavší okraj
            pygame.draw.circle(self.image, (255, 0, 0), (10, 14), 3) # Levé červené oko
            pygame.draw.circle(self.image, (255, 0, 0), (18, 14), 3) # Pravé červené oko
            pygame.draw.rect(self.image, (0, 0, 0), (10, 20, 8, 2)) # Ústa (černý obdélníček)
        elif self.enemy_type == 'flying':                      # Létající nepřítel
            # Bat                                               # Bat
            pygame.draw.circle(self.image, (75, 0, 130), (14, 14), 8) # Tělo (fialový kruh)
            pygame.draw.polygon(self.image, (138, 43, 226), [(6, 14), (-4, 4), (2, 20)]) # Levé křídlo
            pygame.draw.polygon(self.image, (138, 43, 226), [(22, 14), (32, 4), (26, 20)]) # Pravé křídlo
            pygame.draw.circle(self.image, YELLOW, (11, 12), 2) # Levé žluté oko
            pygame.draw.circle(self.image, YELLOW, (17, 12), 2) # Pravé žluté oko
        elif self.enemy_type == 'tank':                        # Tank – šedý golem
            # Golem                                             # Golem
            pygame.draw.rect(self.image, (105, 105, 105), (2, 4, 24, 24), border_radius=4) # Šedé tělo
            pygame.draw.rect(self.image, (50, 50, 50), (2, 4, 24, 24), 3, border_radius=4) # Tmavší okraj
            pygame.draw.circle(self.image, (255, 165, 0), (10, 10), 4) # Levé oranžové oko
            pygame.draw.circle(self.image, (255, 165, 0), (18, 10), 4) # Pravé oranžové oko
            pygame.draw.rect(self.image, (0, 0, 0), (8, 18, 12, 4)) # Ústa
        elif self.enemy_type == 'fast':                        # Fast je lehký
            # Ghost/small eye                                   # Ghost/small eye
            pygame.draw.circle(self.image, (200, 200, 255, 180), (14, 14), 10) # Světle modrý kruh (poloprůhledný)
            pygame.draw.circle(self.image, (255, 0, 0), (14, 14), 4) # Červená duhovka
            pygame.draw.circle(self.image, (0, 0, 0), (14, 14), 2) # Černá zornička
        elif self.enemy_type == 'boss':                        # Boss je těžký
            # Boss                                              # Boss
            pygame.draw.rect(self.image, (150, 0, 0), (4, 4, self.width-8, self.height-8), border_radius=8) # Červené tělo
            pygame.draw.rect(self.image, (50, 0, 0), (4, 4, self.width-8, self.height-8), 4, border_radius=8) # Tmavší okraj
            pygame.draw.circle(self.image, (255, 255, 0), (self.width//3, self.height//3), 6) # Levé žluté oko
            pygame.draw.circle(self.image, (255, 255, 0), (2*self.width//3, self.height//3), 6) # Pravé žluté oko
            pygame.draw.rect(self.image, (0, 0, 0), (self.width//4, 2*self.height//3, self.width//2, 8)) # Ústa

        mask = pygame.mask.from_surface(self.image)            # Vytvoří masku z obrázku (pixely vs. průhlednost)
        self.flash_image = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)) # Bílá verze pro blikání



    def move(self, blocks):                                    # Pohyb nepřítele
        # X                                                     # X
        self.rect.x += self.vel_x                              # Posun X
        self.collide(self.vel_x, 0, blocks)                    # Kolize X
        # Y                                                     # Y
        self.rect.y += self.vel_y                              # Posun Y
        self.collide(0, self.vel_y, blocks)                    # Kolize Y

    def collide(self, vel_x, vel_y, blocks):                   # Kolize nepřítele se stěnami
        for block in blocks:                                   # Pro každý blok
            if self.rect.colliderect(block.rect):              # Pokud se překrývají
                if vel_x > 0:                                  # Šel doprava
                    self.rect.right = block.rect.left          # Zastaví
                    self.vel_x = -self.speed                   # Pohyb doleva
                    self.facing_right = False                  # Otočí se doleva
                elif vel_x < 0:                                # Šel doleva
                    self.rect.left = block.rect.right          # Zastaví
                    self.vel_x = self.speed                    # Pohyb doprava
                    self.facing_right = True                   # Určuje směr pohledu pro animaci útoku
                if vel_y > 0:                                  # Šel dolů
                    self.rect.bottom = block.rect.top          # Zastaví
                    self.vel_y = -self.speed                   # Obrátí směr
                elif vel_y < 0:                                # Šel nahoru
                    self.rect.top = block.rect.bottom          # Zastaví
                    self.vel_y = self.speed                    # Obrátí směr

    def update(self, blocks, player=None):                     # Hlavní update nepřítele
        if self.hit_flash > 0:                                 # Pokud běží hit flash efekt
            self.hit_flash -= 1                                # Sníží časovač blikání

        if self.knockback_timer > 0:                           # Pokud běží knockback
            self.knockback_timer -= 1                          # Sníží časovač
            self.vel_x *= 0.85                                 # Zpomalení X (tření)
            self.vel_y *= 0.85                                 # Zpomalení Y (tření)
        elif self.enemy_type in ['walker', 'tank', 'fast', 'boss']: # Pozemní nepřátelé
            # Chodec: pravidelně chase hráče, s malou plynulou korekcí # Chodec: pravidelně chase hráče, s malou plynulou korekcí
            if player:                                         # Pokud existuje hráč
                dx = player.rect.centerx - self.rect.centerx   # Vzdálenost X
                dy = player.rect.centery - self.rect.centery   # Vzdálenost Y
                dist = math.hypot(dx, dy)                      # Vzdálenost
                if dist != 0:                                  # Ochrana proti dělení nulou
                    self.vel_x = (dx / dist) * self.speed      # Směr k hráči (X)
                    self.vel_y = (dy / dist) * self.speed      # Směr k hráči (Y)
                else:                                          # Pokud se nevlezla
                    self.vel_x, self.vel_y = 0, 0              # Nehýbe se
            else:                                              # Pokud se nevlezla
                if self.facing_right:                          # Jde doprava
                    self.vel_x = self.speed                    # Pohyb doprava
                else:                                          # Pokud se nevlezla
                    self.vel_x = -self.speed                   # Pohyb doleva
                self.vel_y = 0                                 # Stojí
        elif self.enemy_type == 'flying':                      # Létající nepřítel
            # Létající: sleduje hráče (jednoduché přiblížení)   # Létající: sleduje hráče (jednoduché přiblížení)
            if player:                                         # Pokud existuje hráč
                dx = player.rect.centerx - self.rect.centerx   # Vzdálenost X
                dy = player.rect.centery - self.rect.centery   # Vzdálenost Y
                dist = math.hypot(dx, dy)                      # Vzdálenost
                if dist != 0:                                  # Ochrana proti dělení nulou
                    self.vel_x = (dx / dist) * self.speed      # Směr k hráči (X)
                    self.vel_y = (dy / dist) * self.speed      # Směr k hráči (Y)
                else:                                          # Pokud se nevlezla
                    self.vel_x = 0                             # Stojí
                    self.vel_y = 0                             # Stojí


        self.move(blocks)                                      # Provede pohyb s kolizemi



    def take_damage(self, amount):                             # uvnitř Enemy (__init__ atp)
        self.health -= amount                                  # Odečte zdraví
        self.hit_flash = 6                                     # Zapne blikající bílý efekt na 6 snímků

    def apply_knockback(self, source_rect):                    # Aplikuje odskok od zdroje poškození
        dx = self.rect.centerx - source_rect.centerx           # Směr odskoku X (od hráče)
        dy = self.rect.centery - source_rect.centery           # Směr odskoku Y (od hráče)
        dist = math.hypot(dx, dy)                              # Vzdálenost
        if dist != 0:                                          # Ochrana proti dělení nulou
            kb_strength = 12.0                                 # Výchozí síla knockbacku
            if self.enemy_type == 'tank':                      # Tank je odolný
                kb_strength = 4.0                              # Menší knockback
            elif self.enemy_type == 'fast':                    # Fast je lehký
                kb_strength = 16.0                             # Větší knockback
            elif self.enemy_type == 'boss':                    # Boss je těžký
                kb_strength = 1.0                              # Minimální knockback
            self.vel_x = (dx / dist) * kb_strength             # Rychlost odskoku (X)
            self.vel_y = (dy / dist) * kb_strength             # Rychlost odskoku (Y)
            self.knockback_timer = 15                          # Knockback trvá 15 snímků

    def is_dead(self):                                         # Kontrola smrti nepřítele
        return self.health <= 0                                # True pokud HP ≤ 0

# Generátor dungeonu (místnosti a chodby)                       # Generátor dungeonu (místnosti a chodby)
def generate_dungeon(size):                                    # Parametr size = velikost mřížky (5 = 5×5 místností)
    # Vytvoříme mřížku místností (každá místnost je slovník s x,y,w,h a dveřmi) # Vytvoříme mřížku místností (každá místnost je slovník s x,y,w,h a dveřmi)
    rooms: List[RoomDict] = []                                 # Prázdný seznam místností
    for i in range(size):                                      # Pro každý sloupec mřížky
        for j in range(size):                                  # Pro každý řádek mřížky
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)   # Náhodná šířka místnosti (v blocích)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)   # Náhodná výška místnosti (v blocích)
            x = i * (ROOM_MAX_SIZE + 2) * BLOCK_SIZE           # Rozestup mezi místnostmi při generování na startu
            y = j * (ROOM_MAX_SIZE + 2) * BLOCK_SIZE           # Y pozice místnosti (s mezerami)
            rooms.append({                                     # Přidá místnost do seznamu
                'x': x, 'y': y,                                # Pozice
                'width': w * BLOCK_SIZE,                       # Šířka v pixelech
                'height': h * BLOCK_SIZE,                      # Výška v pixelech
                'grid_x': i, 'grid_y': j,                      # Pozice v mřížce
                'doors': []                                    # Prázdný seznam dveří
            })                                                 # Konec přidání

    # Propojení místností chodbami (jednoduché: každá místnost s pravým a dolním sousedem) # Propojení místností chodbami (jednoduché: každá místnost s pravým a dolním sousedem)

    for room in rooms:                                         # Pro každou místnost
        # Pravý soused                                          # Pravý soused
        right_room = next((r for r in rooms if r['grid_x'] == room['grid_x']+1 and r['grid_y'] == room['grid_y']), None) # Hledá souseda vpravo
        if right_room:                                         # Pokud existuje
            door_y = room['y'] + ((room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE # Y pozice dveří (uprostřed)
            door1 = (room['x'] + room['width'] - BLOCK_SIZE, door_y) # Dveře v aktuální místnosti
            door2 = (right_room['x'], right_room['y'] + ((right_room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE) # Dveře v sousedovi
            room['doors'].append(door1)                        # Přidá dveře
            right_room['doors'].append(door2)                  # Přidá dveře sousedovi


        # Dolní soused                                          # Dolní soused
        down_room = next((r for r in rooms if r['grid_x'] == room['grid_x'] and r['grid_y'] == room['grid_y']+1), None) # Hledá souseda dole
        if down_room:                                          # Pokud existuje
            door_x = room['x'] + ((room['width'] // 2) // BLOCK_SIZE) * BLOCK_SIZE # X pozice dveří (uprostřed)
            door1 = (door_x, room['y'] + room['height'] - BLOCK_SIZE) # Dveře v aktuální místnosti
            door2 = (door_x, down_room['y'])                   # Dveře v sousedovi
            room['doors'].append(door1)                        # Přidá dveře
            down_room['doors'].append(door2)                   # Přidá dveře sousedovi


    # Místnost už nerenderujeme jako složitý dungeon; děláme otevřený travnatý svět s border stěnami. # Místnost už nerenderujeme jako složitý dungeon; děláme otevřený travnatý svět s border stěnami.
    blocks = pygame.sprite.Group()                             # Sprite group pro všechny bloky
    placed = set()                                             # Množina již umístěných pozic (prevence duplikátů)

    min_x = min(room['x'] for room in rooms)                   # Nejlevější bod
    min_y = min(room['y'] for room in rooms)                   # Nejvyšší bod
    max_x = max(room['x'] + room['width'] for room in rooms)   # Pravý okraj světa
    max_y = max(room['y'] + room['height'] for room in rooms)  # Dolní okraj světa

    # Vodorovné stěny v horní a dolní hranici                   # Vodorovné stěny v horní a dolní hranici
    y_top = min_y - BLOCK_SIZE                                 # Pozice horní stěny (1 blok nad světem)
    y_bottom = max_y + BLOCK_SIZE                              # Pozice dolní stěny (1 blok pod světem)
    for bx in range(min_x - BLOCK_SIZE, max_x + 2*BLOCK_SIZE, BLOCK_SIZE): # Od levé do pravé strany
        blocks.add(Block(bx, y_top, 'stone'))                  # Horní stěna – kamenný blok
        placed.add((bx, y_top))                                # Zapamatuje pozici
        blocks.add(Block(bx, y_bottom, 'stone'))               # Dolní stěna – kamenný blok
        placed.add((bx, y_bottom))                             # Zapamatuje pozici

    # Svislé stěny vlevo a vpravo                               # Svislé stěny vlevo a vpravo
    x_left = min_x - BLOCK_SIZE                                # Pozice levé stěny
    x_right = max_x + BLOCK_SIZE                               # Pozice pravé stěny
    for by in range(min_y - BLOCK_SIZE, max_y + 2*BLOCK_SIZE, BLOCK_SIZE): # Od horní strany dolů
        blocks.add(Block(x_left, by, 'stone'))                 # Levá stěna
        placed.add((x_left, by))                               # Zapamatuje
        blocks.add(Block(x_right, by, 'stone'))                # Pravá stěna
        placed.add((x_right, by))                              # Zapamatuje

    # Přidáme hranice světa (jednobloční zdi) tak, aby hráč nemohl vypadnout ven # Přidáme hranice světa (jednobloční zdi) tak, aby hráč nemohl vypadnout ven


    # Vodorovné hrany                                           # Vodorovné hrany
    for bx in range(min_x - BLOCK_SIZE, max_x + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE): # Vodorovné doplnění
        for by in [min_y - BLOCK_SIZE, max_y + BLOCK_SIZE]:    # Horní a dolní řada
            if (bx, by) not in placed:                         # Pokud tam ještě není blok
                blocks.add(Block(bx, by, 'stone'))             # Přidá kamenný blok
                placed.add((bx, by))                           # Zapamatuje

    # Svislé hrany                                              # Svislé hrany
    for by in range(min_y - BLOCK_SIZE, max_y + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE): # Svislé doplnění
        for bx in [min_x - BLOCK_SIZE, max_x + BLOCK_SIZE]:    # Levý a pravý sloupec
            if (bx, by) not in placed:                         # Pokud tam ještě není blok
                blocks.add(Block(bx, by, 'stone'))             # Přidá kamenný blok
                placed.add((bx, by))                           # Zapamatuje

    items = pygame.sprite.Group()                              # Prázdná sprite group pro předměty

    return blocks, items, rooms                                # Vrátí stěny, předměty a seznam místností

def spawn_at_screen_edge(camera, offset):                      # Parametr offset = vzdálenost za okrajem
    """Vrátí náhodnou pozici za okrajem kamery."""             # Docstring
    cam_x = -camera.rect.x                                     # Levý okraj kamery ve světových souřadnicích
    cam_y = -camera.rect.y                                     # Horní okraj kamery ve světových souřadnicích
    cam_w = int(WINDOW_WIDTH / ZOOM)                           # Šířka plátna po zoomu
    cam_h = int(WINDOW_HEIGHT / ZOOM)                          # Výška plátna po zoomu
    edge = random.randint(0, 3)                                # Náhodná hrana (0=horní, 1=pravá, 2=dolní, 3=levá)
    if edge == 0:                                              # Horní hrana
        sx = random.randint(cam_x - offset, cam_x + cam_w + offset) # Náhodné X
        sy = cam_y - offset                                    # Y nad horní hranou
    elif edge == 1:                                            # Pravá hrana
        sx = cam_x + cam_w + offset                            # X za pravou hranou
        sy = random.randint(cam_y - offset, cam_y + cam_h + offset) # Náhodné Y
    elif edge == 2:                                            # Dolní hrana
        sx = random.randint(cam_x - offset, cam_x + cam_w + offset) # Náhodné X
        sy = cam_y + cam_h + offset                            # Y pod dolní hranou
    else:                                                      # Pokud se nevlezla
        sx = cam_x - offset                                    # X před levou hranou
        sy = random.randint(cam_y - offset, cam_y + cam_h + offset) # Náhodné Y
    sx = max(BLOCK_SIZE, min(sx, WORLD_WIDTH_PX - BLOCK_SIZE)) # Omezení X na hranice světa
    sy = max(BLOCK_SIZE, min(sy, WORLD_HEIGHT_PX - BLOCK_SIZE)) # Omezení Y na hranice světa
    return sx, sy                                              # Vrátí souřadnice pro spawn

def show_death_screen(screen, score, wave, menu_font, info_font): # Parametry: okno, skóre, vlna, fonty
    options = ["Retry", "Main Menu"]                           # Dvě možnosti
    selected = 0                                               # Výchozí výběr (Start Game)
    clock = pygame.time.Clock()                                # Časovač (FPS kontroler)
    btn_font = pygame.font.Font(None, 60)                      # Font pro tlačítka (60 px)

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA) # Tmavá poloprůhledná vrstva
    overlay.fill((0, 0, 0, 150))                               # Černý s 60% průhledností
    screen.blit(overlay, (0, 0))                               # Vykreslí poloprůhledné pozadí přes celou hru

    while True:                                                # Menu smyčka, běží, dokud hráč nevybere postavu
        mx, my = pygame.mouse.get_pos()                        # Pozice kurzoru myši pro interakci
        clicked = False                                        # Flag kliknutí

        for event in pygame.event.get():                       # Zpracování uživatelských událostí
            if event.type == pygame.QUIT:                      # Kliknuto na křížek okna
                pygame.quit()                                  # Ukončí pygame
                sys.exit()                                     # Ukončí program
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Levé kliknutí
                clicked = True                                 # Nastaví flag
            elif event.type == pygame.KEYDOWN:                 # Stisk klávesy
                if event.key in (pygame.K_UP, pygame.K_w):     # Nahoru / W
                    selected = (selected - 1) % len(options)   # Přesune výběr nahoru
                elif event.key in (pygame.K_DOWN, pygame.K_s): # Dolů / S
                    selected = (selected + 1) % len(options)   # Přesune výběr dolů
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE): # Enter / Space
                    return options[selected].lower()           # Vrátí výběr

        title_surf = menu_font.render("YOU DIED", True, (255, 50, 50)) # Červený text
        title_shadow = menu_font.render("YOU DIED", True, (0, 0, 0)) # Černý stín
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)) # Centrováno nahoře
        screen.blit(title_shadow, title_rect.move(4, 4))       # Stín posunutý o 4 px
        screen.blit(title_surf, title_rect)                    # Text přes stín

        stats_surf = info_font.render(f"Score: {score}   |   Wave: {wave}", True, WHITE) # Skóre a vlna
        stats_rect = stats_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4 + 70)) # Pod titulkem
        screen.blit(stats_surf, stats_rect)                    # Vykreslí

        button_width = 300                                     # Šířka tlačítka
        button_height = 80                                     # Výška tlačítka
        for idx, option in enumerate(options):                 # Pro každou možnost
            btn_rect = pygame.Rect(0, 0, button_width, button_height) # Obdélník tlačítka
            btn_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 110) # Centrováno, mezera 110 px

            if btn_rect.collidepoint(mx, my):                  # Pokud myš je nad tlačítkem
                selected = idx                                 # Zvýrazní
                if clicked:                                    # Pokud klik
                    return options[selected].lower()           # Vrátí výběr

            color_bg = (150, 50, 50) if idx == selected else (80, 30, 30) # Barva pozadí (vybraný/nevybraný)
            color_text = WHITE if idx == selected else (200, 200, 200) # Barva textu

            pygame.draw.rect(screen, color_bg, btn_rect, border_radius=15) # Pozadí tlačítka
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15) # Okraj tlačítka

            option_surf = btn_font.render(option, True, color_text) # Text tlačítka
            option_rect = option_surf.get_rect(center=btn_rect.center) # Centrováno v tlačítku
            screen.blit(option_surf, option_rect)              # Vykreslí text

        pygame.display.flip()                                  # Aktualizuje obrazovku menu
        clock.tick(FPS)                                        # 60 FPS

# =============================================                 # =============================================
# Vykreslení level-up obrazovky (MegaBonk style)                # Vykreslení level-up obrazovky (MegaBonk style)
# =============================================                 # =============================================

def draw_level_up_screen(screen, upgrades_offered, player, fonts): # Funkce vykreslující obrazovku výběru odměny
    """Vykreslí MegaBonk-style level-up obrazovku s kartami zbraní/tomů.""" # Docstring
    font_lg, font_ui, font_sm, font_rar, font_desc = fonts     # Rozbalí pět různých velikostí písma

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA) # Tmavá poloprůhledná vrstva
    overlay.fill((0, 0, 0, 190))                               # Vyplnění černou barvou s průhledností (190)
    screen.blit(overlay, (0, 0))                               # Vykreslí poloprůhledné pozadí přes celou hru

    # Titulek                                                   # Titulek
    title = font_lg.render('LEVEL UP!', True, (255, 215, 0))   # Žlutý text LEVEL UP
    title_shadow = font_lg.render('LEVEL UP!', True, (80, 60, 0)) # Tmavý stín pod nadpisem
    screen.blit(title_shadow, (WINDOW_WIDTH // 2 - title.get_width() // 2 + 3, 53)) # Stín mírně posunutý doprava a dolů
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50)) # Skutečný žlutý nápis

    subtitle = font_ui.render('Choose an upgrade:', True, (200, 200, 200)) # Text "Vyberte si vylepšení"
    screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 120)) # Zarovnání na střed

    if not upgrades_offered:                                   # Pokud nebyly nalezeny žádné odměny (už má hráč všechno)
        no_upg = font_sm.render("No upgrades available!", True, (200, 100, 100)) # Červený text oznámení
        screen.blit(no_upg, (WINDOW_WIDTH // 2 - no_upg.get_width() // 2, WINDOW_HEIGHT // 2)) # Na střed obrazovky
        return                                                 # Ukončí update (mrtvý hráč nic jiného nedělá)

    card_count = len(upgrades_offered)                         # Počet karet na obrazovce (většinou 3)
    card_w, card_h, spacing = 280, 400, 45                     # Šířka, výška a mezery mezi kartami
    total_w = card_count * card_w + (card_count - 1) * spacing # Celková šířka všech karet dohromady
    start_x = (WINDOW_WIDTH - total_w) // 2                    # Vycentrování celého bloku na X ose okna
    start_y = (WINDOW_HEIGHT - card_h) // 2 + 15               # Posun na střed obrazovky + malý posun dolů
    mx, my = pygame.mouse.get_pos()                            # Pozice kurzoru myši pro interakci

    for idx, upgrade in enumerate(upgrades_offered):           # Cyklus pro vykreslení každé karty
        cx = start_x + idx * (card_w + spacing)                # Odsazení každé karty X od začátku
        rect = pygame.Rect(cx, start_y, card_w, card_h)        # Vytvoření hranic
        hovered = rect.collidepoint(mx, my)                    # Najetí myší na kartu postaví Hover Effect

        base_col = RARITY_COLORS.get(upgrade["rarity"], WHITE) # Barva podle rarity

        # Glow efekt při hoveru                                 # Glow efekt při hoveru
        if hovered:                                            # Pokud najedu na kartu myší (aktivní efekt)
            glow_surf = pygame.Surface((card_w + 24, card_h + 24), pygame.SRCALPHA) # Plátno pro vnější záři
            pygame.draw.rect(glow_surf, (*base_col, 50), (0, 0, card_w + 24, card_h + 24), border_radius=16) # Vnější rámeček
            screen.blit(glow_surf, (cx - 12, start_y - 12))    # Kreslení obrysu
            # Druhá vrstva záře                                 # Druhá vrstva záře
            glow_surf2 = pygame.Surface((card_w + 12, card_h + 12), pygame.SRCALPHA) # Plátno pro vnitřní záři
            pygame.draw.rect(glow_surf2, (*base_col, 30), (0, 0, card_w + 12, card_h + 12), border_radius=14) # Vnitřní rámeček
            screen.blit(glow_surf2, (cx - 6, start_y - 6))     # Kreslení obrysu

        # Pozadí karty                                          # Pozadí karty
        bg_r = min(255, base_col[0] // 5 + 25)                 # Použije se temnější odstín
        bg_g = min(255, base_col[1] // 5 + 25)                 # Mírný odstín zelené složky
        bg_b = min(255, base_col[2] // 5 + 25)                 # Modré
        if hovered:                                            # Pokud najedu na kartu myší (aktivní efekt)
            bg_r = min(255, bg_r + 15)                         # Zesvětlení v hover modu (červená)
            bg_g = min(255, bg_g + 15)                         # Zelená složka
            bg_b = min(255, bg_b + 15)                         # Modrá složka
        bg_col = (bg_r, bg_g, bg_b)                            # Složení vybrané barvy

        pygame.draw.rect(screen, bg_col, rect, border_radius=12) # Základní vnitřní tělo karty

        # Gradient efekt na kartě (horní polovina světlejší)    # Gradient efekt na kartě (horní polovina světlejší)
        grad_surf = pygame.Surface((card_w, card_h // 2), pygame.SRCALPHA) # Horní polovina karty s odleskem
        grad_surf.fill((*base_col, 15))                        # Podbarvení (gradient effect)
        screen.blit(grad_surf, (cx, start_y))                  # Vložení horního efektu podsvícení

        # Okraj karty                                           # Okraj karty
        border_w = 3 if not hovered else 4                     # Karta je při najetí myší nepatrně tučnější
        pygame.draw.rect(screen, base_col, rect, border_w, border_radius=12) # Vykreslení finálního barevného okraje karty

        # Ikona - kruh nahoře                                   # Ikona - kruh nahoře
        icon_y = rect.top + 70                                 # Y Souřadnice pro hlavní ikonu (odshora)
        icon_color = upgrade.get("icon_color", base_col)       # Zjištění barvy ikony

        # Kruhy pozadí ikony                                    # Kruhy pozadí ikony
        pygame.draw.circle(screen, (0, 0, 0, 80), (rect.centerx + 2, icon_y + 2), 36) # Stín za ikonou zbraně (černé kolo)
        pygame.draw.circle(screen, (icon_color[0] // 3, icon_color[1] // 3, icon_color[2] // 3), (rect.centerx, icon_y), 36) # Tmavší okraj
        pygame.draw.circle(screen, icon_color, (rect.centerx, icon_y), 30) # Vnitřní světlá plocha pro ikonu
        pygame.draw.circle(screen, (255, 255, 255), (rect.centerx, icon_y), 30, 2) # Bílý kroužek - orámování vnitřku ikony

        # Ikona uvnitř kruhu                                    # Ikona uvnitř kruhu
        draw_upgrade_icon(screen, upgrade["id"], rect.centerx, icon_y) # Pomocná funkce vykreslí samotný tvar (meč, hodiny apod.)

        # Typ label (WEAPON / TOME)                             # Typ label (WEAPON / TOME)
        is_weapon = "weapon" in upgrade["type"]                # Proměnná pro logiku, zdali je to zbraň (nebo kniha/tome)
        type_label = "WEAPON" if is_weapon else "TOME"         # Nápis pod ikonou
        type_col = (255, 200, 100) if is_weapon else (100, 255, 200) # Oranžový nápis pro zbraň, světle zelený pro Tome
        type_surf = font_desc.render(type_label, True, type_col) # Vyrendruje typ jako obrázek textu
        screen.blit(type_surf, (rect.centerx - type_surf.get_width() // 2, rect.top + 115)) # Nakreslí uprostřed

        # Název                                                 # Název
        name_surf = font_sm.render(upgrade['name'], True, WHITE) # Jméno upgradu
        screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.top + 140)) # Nakreslí na střed

        # Rarity                                                # Rarity
        rar_surf = font_rar.render(upgrade['rarity'], True, base_col) # Rarity text v raritní barvě
        screen.blit(rar_surf, (rect.centerx - rar_surf.get_width() // 2, rect.top + 170)) # Nakreslí pod jméno

        # Level info                                            # Level info
        if upgrade['current_level'] == 0:                      # Pokud zbraň ještě hráč nevlastní
            level_text = "NEW!"                                # Text je "Novinka"
            level_col = (100, 255, 100)                        # Modrozelená barva (vyznačuje první sebrání)
        else:                                                  # Pokud se nevlezla
            level_text = f"Lv.{upgrade['current_level']}  ->  Lv.{upgrade['next_level']}" # Text změny úrovně
            level_col = (255, 255, 100)                        # Žlutá barva pro vylepšení aktuální věci
        level_surf = font_rar.render(level_text, True, level_col) # Vykreslení textu s levelem
        screen.blit(level_surf, (rect.centerx - level_surf.get_width() // 2, rect.top + 200)) # Umístění na kartě

        # Oddělovací čára                                       # Oddělovací čára
        pygame.draw.line(screen, base_col, (rect.left + 25, rect.top + 235), (rect.right - 25, rect.top + 235), 1) # Tenká oddělovací čára v barvě rarity

        # Popis                                                 # Popis
        desc_surf = font_desc.render(upgrade['desc'], True, (210, 210, 210)) # Vypsání detailů vylepšení (např. "+1 Damage, -2 Cooldown")
        screen.blit(desc_surf, (rect.centerx - desc_surf.get_width() // 2, rect.top + 255)) # Nasázení pod čáru

        # MAX level indikátor                                   # MAX level indikátor
        if upgrade.get("next_level", 0) >= MAX_WEAPON_LEVEL and is_weapon: # Informace, zdali je to poslední možné vylepšení
            max_surf = font_desc.render("* MAX LEVEL *", True, (255, 215, 0)) # Zlatý text Max Level
            screen.blit(max_surf, (rect.centerx - max_surf.get_width() // 2, rect.top + 290)) # Vložení dole na kartu

        # Weapon slot info                                      # Weapon slot info
        if is_weapon:                                          # Pokud je odměna zbraň a ne tome, sledujeme počet slotů
            slots_used = len(player.weapons)                   # Kolik má teď hráč slotů zaplněných (meč, shuriken...)
            if upgrade["type"] == "weapon_new":                # Pokud je to nová zbraň
                slot_text = f"Slots: {slots_used}/{MAX_WEAPON_SLOTS}" # Popisek s počtem zaplněných pozic ze čtyř možných
            else:                                              # Pokud se nevlezla
                slot_text = f"Slots: {slots_used}/{MAX_WEAPON_SLOTS}" # Popisek s počtem zaplněných pozic ze čtyř možných
            slot_surf = font_desc.render(slot_text, True, (150, 150, 150)) # Světle šedý text
            screen.blit(slot_surf, (rect.centerx - slot_surf.get_width() // 2, rect.bottom - 40)) # Vloží varování nad spodek karty

    # Reroll tlačítko                                           # Reroll tlačítko
    reroll_cost = player.reroll_cost                           # Získá cenu za znovulosování od hráče (dynamicky se zvyšuje s používáním)
    reroll_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, start_y + card_h + 25, 240, 50) # Tlačítko pro reroll vycentruje na ose X
    reroll_hovered = reroll_rect.collidepoint(mx, my)          # Jestli je myš na tlačítku
    can_reroll = player.money >= reroll_cost                   # Zjistí, jestli na to má hráč peníze

    reroll_bg = (80, 65, 20) if can_reroll else (45, 45, 45)   # Zlaté pozadí pokud lze, jinak tmavě šedé, pokud chybí peníze
    if reroll_hovered and can_reroll:                          # Při přejetí myši a s dostatkem peněz se tlačítko rozsvítí
        reroll_bg = (120, 95, 30)                              # Výraznější žlutozlatá barva
    pygame.draw.rect(screen, reroll_bg, reroll_rect, border_radius=10) # Základní vrstva tlačítka pro reroll (přeměnu dropů)

    reroll_border_col = (255, 215, 0) if can_reroll else (100, 100, 100) # Rámeček svítí žlutě pokud to jde, jinak zešedne
    pygame.draw.rect(screen, reroll_border_col, reroll_rect, 2, border_radius=10) # Vykreslí prázdný okraj přes tlačítko

    reroll_text_col = (255, 215, 0) if can_reroll else (100, 100, 100) # Barva textu zavisí též na mincích
    reroll_text = font_rar.render(f"Reroll  ({reroll_cost} coins)  [R]", True, reroll_text_col) # Vypsání, kolik přetočení bude stát a zkratka tlačítka
    screen.blit(reroll_text, (reroll_rect.centerx - reroll_text.get_width() // 2, reroll_rect.centery - reroll_text.get_height() // 2)) # Usazení doprostřed tlačítka

    return start_x, start_y, card_w, card_h, spacing, reroll_rect # Návratové parametry rozložení na obrazovce (pro snímání kliknutí myší v event loopu)


# Hlavní funkce hry                                             # Hlavní funkce hry
def main(character_id="knight"):                               # Hlavní funkce now přijímá vybranou postavu z menu
    global WORLD_WIDTH_PX, WORLD_HEIGHT_PX                     # Globální proměnné pro velikost světa
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME) # Fullscreen borderless okno
    pygame.display.set_caption(TITLE)                          # Titulek okna
    clock = pygame.time.Clock()                                # Časovač (FPS kontroler)

    # Cachované fonty (vytvořené jednou, ne každý snímek)       # Cachované fonty (vytvořené jednou, ne každý snímek)
    font_ui = pygame.font.Font(None, 36)                       # Font pro UI text (36 px)
    font_lg = pygame.font.Font(None, 74)                       # Velký font pro nadpisy (74 px)
    font_sm = pygame.font.Font(None, 36)                       # Malý font pro jména upgradů
    font_rar = pygame.font.Font(None, 28)                      # Font pro rarity text (28 px)
    font_desc = pygame.font.Font(None, 24)                     # Font pro popisky (malý)
    fonts = (font_lg, font_ui, font_sm, font_rar, font_desc)   # Přesun písem do jedné proměnné, aby se daly posílat jako atribut pro level up obrazovku

    # Generování dungeonu                                       # Generování dungeonu
    blocks, items, rooms = generate_dungeon(DUNGEON_SIZE)      # Vygeneruje dungeon (stěny, předměty, místnosti)
    # Velikost světa (maximální rozsah místností)               # Velikost světa (maximální rozsah místností)
    max_x = max(room['x'] + room['width'] for room in rooms)   # Pravý okraj světa
    max_y = max(room['y'] + room['height'] for room in rooms)  # Dolní okraj světa
    WORLD_WIDTH_PX = max_x + BLOCK_SIZE                        # Celková šířka světa v pixelech
    WORLD_HEIGHT_PX = max_y + BLOCK_SIZE                       # Celková výška světa v pixelech

    # Najdeme startovní místnost (první)                        # Najdeme startovní místnost (první)
    start_room = rooms[0]                                      # První místnost = start
    start_x = start_room['x'] + start_room['width'] // 2       # Střed místnosti X
    start_y = start_room['y'] + start_room['height'] // 2      # Střed místnosti Y
    player = Player(start_x, start_y, character_id)            # Konstruktor hráče dostal navíc z menu postavu, s jakou chceme hrát (Zloděj atp.)

    # Spawn nepřátel (startovní místnost bez nepřátel)          # Spawn nepřátel (startovní místnost bez nepřátel)
    enemies = pygame.sprite.Group()                            # Sprite group pro nepřátele
    for room in rooms:                                         # Pro každou místnost
        if room == start_room:                                 # Přeskoč startovní místnost (bez nepřátel)
            continue                                           # Proto přeskočíme, meč se počítá v klávesách `handle_input`
        if random.random() < 0.7:                              # 70% šance na nepřítele v ostatních místnostech # Zbytek kódu při generování příšer při startu levelu
            ex = room['x'] + random.randint(2, (room['width']//BLOCK_SIZE)-3) * BLOCK_SIZE # Náhodná X pozice v místnosti
            ey = room['y'] + random.randint(2, (room['height']//BLOCK_SIZE)-3) * BLOCK_SIZE # Náhodná Y pozice
            enemy_type = random.choices(['walker', 'flying'], weights=[0.7, 0.3])[0] # 70% walker, 30% flying
            enemy = Enemy(ex, ey, enemy_type)                  # Vytvoří nepřítele
            enemies.add(enemy)                                 # Přidá do skupiny

    # Projektily (shurikeny atd.)                               # Projektily (shurikeny atd.)
    projectiles = pygame.sprite.Group()                        # Založení pole pro všechny střely zbraní (př. hozené Shurikeny)

    # Kamera                                                    # Kamera
    camera = Camera(WORLD_WIDTH_PX, WORLD_HEIGHT_PX)           # Kamera pokrývající celý svět

    # Neustálý spread nepřátel                                  # Neustálý spread nepřátel
    spawn_timer = 0                                            # Resetuje časovač
    current_spawn_interval = ENEMY_SPAWN_INTERVAL              # Resetuje interval spawnu
    wave_number = 1                                            # Číslo aktuální vlny
    wave_timer = 0                                             # Resetuje časovač
    total_spawns = 0                                           # Celkový počet provedených spawnů

    # Herní smyčka                                              # Herní smyčka
    running = True                                             # Flag pro běh herní smyčky
    score: int = 0                                             # Skóre hráče
    death_timer = 0                                            # Časovač po smrti (pro zpoždění death screenu)
    is_level_up_screen = False                                 # Zavře upgrade menu
    upgrades_offered = []                                      # Vyčistí nabídku

    while running:                                             # TODO_COMMENT
        clock.tick(FPS)                                        # 60 FPS

        for event in pygame.event.get():                       # Zpracování uživatelských událostí
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Levé tlačítko myši
                if is_level_up_screen and upgrades_offered:    # Event Loop chytá kliknutí do obrazovky level-upu na jednotlivé karty (myš)
                    mx, my = pygame.mouse.get_pos()            # Pozice kurzoru myši pro interakci
                    card_count = len(upgrades_offered)         # Počet karet na obrazovce (většinou 3)
                    card_w, card_h, spacing = 280, 400, 45     # Šířka, výška a mezery mezi kartami
                    total_w = card_count * card_w + (card_count - 1) * spacing # Celková šířka všech karet dohromady
                    lu_start_x = (WINDOW_WIDTH - total_w) // 2 # Kde začaly karty (osa X)
                    lu_start_y = (WINDOW_HEIGHT - card_h) // 2 + 15 # Kde začaly karty (osa Y)

                    # Kontrola kliknutí na karty                # Kontrola kliknutí na karty
                    for idx, upgrade in enumerate(upgrades_offered): # Cyklus pro vykreslení každé karty
                        cx = lu_start_x + idx * (card_w + spacing) # Rozpočítání, jestli myš klikla do jedné ze tří karet
                        rect = pygame.Rect(cx, lu_start_y, card_w, card_h) # Kolizní box
                        if rect.collidepoint(mx, my):          # Myš trefila obdélník
                            apply_upgrade(player, upgrade)     # Pokud ano, aplikuje vybraný level up z nabídky pro hráče
                            player.level_up_pending -= 1       # Sníží počet čekajících level-upů
                            is_level_up_screen = False         # Zavře upgrade menu
                            break                              # Přeruší výběr

                    # Kontrola reroll tlačítka                  # Kontrola reroll tlačítka
                    reroll_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, lu_start_y + card_h + 25, 240, 50) # Znovuvytvoření tlačítka, jestli klikla na něj a ne na kartu
                    if reroll_rect.collidepoint(mx, my):       # Ověří se, zda kliknul na Reroll (přetočit nabídku)
                        if player.money >= player.reroll_cost: # Jestli peněženka stačí na poplatek
                            player.money -= player.reroll_cost # Odečte mince
                            player.reroll_cost += 2            # Poplatek se s každým použitím zvýší (stojí 3, pak 5, 7, atd.)
                            upgrades_offered = generate_upgrade_offers(player) # Vygeneruje 3 úplně nové nabídky a hra ukáže level up obrazovku znovu

            if event.type == pygame.QUIT:                      # Kliknuto na křížek okna
                running = False                                # Ukončí hru
            elif event.type == pygame.KEYDOWN:                 # Stisk klávesy
                if event.key == pygame.K_ESCAPE:               # Klávesa Escape
                    running = False                            # Ukončí hru
                elif event.key == pygame.K_f:                  # F – přepnutí fullscreenu
                    if screen.get_flags() & pygame.FULLSCREEN: # Pokud je fullscreen
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Přepne na okno
                    else:                                      # Pokud se nevlezla
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME) # Fullscreen borderless okno
                elif event.key == pygame.K_r and is_level_up_screen: # Tlačítko pro reroll přes klávesu R
                    # Reroll klávesou R                         # Reroll klávesou R
                    if player.money >= player.reroll_cost:     # Jestli peněženka stačí na poplatek
                        player.money -= player.reroll_cost     # Odečte mince
                        player.reroll_cost += 2                # Poplatek se s každým použitím zvýší (stojí 3, pak 5, 7, atd.)
                        upgrades_offered = generate_upgrade_offers(player) # Vygeneruje 3 úplně nové nabídky a hra ukáže level up obrazovku znovu

        # Aktualizace                                           # Aktualizace
        if player.level_up_pending > 0 and not is_level_up_screen: # Pokud čeká level-up a menu ještě není zobrazeno
            is_level_up_screen = True                          # Zapne upgrade menu
            player.reroll_cost = REROLL_BASE_COST              # Reset reroll cost při novém level-upu zpět na hodnotu 3
            upgrades_offered = generate_upgrade_offers(player) # Vygeneruje 3 úplně nové nabídky a hra ukáže level up obrazovku znovu

        if not is_level_up_screen:                             # Update logiky pokračuje jen, pokud hra není pozastavena
            player.update(blocks, camera)                      # Aktualizace hráče (vstup, pohyb, animace)
            enemies.update(blocks, player)                     # Aktualizace všech nepřátel (pohyb k hráči)
            items.update(player)                               # Aktualizace předmětů (magnetismus)
            projectiles.update()                               # Spustí update letících projektilů a aktualizuje jim pozice

            # =============================================     # =============================================
            # Weapon fire logic (MegaBonk styl)                 # Weapon fire logic (MegaBonk styl)
            # =============================================     # =============================================
            for weapon_id, level in player.weapons.items():    # Update cooldownů automatických zbraní
                if weapon_id == "sword":                       # Meč neignorujeme úplně, ale nepočítáme do auto attacku
                    continue                                   # Proto přeskočíme, meč se počítá v klávesách `handle_input`

                if weapon_id not in player.weapon_timers:      # Pojistka: Pokud zbraň náhodou nemá nastavený časovač (úplně nová zbraň z level-upu)
                    player.weapon_timers[weapon_id] = 0        # Ihned může začít střílet

                player.weapon_timers[weapon_id] -= 1           # Odkrajuje časovač ze cooldownu zbraně do dalšího výstřelu
                if player.weapon_timers[weapon_id] <= 0:       # Zbraň je "nabitá" k útoku
                    stats = WEAPON_DEFS[weapon_id]["levels"][level] # Vezmeme si data k tomuto meči z hlavní paměti a jejího aktuálního levelu
                    effective_cd = max(5, int(stats["cooldown"] * player.cooldown_mult)) # Snižuje čas střelby knihou Haste Tome na maximálně rychlost limit 5 framů
                    player.weapon_timers[weapon_id] = effective_cd # Uložíme zbrani novou hodnotu nabití

                    if weapon_id == "shuriken":                # Jak útočí SHURIKEN
                        count = stats["count"]                 # Počet shurikenů kolik jich letí naráz
                        # Najdi nejbližšího nepřítele           # Najdi nejbližšího nepřítele
                        nearest = None                         # Uchová referenci na cíl
                        min_dist = float('inf')                # Nastaví minimální vzálenost k nalezení na maximum
                        for e in enemies:                      # Cyklus co zjistí kde je nejbližší netvor
                            d = math.hypot(e.rect.centerx - player.rect.centerx, # Pitagorova věta (hypot)
                                           e.rect.centery - player.rect.centery) # X a Y pro výpočet vzdálenosti na mapě
                            if d < min_dist:                   # Menší vzdálenost
                                min_dist = d                   # Přepíše hodnotu
                                nearest = e                    # Označí oběť

                        for i in range(count):                 # Nyní postupně vrhá shurikeny do zadaného cíle
                            if nearest and count <= 2:         # Málo shurikenů, úzce hozených na jeden target
                                base_angle = math.degrees(math.atan2( # Uhel letu od hráče tam, kde je zrůda
                                    nearest.rect.centery - player.rect.centery, # TODO_COMMENT
                                    nearest.rect.centerx - player.rect.centerx)) # TODO_COMMENT
                                angle = base_angle + (i - (count - 1) / 2) * 25 # Změna úhlu, aby druhý Shuriken letěl kousek vedle prvního o 25 stupnů
                            elif nearest:                      # Mnoho shurikenů z velkého kruhu (3 a víc), vyletí vějíř
                                base_angle = math.degrees(math.atan2( # Uhel letu od hráče tam, kde je zrůda
                                    nearest.rect.centery - player.rect.centery, # TODO_COMMENT
                                    nearest.rect.centerx - player.rect.centerx)) # TODO_COMMENT
                                angle = base_angle + (i - (count - 1) / 2) * (360 / count) # Rozprostře Shurikeny symetricky na všechny strany mapy
                            else:                              # Pokud se nevlezla
                                angle = (360 / count) * i + random.uniform(-15, 15) # Shurikeny vyletí do všech stran (dokola hráče) s náhodným rozptylem k rozbití předmětů

                            proj_damage = stats["damage"] * player.damage_mult # Spočítá jak moc ublíží s knihou na damage (Power Tome)
                            proj = ShurikenProjectile(         # Vytvoření objektu projektilu stávající hodnoty Shurikenu
                                player.rect.centerx, player.rect.centery, # Vychází ze středu postavy
                                angle, stats["speed"], proj_damage) # Směr, rychlost, zranění
                            projectiles.add(proj)              # Shuriken hodí do globálního pole fyziky všech dalších letících shurikenů

                    elif weapon_id == "fire_ring":             # Jak útočí FIRE RING (Ohnivý prsten)
                        player.fire_ring_active = stats["duration"] # Nastaví u hráče časovač, jak dlouho má efekt svítit
                        player.fire_ring_radius = stats["radius"] # Z dat zbraní přečte dosah radiusu kruhu pro ten daný level hráče
                        player.fire_ring_damage = stats["damage"] * player.damage_mult # Přečte udělované zranění (+ Power Tome boost)
                        player.fire_ring_max_duration = stats["duration"] # Max duration pomáhá vizuálnímu odlesku plamenů zmizet průhledně v update

                    elif weapon_id == "lightning":             # Jak útočí LIGHTNING (Blesky)
                        targets_count = stats["targets"]       # Do kolika nepřátel může udeřit jeden blesk podle levelu? (Chaining efekt)
                        enemy_list = sorted(                   # Nalezne ty oběti
                            enemies.sprites(),                 # Ze všech nepřátel (Array ze Sprites)
                            key=lambda e: math.hypot(          # Seřadí je blíž od hráče
                                e.rect.centerx - player.rect.centerx, # TODO_COMMENT
                                e.rect.centery - player.rect.centery)) # TODO_COMMENT
                        player.lightning_bolts = []            # Promaže u hráče blesky nakreslené z minulého snímku (už zmizely)
                        lt_damage = stats["damage"] * player.damage_mult # Síla bleskového útoku z updatu
                        for e in enemy_list[:targets_count]:   # Prochází tolik nejbližších nepřátel, jaký je chain
                            e.take_damage(lt_damage)           # Instantní (okamžité) udělení zranění bez fyzikálního letu
                            e.hit_flash = 8                    # Zablýskne se do bíla
                            if hasattr(e, 'apply_knockback'):  # Podařilo se
                                e.apply_knockback(player.rect) # Odkopnutí od výbuchu
                            player.lightning_bolts.append(     # Uloží trajektorii čáry (od Hráče do Netvora) k vykreslení modrých a bílých čar (Blesku)
                                (player.rect.center, e.rect.center)) # TODO_COMMENT
                            if e.is_dead():                    # Nepřítel usmrcen okamžitě
                                items.add(Item(e.rect.x, e.rect.y, 'xp', xp_value=e.xp_value)) # Vypadne modrá hvězdička (XPčka na level-up)
                                if random.random() < 0.3:      # 30% šance na drop peněz
                                    items.add(Item(e.rect.x + random.randint(-10, 10), # Plus šance i vedle občas hodit
                                                   e.rect.y + random.randint(-10, 10), # TODO_COMMENT
                                                   'money', xp_value=random.randint(1, 3))) # Vypadnou zlaté peníze s odchylkou souřadnice, ne doprostřed
                                e.kill()                       # Zničení mrtvého nepřítele
                                score += 10                    # Přidá 10 bodů do skóre
                        player.lightning_timer = 15            # Říká enginu: Nyní nakresli tu modrou čáru (Blesk) po dalších 15 snímků hry pro vizualizaci zásahu bleskem

            # Fire ring damage tick                             # Fire ring damage tick
            if player.fire_ring_active > 0 and player.fire_ring_active % 10 == 0: # Když ohnivý prsten ubíhá časovač, každých "10 snímků" dává Damage, co je v něm
                for e in list(enemies):                        # Najde všechny nepřátele
                    dist = math.hypot(e.rect.centerx - player.rect.centerx, # Kde stvůra k hráči je
                                      e.rect.centery - player.rect.centery) # X a Y pro výpočet vzdálenosti na mapě
                    if dist < player.fire_ring_radius:         # Je poloha stvůry menší jak dosah ohně? (hoří?)
                        e.take_damage(player.fire_ring_damage) # Utrží Damage z ohnivého kruhu
                        e.hit_flash = 4                        # Rychle zablýskne bíle, signalizuje popáleninu (tick damage)
                        if e.is_dead():                        # Nepřítel usmrcen okamžitě
                            items.add(Item(e.rect.x, e.rect.y, 'xp', xp_value=e.xp_value)) # Vypadne modrá hvězdička (XPčka na level-up)
                            if random.random() < 0.3:          # 30% šance na drop peněz
                                items.add(Item(e.rect.x + random.randint(-10, 10), # Plus šance i vedle občas hodit
                                               e.rect.y + random.randint(-10, 10), # TODO_COMMENT
                                               'money', xp_value=random.randint(1, 3))) # Vypadnou zlaté peníze s odchylkou souřadnice, ne doprostřed
                            e.kill()                           # Zničení mrtvého nepřítele
                            score += 10                        # Přidá 10 bodů do skóre

            # Shuriken kolize s nepřáteli                       # Shuriken kolize s nepřáteli
            for proj in list(projectiles):                     # A ještě kolize fyzikálních střel po mapě (letící Shurikeny)
                if isinstance(proj, ShurikenProjectile):       # Je toto letící zbraň Shuriken a ne nic jiného z modů?
                    for e in list(enemies):                    # Najde všechny nepřátele
                        if e not in proj.hit_enemies and proj.rect.colliderect(e.rect): # Pokud stvůru ještě zbraň neprořízla (Shuriken je piercující, prolétává skrz hordu, každou zasáhne JEN 1x)
                            proj.hit_enemies.add(e)            # Tak ho zapsat do setu (už je řízlej, podruhé tímto shurikenem damage nebude)
                            e.take_damage(proj.damage)         # Způsobí zranění stvůře
                            e.hit_flash = 6                    # Signalizace zásahu na sprite
                            if hasattr(e, 'apply_knockback'):  # Podařilo se
                                e.apply_knockback(proj.rect)   # Zpětný náraz ho naopak o kus posune pryč
                            if e.is_dead():                    # Nepřítel usmrcen okamžitě
                                items.add(Item(e.rect.x, e.rect.y, 'xp', xp_value=e.xp_value)) # Vypadne modrá hvězdička (XPčka na level-up)
                                if random.random() < 0.3:      # 30% šance na drop peněz
                                    items.add(Item(e.rect.x + random.randint(-10, 10), # Plus šance i vedle občas hodit
                                                   e.rect.y + random.randint(-10, 10), # TODO_COMMENT
                                                   'money', xp_value=random.randint(1, 3))) # Vypadnou zlaté peníze s odchylkou souřadnice, ne doprostřed
                                e.kill()                       # Zničení mrtvého nepřítele
                                score += 10                    # Přidá 10 bodů do skóre

            # Wave timer                                        # Wave timer
            wave_timer += 1                                    # Zvýší časovač
            if wave_timer >= WAVE_DURATION:                    # Pokud vlna skončila (2 minuty)
                wave_timer = 0                                 # Resetuje časovač
                wave_number += 1                               # Další vlna
                current_spawn_interval = ENEMY_SPAWN_INTERVAL  # Resetuje interval spawnu

                # Boss spawn na konci vlny                      # Boss spawn na konci vlny
                bx, by = spawn_at_screen_edge(camera, ENEMY_SIZE * 3) # Pozice za okrajem
                boss = Enemy(bx, by, 'boss')                   # Vytvoří bosse
                boss.health += (wave_number - 2) * 200         # Boss je silnější v pozdějších vlnách (+200 HP za vlnu)
                boss.damage += (wave_number - 2) * 10          # Boss dělá více poškození (+10 za vlnu)
                enemies.add(boss)                              # Přidá bosse na mapu

            # Spawn nepřátel v čase (wave style)                # Spawn nepřátel v čase (wave style)
            spawn_timer += 1                                   # Zvýší časovač spawnu
            if spawn_timer >= current_spawn_interval:          # Pokud je čas na spawn
                spawn_timer = 0                                # Resetuje časovač
                total_spawns += 1                              # Zvýší celkový počet spawnů
                current_spawn_interval = max(15, int(current_spawn_interval * ENEMY_SPAWN_ACCELERATION)) # Zkrátí interval (min 15 snímků)

                spawn_count = int(min(ENEMY_MAX_PER_WAVE, ENEMY_WAVE_BASE + (total_spawns - 1) * ENEMY_WAVE_GROWTH)) # Postupně rostoucí
                spawned = 0                                    # Kolik se už spawnulo
                attempts = 0                                   # Počet pokusů (ochrana proti nekonečné smyčce)

                while spawned < spawn_count and attempts < spawn_count * 8: # Pokouší se spawn nepřátel
                    if len(enemies) >= ENEMY_MAX_ON_MAP:       # Pokud je na mapě maximum nepřátel
                        break                                  # Přeruší výběr
                    attempts += 1                              # Zvýší počet pokusů

                    sx, sy = spawn_at_screen_edge(camera, ENEMY_SIZE + 20) # Náhodná pozice za okrajem

                    if math.hypot(sx - player.rect.centerx, sy - player.rect.centery) < ENEMY_SPAWN_RADIUS_MIN: # Příliš blízko hráči
                        continue                               # Proto přeskočíme, meč se počítá v klávesách `handle_input`

                    enemy_types = ['walker', 'flying', 'tank', 'fast'] # Seznam typů
                    wave_type_index = (wave_number - 1) % len(enemy_types) # Index podle čísla vlny
                    enemy_type = enemy_types[wave_type_index]  # Typ pro tuto vlnu
                    enemies.add(Enemy(sx, sy, enemy_type))     # Vytvoří a přidá nepřítele
                    spawned += 1                               # Zvýší počet spawnutých

            # Světové hranice: hráč a nepřátelé nesmí mimo      # Světové hranice: hráč a nepřátelé nesmí mimo
            if player.rect.left < 0:                           # Levý okraj
                player.rect.left = 0                           # Zastaví
                player.vel_x = 0                               # Zastaví pohyb
            if player.rect.right > WORLD_WIDTH_PX:             # Pravý okraj
                player.rect.right = WORLD_WIDTH_PX             # Zastaví
                player.vel_x = 0                               # Zastaví pohyb
            if player.rect.top < 0:                            # Horní okraj
                player.rect.top = 0                            # Zastaví
                player.vel_y = 0                               # TODO_COMMENT

            if player.rect.top > WORLD_HEIGHT_PX + 5*BLOCK_SIZE: # Pokud hráč spadl hodně mimo mapu (zcela pod světem)
                # pokud spadne hráč hodně dolů mimo mapu, resetujeme pozici # pokud spadne hráč hodně dolů mimo mapu, resetujeme pozici
                player.rect.x = start_x                        # Resetuje pozici na start
                player.rect.y = start_y                        # TODO_COMMENT
                player.vel_x = 0                               # Zastaví pohyb
                player.vel_y = 0                               # TODO_COMMENT

            # Odstranění nepřátel mimo svět                     # Odstranění nepřátel mimo svět
            for spr in list(enemies):                          # Pro každého nepřítele (kopie kvůli mazání)
                if isinstance(spr, Enemy):                     # Jen pro Enemy objekty
                    if (spr.rect.right < 0 or spr.rect.left > WORLD_WIDTH_PX or # TODO_COMMENT
                        spr.rect.top < 0 or spr.rect.bottom > WORLD_HEIGHT_PX + 5*BLOCK_SIZE): # Mimo svět
                        spr.kill()                             # Odstraní nepřítele z mapy

            # Kolize hráče s nepřáteli                          # Kolize hráče s nepřáteli
            for spr in enemies:                                # Pro každého nepřítele
                if isinstance(spr, Enemy) and player.rect.colliderect(spr.rect): # Pokud se hráč dotýká nepřítele
                    if player.hit_cooldown <= 0:               # Pokud nemá imunitu
                        player.take_damage(spr.damage)         # Dostane poškození
                        player.hit_cooldown = PLAYER_HIT_COOLDOWN # Zapne imunitu
                        # odskok pouze při zranění a mírnější (1.5x speed a 7 snímků) # odskok pouze při zranění a mírnější (1.5x speed a 7 snímků)
                        if player.rect.centerx < spr.rect.centerx: # Nepřítel je vpravo
                            player.vel_x = -PLAYER_SPEED * 1.5 # Odskok doleva
                        else:                                  # Pokud se nevlezla
                            player.vel_x = PLAYER_SPEED * 1.5  # Odskok doprava
                        if player.rect.centery < spr.rect.centery: # Nepřítel je dole
                            player.vel_y = -PLAYER_SPEED * 1.5 # Odskok nahoru
                        else:                                  # Pokud se nevlezla
                            player.vel_y = PLAYER_SPEED * 1.5  # Odskok dolů
                        player.knockback_timer = 7             # Knockback trvá 7 snímků

            # Kolize útoku (meč) s nepřáteli - používá sword weapon stats # Kolize útoku (meč) s nepřáteli - používá sword weapon stats
            if player.attacking:                               # Pokud hráč útočí
                sword_damage = player.get_sword_damage()       # TODO_COMMENT
                for spr in list(enemies):                      # Pro každého nepřítele (kopie kvůli mazání)
                    if isinstance(spr, Enemy) and spr not in player.hit_enemies and player.attack_hits(spr): # Zasažen a ještě nebyl v tomto švihu
                        player.hit_enemies.add(spr)            # Označí jako zasaženého (aby nedostal 2× dmg)
                        spr.take_damage(sword_damage)          # TODO_COMMENT
                        if hasattr(spr, 'apply_knockback'):    # Ověří, zda má knockback metodu
                            spr.apply_knockback(player.rect)   # Aplikuje knockback od hráče
                        if spr.is_dead():                      # Pokud nepřítel zemřel
                            items.add(Item(spr.rect.x, spr.rect.y, 'xp', xp_value=spr.xp_value)) # Dropne XP orb
                            if random.random() < 0.3:          # 30% šance na drop peněz
                                items.add(Item(spr.rect.x + random.randint(-10, 10), spr.rect.y + random.randint(-10, 10), 'money', xp_value=random.randint(1, 3))) # Dropne 1-3 mincí
                            spr.kill()                         # Odstraní nepřítele z mapy
                            score += 10                        # Přidá 10 bodů do skóre

            # Kolize s předměty                                 # Kolize s předměty
            item_hits = pygame.sprite.spritecollide(player, items, True) # Najde všechny předměty překrývající hráče (True = smaže je)
            for item in item_hits:                             # Pro každý sebraný předmět
                item.apply(player)                             # Aplikuje efekt (heal, XP, boost atd.)



            # Kamera                                            # Kamera
            camera.update(player)                              # Centruje kameru na hráče


        # Vytvoření menšího plátna pro renderování hry (pro zoom) # Vytvoření menšího plátna pro renderování hry (pro zoom)
        cam_w = int(WINDOW_WIDTH / ZOOM)                       # Šířka plátna po zoomu
        cam_h = int(WINDOW_HEIGHT / ZOOM)                      # Výška plátna po zoomu
        display_surface = pygame.Surface((cam_w, cam_h))       # Menší surface pro vykreslení hry

        # Kreslení travnatého pozadí                            # Kreslení travnatého pozadí
        display_surface.fill((34, 110, 34))                    # Základní zelená
        bg_offset_x = camera.rect.x % 64                       # Offset pozadí X (pro scrollování)
        bg_offset_y = camera.rect.y % 64                       # Offset pozadí Y
        for i in range(-64, cam_w + 64, 64):                   # Vodorovné dlaždice
            for j in range(-64, cam_h + 64, 64):               # Svislé dlaždice
                pygame.draw.rect(display_surface, (30, 100, 30), (i + bg_offset_x, j + bg_offset_y, 32, 32)) # Tmavší čtvereček
                pygame.draw.rect(display_surface, (30, 100, 30), (i + 32 + bg_offset_x, j + 32 + bg_offset_y, 32, 32)) # Tmavší čtvereček (diagonálně)

        # Obdélník pro culling (vykreslení jen na obrazovce)    # Obdélník pro culling (vykreslení jen na obrazovce)
        screen_rect = pygame.Rect(0, 0, cam_w, cam_h)          # Oblast viditelná na obrazovce

        # Kreslení bloků v kameře                               # Kreslení bloků v kameře
        for block in blocks:                                   # Pro každý blok
            screen_pos = camera.apply(block)                   # Pozice na obrazovce
            if screen_rect.colliderect(screen_pos):            # Pokud je viditelný (culling optimalizace)
                display_surface.blit(block.image, screen_pos)  # Vykreslí blok

        # Kreslení předmětů                                     # Kreslení předmětů
        for item in items:                                     # Pro každý předmět
            display_surface.blit(item.image, camera.apply(item)) # Vykreslí na správné pozici

        # Kreslení projektilů (shurikeny)                       # Kreslení projektilů (shurikeny)
        for proj in projectiles:                               # TODO_COMMENT
            proj_pos = camera.apply(proj)                      # TODO_COMMENT
            if screen_rect.colliderect(proj_pos):              # TODO_COMMENT
                display_surface.blit(proj.image, proj_pos)     # TODO_COMMENT

        # Kreslení nepřátel                                     # Kreslení nepřátel
        for enemy in enemies:                                  # Pro každého nepřítele
            if getattr(enemy, 'hit_flash', 0) > 0 and hasattr(enemy, 'flash_image'): # Pokud bliká (právě dostal zásah)
                display_surface.blit(enemy.flash_image, camera.apply(enemy)) # Bílá verze (flash)
            else:                                              # Pokud se nevlezla
                display_surface.blit(enemy.image, camera.apply(enemy)) # Normální obrázek

        # Kreslení hráče                                        # Kreslení hráče
        if player.hit_cooldown > 0 and (player.hit_cooldown // 4) % 2 == 0: # Pokud má imunitu a bliká (každé 4 snímky)
            mask = pygame.mask.from_surface(player.image)      # Vytvoří masku z obrázku
            flash_image = mask.to_surface(setcolor=(255, 50, 50, 255), unsetcolor=(0, 0, 0, 0)) # Červená verze
            display_surface.blit(flash_image, camera.apply(player)) # Vykreslí červeného hráče
        else:                                                  # Pokud se nevlezla
            display_surface.blit(player.image, camera.apply(player)) # Normální hráč

        # Kreslení útoku (meč swoosh)                           # Kreslení útoku (meč swoosh)
        player.draw_attack(display_surface, camera)            # Vykreslí srpkovitý efekt

        # Kreslení fire ring efektu                             # Kreslení fire ring efektu
        player.draw_fire_ring(display_surface, camera)         # TODO_COMMENT

        # Kreslení lightning efektu                             # Kreslení lightning efektu
        player.draw_lightning(display_surface, camera)         # TODO_COMMENT

        # Škálování kamery na celou obrazovku                   # Škálování kamery na celou obrazovku
        scaled_surf = pygame.transform.scale(display_surface, (WINDOW_WIDTH, WINDOW_HEIGHT)) # Škálování na plnou velikost
        screen.blit(scaled_surf, (0, 0))                       # Vykreslí na hlavní okno

        # UI                                                    # UI

        wave_time_left = (WAVE_DURATION - wave_timer) // FPS   # Zbývající čas vlny v sekundách
        minutes = wave_time_left // 60                         # Minuty
        seconds = wave_time_left % 60                          # Sekundy
        wave_text = font_ui.render(f"Wave: {wave_number} ({minutes}:{seconds:02d})", True, ORANGE) # Text vlny (oranžový)
        screen.blit(wave_text, (WINDOW_WIDTH // 2 - wave_text.get_width() // 2, 10)) # Centrováno nahoře
        level_text = font_ui.render(f"Level: {player.level} ({player.xp}/{player.max_xp} XP)", True, CYAN) # Tyrkysový text
        screen.blit(level_text, (10, 10))                      # Vlevo nahoře
        health_text = font_ui.render(f"Health: {player.health}/{player.max_health}", True, WHITE) # Bílý text
        screen.blit(health_text, (10, 50))                     # Pod levelem
        score_text = font_ui.render(f"Score: {score}", True, WHITE) # TODO_COMMENT
        screen.blit(score_text, (10, 90))                      # Pod zdravím
        key_text = font_ui.render(f"Keys: {player.keys}", True, WHITE) # TODO_COMMENT
        screen.blit(key_text, (10, 130))                       # Pod skóre
        money_text = font_ui.render(f"Coins: {player.money}", True, (255, 215, 0)) # TODO_COMMENT
        screen.blit(money_text, (10, 170))                     # Pod klíči

        # Sword damage display                                  # Sword damage display
        sword_dmg = int(player.get_sword_damage())             # TODO_COMMENT
        damage_text = font_ui.render(f"Sword Dmg: {sword_dmg}", True, RED) # TODO_COMMENT
        screen.blit(damage_text, (10, 210))                    # Pod penězi
        if player.damage_boost > 1:                            # Pokud je boost aktivní
            boost_text = font_ui.render(f"Damage Boost: {player.damage_boost_timer//60}s", True, YELLOW) # Zbývající sekundy
            screen.blit(boost_text, (10, 250))                 # Pod poškozením

        # Weapon slots display (pravý horní roh)                # Weapon slots display (pravý horní roh)
        wp_y = 10                                              # TODO_COMMENT
        wp_x = WINDOW_WIDTH - 200                              # TODO_COMMENT
        wp_title = font_desc.render("Weapons:", True, (255, 200, 100)) # TODO_COMMENT
        screen.blit(wp_title, (wp_x, wp_y))                    # TODO_COMMENT
        wp_y += 22                                             # TODO_COMMENT
        for wid, wlevel in player.weapons.items():             # TODO_COMMENT
            wname = WEAPON_DEFS[wid]["name"]                   # TODO_COMMENT
            wcol = WEAPON_DEFS[wid]["icon_color"]              # TODO_COMMENT
            w_text = font_desc.render(f"{wname} Lv.{wlevel}", True, wcol) # TODO_COMMENT
            screen.blit(w_text, (wp_x, wp_y))                  # TODO_COMMENT
            wp_y += 20                                         # TODO_COMMENT

        # Tome display                                          # Tome display
        if player.tomes:                                       # TODO_COMMENT
            wp_y += 5                                          # TODO_COMMENT
            tome_title = font_desc.render("Tomes:", True, (100, 255, 200)) # TODO_COMMENT
            screen.blit(tome_title, (wp_x, wp_y))              # TODO_COMMENT
            wp_y += 22                                         # TODO_COMMENT
            for tid, tlevel in player.tomes.items():           # TODO_COMMENT
                tname = TOME_DEFS[tid]["name"]                 # TODO_COMMENT
                tcol = TOME_DEFS[tid]["icon_color"]            # TODO_COMMENT
                t_text = font_desc.render(f"{tname} x{tlevel}", True, tcol) # TODO_COMMENT
                screen.blit(t_text, (wp_x, wp_y))              # TODO_COMMENT
                wp_y += 20                                     # TODO_COMMENT

        # Level-up screen                                       # Level-up screen
        if is_level_up_screen:                                 # Pokud je zobrazeno upgrade menu
            draw_level_up_screen(screen, upgrades_offered, player, fonts) # TODO_COMMENT

        pygame.display.flip()                                  # Aktualizuje obrazovku menu

        # Konec hry (smrt)                                      # Konec hry (smrt)
        if player.is_dead():                                   # Pokud je hráč mrtvý
            death_timer += 1                                   # Zvyšuje časovač smrti
            if death_timer > 90:                               # Po ~1.5 sekundě
                menu_font = pygame.font.Font(None, 100)        # Font pro titulek (100 px)
                info_font = pygame.font.Font(None, 40)         # Font pro nápovědu (40 px)
                action = show_death_screen(screen, score, wave_number, menu_font, info_font) # Zobrazí death screen
                if action == "retry":                          # Retry – hráč chce hrát znovu
                    return "retry"                             # Vrátí "retry" → hlavní smyčka restartuje hru
                else:                                          # Pokud se nevlezla
                    return "menu"                              # Vrátí "menu" → vrátí se do hlavního menu

    return "quit"                                              # Pokud se herní smyčka ukončí normálně (ESC)

# =============================================                 # =============================================
# Character Select Screen                                       # Character Select Screen
# =============================================                 # =============================================
def show_character_select(screen, current_character="knight"): # TODO_COMMENT
    """Zobrazí obrazovku výběru postavy s animovanými náhledy.""" # TODO_COMMENT
    clock = pygame.time.Clock()                                # Časovač (FPS kontroler)
    title_font = pygame.font.Font(None, 80)                    # TODO_COMMENT
    name_font = pygame.font.Font(None, 48)                     # TODO_COMMENT
    desc_font = pygame.font.Font(None, 28)                     # TODO_COMMENT
    btn_font = pygame.font.Font(None, 50)                      # TODO_COMMENT

    char_ids = list(CHARACTER_DEFS.keys())                     # Získá všechny ID postav do seznamu (knight, mage, rogue...)
    selected = char_ids.index(current_character) if current_character in char_ids else 0 # TODO_COMMENT

    # Předvykreslení náhledů postav (zvětšené 5×)               # Předvykreslení náhledů postav (zvětšené 5×)
    scale = 5                                                  # TODO_COMMENT
    previews = {}                                              # TODO_COMMENT
    walk_frames = {}                                           # TODO_COMMENT
    for cid in char_ids:                                       # TODO_COMMENT
        cdef = CHARACTER_DEFS[cid]                             # TODO_COMMENT
        # Idle frame                                            # Idle frame
        surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA) # TODO_COMMENT
        draw_character_sprite(surf, cid, cdef)                 # TODO_COMMENT
        previews[cid] = pygame.transform.scale(surf, (PLAYER_WIDTH * scale, PLAYER_HEIGHT * scale)) # TODO_COMMENT
        # Walk frames                                           # Walk frames
        frames = []                                            # Prázdný seznam
        for step in range(4):                                  # TODO_COMMENT
            ws = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA) # TODO_COMMENT
            draw_character_sprite(ws, cid, cdef, is_walking=True, step=step) # TODO_COMMENT
            frames.append(pygame.transform.scale(ws, (PLAYER_WIDTH * scale, PLAYER_HEIGHT * scale))) # TODO_COMMENT
        walk_frames[cid] = frames                              # TODO_COMMENT

    anim_timer = 0                                             # Reset timeru

    # Částice pozadí                                            # Částice pozadí
    particles = []                                             # Seznam částic
    for _ in range(40):                                        # TODO_COMMENT
        particles.append([                                     # TODO_COMMENT
            random.randint(0, WINDOW_WIDTH),                   # TODO_COMMENT
            random.randint(0, WINDOW_HEIGHT),                  # TODO_COMMENT
            random.uniform(0.3, 1.5),                          # TODO_COMMENT
            random.randint(30, 80)                             # TODO_COMMENT
        ])                                                     # TODO_COMMENT

    while True:                                                # Menu smyčka, běží, dokud hráč nevybere postavu
        mx, my = pygame.mouse.get_pos()                        # Pozice kurzoru myši pro interakci
        clicked = False                                        # Flag kliknutí

        for event in pygame.event.get():                       # Zpracování uživatelských událostí
            if event.type == pygame.QUIT:                      # Kliknuto na křížek okna
                pygame.quit()                                  # Ukončí pygame
                sys.exit()                                     # Ukončí program
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Levé kliknutí
                clicked = True                                 # Nastaví flag
            elif event.type == pygame.KEYDOWN:                 # Stisk klávesy
                if event.key in (pygame.K_LEFT, pygame.K_a):   # TODO_COMMENT
                    selected = (selected - 1) % len(char_ids)  # TODO_COMMENT
                elif event.key in (pygame.K_RIGHT, pygame.K_d): # TODO_COMMENT
                    selected = (selected + 1) % len(char_ids)  # TODO_COMMENT
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE): # Enter / Space
                    return char_ids[selected]                  # TODO_COMMENT
                elif event.key == pygame.K_ESCAPE:             # TODO_COMMENT
                    return current_character                   # TODO_COMMENT

        anim_timer += 1                                        # Čas běží
        anim_frame = (anim_timer // 10) % 4                    # TODO_COMMENT

        # Update particles                                      # Update particles
        for p in particles:                                    # Pro každou částici
            p[1] -= p[2]                                       # Posun nahoru (rychlost)
            if p[1] < -10:                                     # Pokud vystoupala nad okraj
                p[1] = WINDOW_HEIGHT + 10                      # Vrátí se dolů
                p[0] = random.randint(0, WINDOW_WIDTH)         # Na náhodné X pozici

        # Pozadí                                                # Pozadí
        screen.fill((15, 15, 25))                              # TODO_COMMENT
        for p in particles:                                    # Pro každou částici
            pygame.draw.circle(screen, (p[3], p[3], p[3] + 20), # TODO_COMMENT
                               (int(p[0]), int(p[1])), int(p[2] * 2)) # TODO_COMMENT

        # Titulek                                               # Titulek
        title = title_font.render("SELECT CHARACTER", True, (255, 215, 0)) # TODO_COMMENT
        title_shadow = title_font.render("SELECT CHARACTER", True, (80, 60, 0)) # TODO_COMMENT
        screen.blit(title_shadow, (WINDOW_WIDTH // 2 - title.get_width() // 2 + 3, 53)) # Stín mírně posunutý doprava a dolů
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50)) # Skutečný žlutý nápis

        # Karty postav                                          # Karty postav
        card_w, card_h = 280, 420                              # TODO_COMMENT
        spacing = 40                                           # Odsazení mezi kartami
        total_w = len(char_ids) * card_w + (len(char_ids) - 1) * spacing # Celková šířka všech karet
        start_x = (WINDOW_WIDTH - total_w) // 2                # Vycentrování celého bloku na X ose okna
        start_y = (WINDOW_HEIGHT - card_h) // 2 + 20           # TODO_COMMENT

        for idx, cid in enumerate(char_ids):                   # TODO_COMMENT
            cdef = CHARACTER_DEFS[cid]                         # TODO_COMMENT
            cx = start_x + idx * (card_w + spacing)            # Odsazení každé karty X od začátku
            rect = pygame.Rect(cx, start_y, card_w, card_h)    # Vytvoření hranic
            is_selected = (idx == selected)                    # TODO_COMMENT
            hovered = rect.collidepoint(mx, my)                # Najetí myší na kartu postaví Hover Effect

            if hovered and clicked:                            # TODO_COMMENT
                selected = idx                                 # Zvýrazní

            # Glow efekt (vybraná)                              # Glow efekt (vybraná)
            if is_selected:                                    # Pokud se jedná o tu označenou postavu
                glow_surf = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA) # TODO_COMMENT
                glow_pulse = 30 + int(15 * math.sin(anim_timer * 0.05)) # TODO_COMMENT
                pygame.draw.rect(glow_surf, (255, 215, 0, glow_pulse), # TODO_COMMENT
                                 (0, 0, card_w + 20, card_h + 20), border_radius=16) # TODO_COMMENT
                screen.blit(glow_surf, (cx - 10, start_y - 10)) # TODO_COMMENT

            # Pozadí karty                                      # Pozadí karty
            bg = (45, 42, 60) if is_selected else (35, 35, 55) # TODO_COMMENT
            if hovered and not is_selected:                    # U neoznačené při najetí myší
                bg = (40, 40, 60)                              # TODO_COMMENT
            pygame.draw.rect(screen, bg, rect, border_radius=12) # TODO_COMMENT

            # Barevný gradient nahoře                           # Barevný gradient nahoře
            grad = pygame.Surface((card_w, card_h // 3), pygame.SRCALPHA) # TODO_COMMENT
            grad.fill((*cdef["shirt"], 20))                    # TODO_COMMENT
            screen.blit(grad, (cx, start_y))                   # TODO_COMMENT

            # Okraj                                             # Okraj
            border_col = (255, 215, 0) if is_selected else (80, 80, 100) # TODO_COMMENT
            border_w = 3 if is_selected else 2                 # TODO_COMMENT
            pygame.draw.rect(screen, border_col, rect, border_w, border_radius=12) # TODO_COMMENT

            # Náhled postavy                                    # Náhled postavy
            preview_y = start_y + 55                           # TODO_COMMENT
            if is_selected:                                    # Pokud se jedná o tu označenou postavu
                frame = walk_frames[cid][anim_frame]           # TODO_COMMENT
            else:                                              # Pokud se nevlezla
                frame = previews[cid]                          # TODO_COMMENT
            preview_rect = frame.get_rect(center=(rect.centerx, preview_y + PLAYER_HEIGHT * scale // 2)) # TODO_COMMENT
            screen.blit(frame, preview_rect)                   # TODO_COMMENT

            # Podstavec pod postavou                            # Podstavec pod postavou
            plat_y = preview_y + PLAYER_HEIGHT * scale - 5     # TODO_COMMENT
            plat_surf = pygame.Surface((70, 12), pygame.SRCALPHA) # TODO_COMMENT
            pygame.draw.ellipse(plat_surf, (0, 0, 0, 60), (0, 0, 70, 12)) # TODO_COMMENT
            screen.blit(plat_surf, (rect.centerx - 35, plat_y)) # TODO_COMMENT

            # Jméno                                             # Jméno
            name_col = (255, 255, 255) if is_selected else (180, 180, 180) # TODO_COMMENT
            name_surf = name_font.render(cdef["name"], True, name_col) # TODO_COMMENT
            screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, start_y + card_h - 120)) # TODO_COMMENT

            # Oddělovací čára                                   # Oddělovací čára
            sep_col = (255, 215, 0) if is_selected else (60, 60, 80) # TODO_COMMENT
            pygame.draw.line(screen, sep_col,                  # TODO_COMMENT
                             (cx + 30, start_y + card_h - 95), # TODO_COMMENT
                             (cx + card_w - 30, start_y + card_h - 95), 1) # TODO_COMMENT

            # Popis                                             # Popis
            desc_surf = desc_font.render(cdef["desc"], True, (160, 160, 180)) # TODO_COMMENT
            screen.blit(desc_surf, (rect.centerx - desc_surf.get_width() // 2, start_y + card_h - 75)) # TODO_COMMENT

            # "SELECTED" badge                                  # "SELECTED" badge
            if is_selected:                                    # Pokud se jedná o tu označenou postavu
                sel_surf = desc_font.render("\u2714 SELECTED", True, (255, 215, 0)) # TODO_COMMENT
                screen.blit(sel_surf, (rect.centerx - sel_surf.get_width() // 2, start_y + card_h - 40)) # TODO_COMMENT

        # Tlačítko Confirm                                      # Tlačítko Confirm
        confirm_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, start_y + card_h + 40, 300, 60) # TODO_COMMENT
        confirm_hover = confirm_rect.collidepoint(mx, my)      # TODO_COMMENT
        confirm_bg = (60, 140, 60) if confirm_hover else (40, 100, 40) # TODO_COMMENT
        pygame.draw.rect(screen, confirm_bg, confirm_rect, border_radius=12) # TODO_COMMENT
        pygame.draw.rect(screen, (100, 220, 100), confirm_rect, 2, border_radius=12) # TODO_COMMENT
        confirm_text = btn_font.render("Confirm", True, WHITE) # TODO_COMMENT
        screen.blit(confirm_text, (confirm_rect.centerx - confirm_text.get_width() // 2, # TODO_COMMENT
                                   confirm_rect.centery - confirm_text.get_height() // 2)) # TODO_COMMENT
        if confirm_hover and clicked:                          # TODO_COMMENT
            return char_ids[selected]                          # TODO_COMMENT

        # Tlačítko Back                                         # Tlačítko Back
        back_rect = pygame.Rect(30, WINDOW_HEIGHT - 70, 120, 45) # TODO_COMMENT
        back_hover = back_rect.collidepoint(mx, my)            # TODO_COMMENT
        back_bg = (70, 50, 50) if back_hover else (50, 35, 35) # TODO_COMMENT
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=8) # TODO_COMMENT
        pygame.draw.rect(screen, (150, 100, 100), back_rect, 2, border_radius=8) # TODO_COMMENT
        back_text = desc_font.render("< Back", True, (200, 200, 200)) # TODO_COMMENT
        screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, # TODO_COMMENT
                                back_rect.centery - back_text.get_height() // 2)) # TODO_COMMENT
        if back_hover and clicked:                             # TODO_COMMENT
            return current_character                           # TODO_COMMENT

        # Hints                                                 # Hints
        hint = desc_font.render("A/D to browse  |  Enter to confirm  |  Esc to go back", # TODO_COMMENT
                                True, (100, 100, 120))         # TODO_COMMENT
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, WINDOW_HEIGHT - 30)) # TODO_COMMENT

        pygame.display.flip()                                  # Aktualizuje obrazovku menu
        clock.tick(FPS)                                        # 60 FPS


# Hlavní menu                                                   # Hlavní menu
def main_menu(selected_character="knight"):                    # TODO_COMMENT
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME) # Fullscreen borderless okno
    pygame.display.set_caption(TITLE)                          # Titulek okna
    clock = pygame.time.Clock()                                # Časovač (FPS kontroler)
    menu_font = pygame.font.Font(None, 100)                    # Font pro titulek (100 px)
    info_font = pygame.font.Font(None, 40)                     # Font pro nápovědu (40 px)
    btn_font = pygame.font.Font(None, 60)                      # Font pro tlačítka (60 px)
    char_font = pygame.font.Font(None, 28)                     # TODO_COMMENT
    options = ["Start Game", "Characters", "Quit"]             # TODO_COMMENT
    selected = 0                                               # Výchozí výběr (Start Game)

    # Animace pro pozadí menu                                   # Animace pro pozadí menu
    particles = []                                             # Seznam částic
    for _ in range(50):                                        # 50 částic
        particles.append([random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), # TODO_COMMENT
                          random.uniform(0.5, 2.0)])           # TODO_COMMENT

    # Mini náhled aktuální postavy                              # Mini náhled aktuální postavy
    def make_preview(cid):                                     # TODO_COMMENT
        cdef = CHARACTER_DEFS.get(cid, CHARACTER_DEFS["knight"]) # TODO_COMMENT
        surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA) # TODO_COMMENT
        draw_character_sprite(surf, cid, cdef)                 # TODO_COMMENT
        return pygame.transform.scale(surf, (PLAYER_WIDTH * 3, PLAYER_HEIGHT * 3)) # TODO_COMMENT

    char_preview = make_preview(selected_character)            # TODO_COMMENT

    while True:                                                # Menu smyčka, běží, dokud hráč nevybere postavu
        mx, my = pygame.mouse.get_pos()                        # Pozice kurzoru myši pro interakci
        clicked = False                                        # Flag kliknutí

        for event in pygame.event.get():                       # Zpracování uživatelských událostí
            if event.type == pygame.QUIT:                      # Kliknuto na křížek okna
                pygame.quit()                                  # Ukončí pygame
                sys.exit()                                     # Ukončí program
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Levé kliknutí
                clicked = True                                 # Nastaví flag
            elif event.type == pygame.KEYDOWN:                 # Stisk klávesy
                if event.key in (pygame.K_UP, pygame.K_w):     # Nahoru / W
                    selected = (selected - 1) % len(options)   # Přesune výběr nahoru
                elif event.key in (pygame.K_DOWN, pygame.K_s): # Dolů / S
                    selected = (selected + 1) % len(options)   # Přesune výběr dolů
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE): # Enter / Space
                    if options[selected] == "Start Game":      # Start Game
                        return ("start", selected_character)   # TODO_COMMENT
                    elif options[selected] == "Characters":    # TODO_COMMENT
                        selected_character = show_character_select(screen, selected_character) # TODO_COMMENT
                        char_preview = make_preview(selected_character) # TODO_COMMENT
                    else:                                      # Pokud se nevlezla
                        pygame.quit()                          # Ukončí pygame
                        sys.exit()                             # Ukončí program

        # Update částic                                         # Update částic
        for p in particles:                                    # Pro každou částici
            p[1] -= p[2]                                       # Posun nahoru (rychlost)
            if p[1] < -10:                                     # Pokud vystoupala nad okraj
                p[1] = WINDOW_HEIGHT + 10                      # Vrátí se dolů
                p[0] = random.randint(0, WINDOW_WIDTH)         # Na náhodné X pozici

        screen.fill((20, 30, 20))                              # Tmavě zelené pozadí

        for p in particles:                                    # Pro každou částici
            pygame.draw.circle(screen, (50, 80, 50), (int(p[0]), int(p[1])), int(p[2] * 2)) # Zelený kroužek

        # Titulek                                               # Titulek
        title_surf = menu_font.render(TITLE, True, (255, 215, 0)) # Zlatý text
        title_shadow = menu_font.render(TITLE, True, (0, 0, 0)) # Černý stín
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)) # Centrováno nahoře
        screen.blit(title_shadow, title_rect.move(4, 4))       # Stín posunutý o 4 px
        screen.blit(title_surf, title_rect)                    # Text přes stín

        # Mini náhled aktuální postavy vedle titulku            # Mini náhled aktuální postavy vedle titulku
        char_name = CHARACTER_DEFS.get(selected_character, CHARACTER_DEFS["knight"])["name"] # TODO_COMMENT
        preview_x = WINDOW_WIDTH // 2 + title_surf.get_width() // 2 + 30 # TODO_COMMENT
        preview_y = WINDOW_HEIGHT // 4 - PLAYER_HEIGHT * 3 // 2 # TODO_COMMENT
        screen.blit(char_preview, (preview_x, preview_y))      # TODO_COMMENT
        char_label = char_font.render(char_name, True, (180, 200, 180)) # TODO_COMMENT
        screen.blit(char_label, (preview_x + PLAYER_WIDTH * 3 // 2 - char_label.get_width() // 2, # TODO_COMMENT
                                 preview_y + PLAYER_HEIGHT * 3 + 5)) # TODO_COMMENT

        # Kreslení tlačítek                                     # Kreslení tlačítek
        button_width = 300                                     # Šířka tlačítka
        button_height = 80                                     # Výška tlačítka
        btn_start_y = WINDOW_HEIGHT // 2 - 40                  # TODO_COMMENT
        for idx, option in enumerate(options):                 # Pro každou možnost
            btn_rect = pygame.Rect(0, 0, button_width, button_height) # Obdélník tlačítka
            btn_rect.center = (WINDOW_WIDTH // 2, btn_start_y + idx * 100) # TODO_COMMENT

            if btn_rect.collidepoint(mx, my):                  # Pokud myš je nad tlačítkem
                selected = idx                                 # Zvýrazní
                if clicked:                                    # Pokud klik
                    if options[selected] == "Start Game":      # Start Game
                        return ("start", selected_character)   # TODO_COMMENT
                    elif options[selected] == "Characters":    # TODO_COMMENT
                        selected_character = show_character_select(screen, selected_character) # TODO_COMMENT
                        char_preview = make_preview(selected_character) # TODO_COMMENT
                    else:                                      # Pokud se nevlezla
                        pygame.quit()                          # Ukončí pygame
                        sys.exit()                             # Ukončí program

            color_bg = (50, 150, 50) if idx == selected else (30, 80, 30) # Zelení pozadí (vybraný/nevybraný)
            color_text = WHITE if idx == selected else (200, 200, 200) # Barva textu

            pygame.draw.rect(screen, color_bg, btn_rect, border_radius=15) # Pozadí tlačítka
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15) # Okraj tlačítka

            option_surf = btn_font.render(option, True, color_text) # Text tlačítka
            option_rect = option_surf.get_rect(center=btn_rect.center) # Centrováno v tlačítku
            screen.blit(option_surf, option_rect)              # Vykreslí text

        info_surf = info_font.render("Use W/S/Mouse to choose, Enter/Click to confirm", # TODO_COMMENT
                                     True, (100, 200, 100))    # TODO_COMMENT
        info_rect = info_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60)) # Centrováno dole
        screen.blit(info_surf, info_rect)                      # Vykreslí

        pygame.display.flip()                                  # Aktualizuje obrazovku menu
        clock.tick(FPS)                                        # 60 FPS


if __name__ == "__main__":                                     # Spustí se pouze pokud se soubor spouští přímo (ne importuje)
    selected_character = "knight"                              # TODO_COMMENT
    while True:                                                # Menu smyčka, běží, dokud hráč nevybere postavu
        result = main_menu(selected_character)                 # TODO_COMMENT
        if result is None:                                     # TODO_COMMENT
            break                                              # Přeruší výběr
        action, selected_character = result                    # TODO_COMMENT
        if action == "quit":                                   # Pokud hráč zvolil ukončení
            break                                              # Přeruší výběr

        while True:                                            # Menu smyčka, běží, dokud hráč nevybere postavu
            action = main(selected_character)                  # TODO_COMMENT
            if action == "retry":                              # Retry – hráč chce hrát znovu
                continue                                       # Proto přeskočíme, meč se počítá v klávesách `handle_input`
            elif action == "menu":                             # Menu – hráč chce zpět do menu
                break                                          # Přeruší výběr
            elif action == "quit":                             # Quit – ukončení
                pygame.quit()                                  # Ukončí pygame
                sys.exit()                                     # Ukončí program
