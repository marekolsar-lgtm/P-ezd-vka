import pygame
import random
import math
import sys
from typing import TypedDict, List, Tuple

class RoomDict(TypedDict):
    x: int
    y: int
    width: int
    height: int
    grid_x: int
    grid_y: int
    doors: List[Tuple[int, int]]

# Inicializace Pygame
pygame.init()

# Konstanty pro borderless fullscreen
infoObject = pygame.display.Info()
WINDOW_WIDTH = infoObject.current_w
WINDOW_HEIGHT = infoObject.current_h
TITLE = "Survival Game"
FPS = 60
ZOOM = 1.5  # Míra přiblížení

RARITY_COLORS = {
    "Common": (200, 200, 200),
    "Uncommon": (50, 205, 50),
    "Rare": (30, 144, 255),
    "Epic": (138, 43, 226),
    "Legendary": (255, 215, 0)
}

# Barvy (použijeme pro textury, ale některé ponecháme pro záložní)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Velikost bloku
BLOCK_SIZE = 32

# Rozměry dungeonu (počet místností v řadě/sloupci)
DUNGEON_SIZE = 5
ROOM_MIN_SIZE = 5  # minimální počet bloků na šířku/výšku místnosti
ROOM_MAX_SIZE = 10

# Hráč
PLAYER_WIDTH = 28
PLAYER_HEIGHT = 28
PLAYER_SPEED = 5

# Nepřátelé
ENEMY_SIZE = 28
ENEMY_SPEED = 2
FLYING_ENEMY_SPEED = 1
ENEMY_SPAWN_INTERVAL = 60  # snímků mezi spawnem (1s při 60FPS)
ENEMY_SPAWN_RADIUS_MIN = 300  # minimální vzdálenost od hráče při spawnu
ENEMY_SPAWN_ACCELERATION = 0.985  # zrychlování intervalu (max speed za cca 5 minut)
ENEMY_WAVE_BASE = 1  # začátek po jednom
ENEMY_WAVE_GROWTH = 0.05  # přidá enemáka každých 20 vln (pomalejší škálování)
ENEMY_MAX_PER_WAVE = 10  # do maxima 10
ENEMY_MAX_ON_MAP = 40  # maximální počet nepřátel najednou na mapě (lze změnit)
WAVE_DURATION = 7200  # 2 minuty při 60 FPS

# Útok
ATTACK_DURATION = 10
ATTACK_SIZE = 40
ATTACK_DAMAGE = 10
BASE_ATTACK_COOLDOWN = 40  # počet snímků mezi útoky

# Zdraví hráče
PLAYER_MAX_HEALTH = 100
PLAYER_HIT_COOLDOWN = 30  # snímků imunita po zásahu

# Předměty
ITEM_SIZE = 24
HEAL_AMOUNT = 2
DAMAGE_BOOST = 2  # zvýšení útoku
DAMAGE_BOOST_DURATION = 300  # snímků

# =============================================
# MegaBonk-style Weapon & Tome Definitions
# =============================================
MAX_WEAPON_LEVEL = 5
MAX_WEAPON_SLOTS = 4
REROLL_BASE_COST = 3

WEAPON_DEFS = {
    "sword": {
        "name": "Sword",
        "icon_color": (200, 200, 220),
        "type": "weapon",
        "levels": {
            1: {"damage": 10, "cooldown": 40, "size": 1.0, "desc": "Basic melee slash"},
            2: {"damage": 15, "cooldown": 35, "size": 1.2, "desc": "+Damage, +Size"},
            3: {"damage": 22, "cooldown": 28, "size": 1.4, "desc": "+Damage, Faster"},
            4: {"damage": 30, "cooldown": 22, "size": 1.7, "desc": "+Damage, +Size"},
            5: {"damage": 42, "cooldown": 16, "size": 2.0, "desc": "MAX: Massive Blade"},
        }
    },
    "shuriken": {
        "name": "Shuriken",
        "icon_color": (180, 180, 200),
        "type": "weapon",
        "levels": {
            1: {"damage": 8, "cooldown": 90, "count": 1, "speed": 5, "desc": "Throws 1 shuriken"},
            2: {"damage": 11, "cooldown": 75, "count": 2, "speed": 5.5, "desc": "2 shurikens"},
            3: {"damage": 15, "cooldown": 60, "count": 3, "speed": 6, "desc": "3 shurikens"},
            4: {"damage": 20, "cooldown": 50, "count": 4, "speed": 6.5, "desc": "4 shurikens!"},
            5: {"damage": 28, "cooldown": 35, "count": 6, "speed": 7, "desc": "MAX: Shuriken Storm"},
        }
    },
    "fire_ring": {
        "name": "Fire Ring",
        "icon_color": (255, 100, 30),
        "type": "weapon",
        "levels": {
            1: {"damage": 4, "cooldown": 180, "radius": 60, "duration": 40, "desc": "Fire burst around you"},
            2: {"damage": 7, "cooldown": 150, "radius": 80, "duration": 45, "desc": "+Damage, +Radius"},
            3: {"damage": 11, "cooldown": 120, "radius": 100, "duration": 50, "desc": "Bigger & stronger"},
            4: {"damage": 16, "cooldown": 90, "radius": 120, "duration": 55, "desc": "Huge fire ring"},
            5: {"damage": 24, "cooldown": 60, "radius": 150, "duration": 60, "desc": "MAX: Inferno"},
        }
    },
    "lightning": {
        "name": "Lightning",
        "icon_color": (100, 180, 255),
        "type": "weapon",
        "levels": {
            1: {"damage": 20, "cooldown": 150, "targets": 1, "desc": "Strikes nearest enemy"},
            2: {"damage": 28, "cooldown": 125, "targets": 2, "desc": "Chains to 2"},
            3: {"damage": 38, "cooldown": 100, "targets": 3, "desc": "3 targets"},
            4: {"damage": 50, "cooldown": 80, "targets": 4, "desc": "4 chain lightning"},
            5: {"damage": 65, "cooldown": 55, "targets": 5, "desc": "MAX: Thunder Storm"},
        }
    }
}

TOME_DEFS = {
    "vitality": {
        "name": "Vitality Tome",
        "icon_color": (255, 80, 80),
        "type": "tome",
        "stat": "max_health",
        "per_level": 10,
        "desc": "+10 Max HP",
        "max_level": 10,
    },
    "power": {
        "name": "Power Tome",
        "icon_color": (255, 165, 0),
        "type": "tome",
        "stat": "damage_mult",
        "per_level": 0.1,
        "desc": "+10% Damage",
        "max_level": 10,
    },
    "speed": {
        "name": "Speed Tome",
        "icon_color": (0, 200, 255),
        "type": "tome",
        "stat": "speed",
        "per_level": 0.3,
        "desc": "+0.3 Speed",
        "max_level": 8,
    },
    "haste": {
        "name": "Haste Tome",
        "icon_color": (255, 255, 100),
        "type": "tome",
        "stat": "cooldown_mult",
        "per_level": 0.05,
        "desc": "-5% Cooldown",
        "max_level": 10,
    },
    "luck": {
        "name": "Luck Tome",
        "icon_color": (0, 255, 100),
        "type": "tome",
        "stat": "luck",
        "per_level": 1,
        "desc": "+1 Luck (better rarity)",
        "max_level": 5,
    }
}

# =============================================
# Helper funkce pro upgrade systém
# =============================================

def get_rarity_for_level(level):
    """Vrátí raritu podle úrovně upgradu."""
    if level <= 1:
        return "Common"
    elif level == 2:
        return "Uncommon"
    elif level == 3:
        return "Rare"
    elif level == 4:
        return "Epic"
    else:
        return "Legendary"

def generate_upgrade_offers(player):
    """Vygeneruje 3 náhodné nabídky upgradu z dostupných zbraní a tomů."""
    available = []

    # Upgrady existujících zbraní (co ještě nejsou na maxu)
    for wid, level in player.weapons.items():
        if level < MAX_WEAPON_LEVEL:
            next_level = level + 1
            stats = WEAPON_DEFS[wid]["levels"][next_level]
            rarity = get_rarity_for_level(next_level)
            available.append({
                "type": "weapon_upgrade",
                "id": wid,
                "name": WEAPON_DEFS[wid]["name"],
                "icon_color": WEAPON_DEFS[wid]["icon_color"],
                "rarity": rarity,
                "desc": stats["desc"],
                "current_level": level,
                "next_level": next_level,
            })

    # Nové zbraně (pokud je slot volný)
    if len(player.weapons) < MAX_WEAPON_SLOTS:
        for wid, wdef in WEAPON_DEFS.items():
            if wid not in player.weapons:
                stats = wdef["levels"][1]
                available.append({
                    "type": "weapon_new",
                    "id": wid,
                    "name": wdef["name"],
                    "icon_color": wdef["icon_color"],
                    "rarity": "Common",
                    "desc": stats["desc"],
                    "current_level": 0,
                    "next_level": 1,
                })

    # Tomy
    for tid, tdef in TOME_DEFS.items():
        current = player.tomes.get(tid, 0)
        if current < tdef["max_level"]:
            next_level = current + 1
            rarity = get_rarity_for_level(next_level)
            available.append({
                "type": "tome",
                "id": tid,
                "name": tdef["name"],
                "icon_color": tdef["icon_color"],
                "rarity": rarity,
                "desc": tdef["desc"],
                "current_level": current,
                "next_level": next_level,
            })

    if not available:
        return []

    # Váhy podle rarity a luck
    luck = player.luck
    weights = []
    for offer in available:
        base_w = {"Common": 50, "Uncommon": 30, "Rare": 15, "Epic": 7, "Legendary": 2}
        w = base_w.get(offer["rarity"], 10)
        if offer["rarity"] in ["Rare", "Epic", "Legendary"]:
            w += luck * 3
        weights.append(max(1, w))

    # Vyber 3 unikátní
    offers = []
    avail_copy = list(available)
    w_copy = list(weights)
    for _ in range(min(3, len(avail_copy))):
        if not avail_copy:
            break
        chosen = random.choices(avail_copy, weights=w_copy, k=1)[0]
        idx = avail_copy.index(chosen)
        offers.append(chosen)
        avail_copy.pop(idx)
        w_copy.pop(idx)

    return offers

def apply_upgrade(player, upgrade):
    """Aplikuje vybraný upgrade na hráče."""
    if upgrade["type"] == "weapon_new":
        player.weapons[upgrade["id"]] = 1
        player.weapon_timers[upgrade["id"]] = 0
    elif upgrade["type"] == "weapon_upgrade":
        player.weapons[upgrade["id"]] = upgrade["next_level"]
    elif upgrade["type"] == "tome":
        tid = upgrade["id"]
        tdef = TOME_DEFS[tid]
        player.tomes[tid] = upgrade["next_level"]
        if tdef["stat"] == "max_health":
            player.max_health += tdef["per_level"]
            player.health += tdef["per_level"]
        elif tdef["stat"] == "damage_mult":
            player.damage_mult += tdef["per_level"]
        elif tdef["stat"] == "speed":
            global PLAYER_SPEED
            PLAYER_SPEED += tdef["per_level"]
        elif tdef["stat"] == "cooldown_mult":
            player.cooldown_mult = max(0.3, player.cooldown_mult - tdef["per_level"])
        elif tdef["stat"] == "luck":
            player.luck += tdef["per_level"]

def draw_upgrade_icon(surface, upgrade_id, cx, cy, size=1.0):
    """Vykreslí ikonu zbraně/tomu na kartě."""
    s = size
    if upgrade_id == "sword":
        pygame.draw.line(surface, (200, 200, 220), (int(cx - 10*s), int(cy + 14*s)), (int(cx + 10*s), int(cy - 14*s)), max(1, int(4*s)))
        pygame.draw.line(surface, (255, 255, 255), (int(cx - 9*s), int(cy + 13*s)), (int(cx + 9*s), int(cy - 13*s)), max(1, int(2*s)))
        pygame.draw.rect(surface, (218, 165, 32), (int(cx - 7*s), int(cy + 1*s), int(14*s), int(4*s)))
        pygame.draw.line(surface, (139, 69, 19), (cx, int(cy + 5*s)), (cx, int(cy + 14*s)), max(1, int(3*s)))
    elif upgrade_id == "shuriken":
        points = []
        for i in range(8):
            a = math.radians(i * 45 - 22.5)
            r = 14*s if i % 2 == 0 else 7*s
            points.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        pygame.draw.polygon(surface, (180, 180, 200), points)
        pygame.draw.circle(surface, (120, 120, 140), (cx, cy), max(1, int(3*s)))
    elif upgrade_id == "fire_ring":
        for i in range(8):
            a = math.radians(i * 45)
            px = cx + int(math.cos(a) * 14*s)
            py = cy + int(math.sin(a) * 14*s)
            c_val = 100 + (i * 20) % 100
            pygame.draw.circle(surface, (255, c_val, 0), (px, py), max(1, int(4*s)))
        pygame.draw.circle(surface, (255, 200, 50), (cx, cy), max(1, int(6*s)))
    elif upgrade_id == "lightning":
        pts = [
            (int(cx - 4*s), int(cy - 14*s)),
            (int(cx + 3*s), int(cy - 4*s)),
            (int(cx - 2*s), int(cy - 1*s)),
            (int(cx + 7*s), int(cy + 14*s)),
            (int(cx + 1*s), int(cy + 3*s)),
            (int(cx + 5*s), int(cy + 5*s)),
        ]
        pygame.draw.lines(surface, (100, 180, 255), False, pts, max(1, int(3*s)))
        pygame.draw.lines(surface, (220, 240, 255), False, pts, max(1, int(1*s)))
    elif upgrade_id == "vitality":
        pygame.draw.rect(surface, (255, 50, 50), (int(cx - 9*s), int(cy - 3*s), int(18*s), int(6*s)))
        pygame.draw.rect(surface, (255, 50, 50), (int(cx - 3*s), int(cy - 9*s), int(6*s), int(18*s)))
    elif upgrade_id == "power":
        pygame.draw.polygon(surface, (255, 165, 0), [(cx, int(cy - 13*s)), (int(cx + 11*s), int(cy + 9*s)), (int(cx - 11*s), int(cy + 9*s))])
        pygame.draw.polygon(surface, (255, 210, 80), [(cx, int(cy - 8*s)), (int(cx + 7*s), int(cy + 6*s)), (int(cx - 7*s), int(cy + 6*s))])
    elif upgrade_id == "speed":
        for i in range(3):
            pygame.draw.line(surface, (0, 200, 255), (int(cx - 10*s + i*5*s), int(cy + 8*s)), (int(cx + 6*s + i*5*s), int(cy - 8*s)), max(1, int(2*s)))
    elif upgrade_id == "haste":
        pygame.draw.circle(surface, (255, 255, 100), (cx, cy), max(1, int(11*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (255, 255, 100), (cx, cy), (int(cx + 7*s), int(cy - 9*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (255, 255, 100), (cx, cy), (int(cx + 9*s), int(cy + 2*s)), max(1, int(2*s)))
    elif upgrade_id == "luck":
        for a in [0, 90, 180, 270]:
            lx = cx + int(math.cos(math.radians(a)) * 7*s)
            ly = cy + int(math.sin(math.radians(a)) * 7*s)
            pygame.draw.circle(surface, (0, 255, 100), (lx, ly), max(1, int(5*s)))
        pygame.draw.line(surface, (0, 180, 50), (cx, int(cy + 5*s)), (cx, int(cy + 15*s)), max(1, int(2*s)))


# =============================================
# Projektilové třídy pro zbraně
# =============================================

class ShurikenProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage):
        super().__init__()
        self.damage = damage
        self.speed = speed
        self.angle_rad = math.radians(angle)
        self.fx = float(x)
        self.fy = float(y)
        self.vx = math.cos(self.angle_rad) * speed
        self.vy = math.sin(self.angle_rad) * speed
        self.lifetime = 180
        self.hit_enemies = set()
        self.rotation = 0

        # Draw shuriken star
        self.base_image = pygame.Surface((14, 14), pygame.SRCALPHA)
        cx, cy = 7, 7
        points = []
        for i in range(8):
            a = math.radians(i * 45 - 22.5)
            r = 6 if i % 2 == 0 else 3
            points.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        pygame.draw.polygon(self.base_image, (180, 190, 210), points)
        pygame.draw.polygon(self.base_image, (140, 150, 170), points, 1)
        pygame.draw.circle(self.base_image, (100, 110, 130), (cx, cy), 2)

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, **kwargs):
        self.fx += self.vx
        self.fy += self.vy
        self.rect.center = (int(self.fx), int(self.fy))
        self.lifetime -= 1
        self.rotation = (self.rotation + 15) % 360
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        if self.lifetime <= 0:
            self.kill()


# Kamera
class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.view_w = int(WINDOW_WIDTH / ZOOM)
        self.view_h = int(WINDOW_HEIGHT / ZOOM)

    def apply(self, entity):
        if hasattr(entity, 'rect'):
            return entity.rect.move(self.rect.x, self.rect.y)
        else:
            # pro útok (rect)
            return entity.move(self.rect.x, self.rect.y)

    def update(self, target):
        # Sleduje hráče přesně - bez mrtvé zóny
        target_x = -target.rect.centerx + self.view_w // 2
        target_y = -target.rect.centery + self.view_h // 2

        x = target_x
        y = target_y

        # horizontální posun kamery v rámci hranic světa
        if self.width > self.view_w:
            x = min(0, x)
            x = max(-(self.width - self.view_w), x)
        else:
            x = 0

        # vertikální posun kamery v rámci hranic světa
        if self.height > self.view_h:
            y = min(0, y)
            y = max(-(self.height - self.view_h), y)
        else:
            y = 0

        self.rect.x = x
        self.rect.y = y

# Třída pro blok s texturou
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type='dirt'):
        super().__init__()
        self.block_type = block_type
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.draw_texture()

    def draw_texture(self):
        # Vytvoření textury podle typu bloku
        if self.block_type == 'dirt':
            self.image.fill((120, 82, 45))
            for _ in range(8):
                dx = random.randint(0, BLOCK_SIZE-4)
                dy = random.randint(0, BLOCK_SIZE-4)
                pygame.draw.rect(self.image, (90, 50, 20), (dx, dy, 4, 3))
        elif self.block_type == 'stone':
            self.image.fill((100, 100, 105))
            pygame.draw.rect(self.image, (140, 140, 145), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 2)
            pygame.draw.polygon(self.image, (70, 70, 75), [(0, BLOCK_SIZE), (BLOCK_SIZE, BLOCK_SIZE), (BLOCK_SIZE, 0)])
            pygame.draw.rect(self.image, (100, 100, 105), (2, 2, BLOCK_SIZE-4, BLOCK_SIZE-4))
            for _ in range(3):
                dx = random.randint(4, BLOCK_SIZE-6)
                dy = random.randint(4, BLOCK_SIZE-6)
                pygame.draw.rect(self.image, (80, 80, 85), (dx, dy, 4, 4))
        elif self.block_type == 'grass':
            self.image.fill((120, 82, 45))
            pygame.draw.rect(self.image, (34, 139, 34), (0, 0, BLOCK_SIZE, 12))
            pygame.draw.rect(self.image, (0, 100, 0), (0, 10, BLOCK_SIZE, 3))
            for i in range(5):
                x = i * 6 + 2
                h = random.randint(3, 6)
                pygame.draw.line(self.image, (50, 200, 50), (x, 10), (x+random.randint(-1, 1), 10-h), 2)
        elif self.block_type == 'wood':
            self.image.fill((139, 69, 19))
            pygame.draw.rect(self.image, (101, 33, 0), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 2)
            for i in range(4):
                y = i * 8 + 4
                pygame.draw.line(self.image, (101, 33, 0), (0, y), (BLOCK_SIZE, y), 2)
        else:  # default
            self.image.fill(WHITE)
            
        # Subtle border for all blocks
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 1)

# Třída pro předmět
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type='health', xp_value=0):
        super().__init__()
        self.item_type = item_type
        self.xp_value = xp_value
        self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x + BLOCK_SIZE//2, y + BLOCK_SIZE//2))
        self.draw_item()

    def draw_item(self):
        self.image.fill((0, 0, 0, 0))  # průhledné pozadí
        # Glowing shadow
        pygame.draw.circle(self.image, (255, 255, 255, 50), (12, 12), 10)

        if self.item_type == 'health':
            pygame.draw.rect(self.image, (150, 0, 0), (6, 10, 12, 4))
            pygame.draw.rect(self.image, (150, 0, 0), (10, 6, 4, 12))
            pygame.draw.rect(self.image, (255, 50, 50), (7, 11, 10, 2))
            pygame.draw.rect(self.image, (255, 50, 50), (11, 7, 2, 10))
        elif self.item_type == 'damage_boost':
            # žlutý meč
            pygame.draw.polygon(self.image, (200, 100, 0), [(12, 3), (22, 13), (18, 17), (8, 7)])
            pygame.draw.polygon(self.image, (255, 215, 0), [(13, 4), (20, 11), (17, 14), (10, 7)])
            pygame.draw.rect(self.image, (139, 69, 19), (6, 15, 6, 6))
        elif self.item_type == 'key':
            # klíč
            pygame.draw.circle(self.image, (255, 215, 0), (8, 12), 5, 2)
            pygame.draw.rect(self.image, (255, 215, 0), (13, 11, 8, 2))
            pygame.draw.rect(self.image, (255, 215, 0), (17, 13, 2, 3))
            pygame.draw.rect(self.image, (255, 215, 0), (20, 13, 2, 2))
        elif self.item_type == 'xp':
            # XP orb = green glowing circle
            pygame.draw.circle(self.image, (0, 255, 100), (12, 12), 6)
            pygame.draw.circle(self.image, (200, 255, 200), (12, 12), 3)
        elif self.item_type == 'money':
            # Zlatá mince
            pygame.draw.circle(self.image, (255, 215, 0), (12, 12), 6)
            pygame.draw.circle(self.image, (218, 165, 32), (12, 12), 6, 2)
            pygame.draw.rect(self.image, (218, 165, 32), (11, 8, 2, 8))

    def apply(self, player):
        if self.item_type == 'health':
            player.heal(HEAL_AMOUNT)
        elif self.item_type == 'damage_boost':
            player.damage_boost = DAMAGE_BOOST
            player.damage_boost_timer = DAMAGE_BOOST_DURATION
        elif self.item_type == 'key':
            player.keys += 1
        elif self.item_type == 'xp':
            player.add_xp(self.xp_value)
        elif self.item_type == 'money':
            player.money += self.xp_value
        self.kill()

    def update(self, player=None):
        if player and self.item_type in ['xp', 'money']:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if 0 < dist < 150:
                speed = 4.0
                self.rect.x += int((dx / dist) * speed)
                self.rect.y += int((dy / dist) * speed)

# =============================================
# Character Definitions
# =============================================
CHARACTER_DEFS = {
    "knight": {
        "name": "Knight",
        "desc": "Balanced warrior with sturdy armor",
        "skin": (255, 224, 189),
        "skin_shadow": (230, 190, 150),
        "hair": (80, 40, 0),
        "hair_highlight": (100, 50, 0),
        "shirt": (30, 90, 200),
        "shirt_dark": (20, 70, 160),
        "shirt_light": (50, 120, 255),
        "pants": (20, 20, 80),
        "boots": (50, 50, 50),
        "belt": (90, 45, 0),
        "buckle": (255, 215, 0),
        "buckle_dark": (200, 150, 0),
        "eye_white": (255, 255, 255),
        "eye_pupil": (20, 20, 30),
        "cape": None,
    },
    "mage": {
        "name": "Mage",
        "desc": "Mystical sorcerer with arcane power",
        "skin": (240, 215, 195),
        "skin_shadow": (210, 180, 160),
        "hair": (200, 200, 220),
        "hair_highlight": (230, 230, 245),
        "shirt": (90, 40, 160),
        "shirt_dark": (65, 25, 120),
        "shirt_light": (120, 60, 200),
        "pants": (60, 30, 100),
        "boots": (40, 20, 60),
        "belt": (70, 50, 90),
        "buckle": (180, 100, 255),
        "buckle_dark": (140, 70, 200),
        "eye_white": (255, 255, 255),
        "eye_pupil": (100, 50, 180),
        "cape": (100, 50, 180),
    },
    "rogue": {
        "name": "Rogue",
        "desc": "Swift and deadly shadow striker",
        "skin": (220, 195, 165),
        "skin_shadow": (190, 160, 130),
        "hair": (25, 25, 30),
        "hair_highlight": (45, 45, 55),
        "shirt": (40, 50, 40),
        "shirt_dark": (25, 35, 25),
        "shirt_light": (55, 70, 55),
        "pants": (30, 30, 30),
        "boots": (35, 30, 25),
        "belt": (50, 40, 30),
        "buckle": (150, 150, 150),
        "buckle_dark": (100, 100, 100),
        "eye_white": (255, 255, 255),
        "eye_pupil": (30, 60, 30),
        "cape": None,
    },
    "berserker": {
        "name": "Berserker",
        "desc": "Savage fighter fueled by rage",
        "skin": (210, 170, 135),
        "skin_shadow": (180, 140, 105),
        "hair": (180, 50, 20),
        "hair_highlight": (210, 80, 40),
        "shirt": (160, 50, 30),
        "shirt_dark": (120, 35, 20),
        "shirt_light": (200, 70, 40),
        "pants": (80, 50, 30),
        "boots": (60, 40, 25),
        "belt": (100, 60, 30),
        "buckle": (200, 180, 50),
        "buckle_dark": (160, 140, 30),
        "eye_white": (255, 255, 255),
        "eye_pupil": (150, 30, 10),
        "cape": None,
    },
}

def draw_character_sprite(surf, character_id, char_config, is_walking=False, step=0):
    """Standalone funkce pro vykreslení postavy podle char_config barev."""
    c = char_config
    surf.fill((0, 0, 0, 0))

    # Stín
    shadow_w = 20 if not is_walking else 22
    shadow_x = 4 if not is_walking else 3
    pygame.draw.ellipse(surf, (0, 0, 0, 80), (shadow_x, 23, shadow_w, 5))

    # Nohy
    leg_y = 19
    leg1_y = leg_y - (2 if is_walking and step in [0, 1] else 0)
    leg2_y = leg_y - (2 if is_walking and step in [2, 3] else 0)
    pygame.draw.rect(surf, c["pants"], (8, leg1_y, 4, 7))
    pygame.draw.rect(surf, c["boots"], (7, leg1_y + 5, 6, 3), border_radius=1)
    pygame.draw.rect(surf, c["pants"], (16, leg2_y, 4, 7))
    pygame.draw.rect(surf, c["boots"], (15, leg2_y + 5, 6, 3), border_radius=1)

    # Plášť (za tělem, pokud postava má)
    if c.get("cape"):
        sway = 1 if is_walking and step in [1, 3] else 0
        pygame.draw.polygon(surf, c["cape"],
                            [(6, 12), (22, 12), (23 + sway, 22), (5 - sway, 22)])
        darker = tuple(max(0, v - 30) for v in c["cape"])
        pygame.draw.polygon(surf, darker,
                            [(8, 16), (20, 16), (21 + sway, 22), (7 - sway, 22)])

    # Zadní ruka
    arm1_y = 12 - (1 if is_walking and step in [2, 3] else 0)
    pygame.draw.rect(surf, c["shirt_dark"], (4, arm1_y, 4, 7), border_radius=2)
    pygame.draw.rect(surf, c["skin"], (4, arm1_y + 5, 4, 3), border_radius=1)

    # Tělo
    pygame.draw.rect(surf, c["shirt"], (6, 10, 16, 10), border_radius=3)
    pygame.draw.rect(surf, c["shirt_dark"], (6, 15, 16, 5),
                     border_bottom_left_radius=3, border_bottom_right_radius=3)
    pygame.draw.rect(surf, c["shirt_light"], (7, 10, 14, 3),
                     border_top_left_radius=3, border_top_right_radius=3)

    # Opasek
    pygame.draw.rect(surf, c["belt"], (6, 17, 16, 3))
    pygame.draw.rect(surf, c["buckle"], (12, 16, 4, 5), border_radius=1)
    pygame.draw.rect(surf, c["buckle_dark"], (13, 17, 2, 3))

    # Hlava
    pygame.draw.rect(surf, c["skin"], (7, 2, 14, 11), border_radius=4)
    pygame.draw.rect(surf, c["skin_shadow"], (7, 9, 14, 4),
                     border_bottom_left_radius=4, border_bottom_right_radius=4)

    # Vlasy (základ)
    pygame.draw.rect(surf, c["hair"], (6, 0, 16, 4),
                     border_top_left_radius=5, border_top_right_radius=5)
    pygame.draw.rect(surf, c["hair"], (6, 3, 3, 5))
    pygame.draw.rect(surf, c["hair"], (19, 3, 3, 4))
    pygame.draw.rect(surf, c["hair_highlight"], (8, 0, 12, 2), border_radius=1)

    # Unikátní detaily podle postavy
    if character_id == "knight":
        # Helmice – kovový pásek přes čelo
        pygame.draw.rect(surf, (160, 160, 170), (7, 0, 14, 2),
                         border_top_left_radius=3, border_top_right_radius=3)
        pygame.draw.rect(surf, (120, 120, 130), (9, 2, 10, 1))
    elif character_id == "mage":
        # Špičatý klobouk
        pygame.draw.polygon(surf, c["shirt"], [(14, -4), (6, 4), (22, 4)])
        pygame.draw.polygon(surf, c["shirt_light"], [(14, -3), (8, 3), (14, 3)])
        pygame.draw.circle(surf, (255, 255, 150), (14, -1), 2)
    elif character_id == "rogue":
        # Kapuce a maska
        pygame.draw.rect(surf, (20, 25, 20), (6, 0, 16, 3),
                         border_top_left_radius=5, border_top_right_radius=5)
        pygame.draw.rect(surf, (30, 35, 30), (7, 9, 14, 4), border_radius=2)
    elif character_id == "berserker":
        # Válečný make-up
        pygame.draw.line(surf, (180, 30, 10), (8, 5), (8, 10), 2)
        pygame.draw.line(surf, (180, 30, 10), (19, 5), (19, 10), 2)
        # Trčící vlasy
        pygame.draw.polygon(surf, c["hair"], [(7, 0), (9, -3), (11, 0)])
        pygame.draw.polygon(surf, c["hair"], [(12, 0), (14, -4), (16, 0)])
        pygame.draw.polygon(surf, c["hair"], [(17, 0), (19, -3), (21, 0)])

    # Oči
    pygame.draw.rect(surf, c["eye_white"], (9, 6, 4, 4), border_radius=1)
    pygame.draw.rect(surf, c["eye_white"], (15, 6, 4, 4), border_radius=1)
    pygame.draw.rect(surf, c["eye_pupil"], (10, 7, 2, 2))
    pygame.draw.rect(surf, c["eye_pupil"], (16, 7, 2, 2))
    # Odlesk v oku
    pygame.draw.rect(surf, (255, 255, 255), (11, 6, 1, 1))
    pygame.draw.rect(surf, (255, 255, 255), (17, 6, 1, 1))

    # Ústa
    if character_id != "rogue":  # rogue má masku
        pygame.draw.line(surf, c["skin_shadow"], (11, 11), (16, 11), 1)

    # Přední ruka
    arm2_y = 12 - (1 if is_walking and step in [0, 1] else 0)
    pygame.draw.rect(surf, c["shirt_light"], (20, arm2_y, 4, 7), border_radius=2)
    pygame.draw.rect(surf, c["skin"], (20, arm2_y + 5, 4, 3), border_radius=1)


# Třída pro hráče (s animacemi)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character_id="knight"):
        super().__init__()
        self.character_id = character_id
        self.char_config = CHARACTER_DEFS.get(character_id, CHARACTER_DEFS["knight"])
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = 0
        self.vel_y = 0
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_damage = ATTACK_DAMAGE
        self.money = 0
        self.attack_hitbox = pygame.Rect(0, 0, ATTACK_SIZE, ATTACK_SIZE)
        self.facing_right = True  # pro animaci a útok
        self.attack_angle = 0
        self.damage_boost = 1
        self.damage_boost_timer = 0
        self.keys = 0
        self.hit_cooldown = 0
        self.knockback_timer = 0
        self.xp = 0
        self.level = 1
        self.max_xp = 10
        self.hit_enemies = set()
        self.level_up_pending = 0

        # Health regen
        self.health_regen_timer = 0
        self.health_regen_rate = 120  # 120 snímků = 2 sekundy při 60 FPS
        self.health_regen_amount = 1

        # MegaBonk weapon/tome system
        self.weapons = {"sword": 1}  # weapon_id: level
        self.tomes = {}  # tome_id: level
        self.damage_mult = 1.0  # z Power Tome
        self.cooldown_mult = 1.0  # z Haste Tome (nižší = rychlejší)
        self.luck = 0  # z Luck Tome
        self.weapon_timers = {}  # cooldown timery pro každou zbraň
        self.fire_ring_active = 0
        self.fire_ring_radius = 0
        self.fire_ring_damage = 0
        self.fire_ring_max_duration = 1
        self.lightning_bolts = []
        self.lightning_timer = 0
        self.reroll_cost = REROLL_BASE_COST

        # Animace
        self.animation_frames = {
            'idle': self.create_idle_frames(),
            'walk': self.create_walk_frames(),
            'attack': self.create_attack_frames(),
            'death': self.create_death_frames()
        }
        self.current_animation = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animation_frames['idle'][0]

    def draw_player_base(self, surf, is_walking=False, step=0):
        draw_character_sprite(surf, self.character_id, self.char_config, is_walking, step)

    def create_idle_frames(self):
        frames = []
        for i in range(2):
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.draw_player_base(surf)
            if i == 1:
                surf.scroll(0, 1) # breathing
            frames.append(surf)
        return frames

    def create_walk_frames(self):
        frames = []
        for i in range(4):
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.draw_player_base(surf, is_walking=True, step=i)
            frames.append(surf)
        return frames

    def create_attack_frames(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_player_base(surf)
        # vylepšený meč
        pygame.draw.line(surf, (160, 160, 170), (16, 16), (27, 2), 4)
        pygame.draw.line(surf, (255, 255, 255), (16, 16), (26, 3), 2)
        pygame.draw.polygon(surf, (218, 165, 32), [(14, 13), (18, 17), (16, 19), (12, 15)]) # záštita
        pygame.draw.line(surf, (139, 69, 19), (15, 16), (11, 20), 3) # rukojeť
        pygame.draw.circle(surf, (255, 215, 0), (11, 20), 2) # hlavice
        return [surf]

    def create_death_frames(self):
        frames = []
        base_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_player_base(base_surf)
        for i in range(10):
            surf = base_surf.copy()
            # Překrytí očí
            pygame.draw.rect(surf, (0, 0, 0), (9, 6, 4, 4))
            pygame.draw.rect(surf, (0, 0, 0), (15, 6, 4, 4))
            # Křížky místo očí
            pygame.draw.line(surf, (255, 0, 0), (9, 6), (12, 9), 2)
            pygame.draw.line(surf, (255, 0, 0), (12, 6), (9, 9), 2)
            pygame.draw.line(surf, (255, 0, 0), (15, 6), (18, 9), 2)
            pygame.draw.line(surf, (255, 0, 0), (18, 6), (15, 9), 2)
            surf = pygame.transform.rotate(surf, -i * 10)
            surf.set_alpha(max(0, 255 - i * 20))
            frames.append(surf)
        return frames

    def get_sword_reach(self):
        """Vrátí efektivní dosah meče na základě úrovně zbraně."""
        level = self.weapons.get("sword", 0)
        if level == 0:
            return ATTACK_SIZE
        return ATTACK_SIZE * WEAPON_DEFS["sword"]["levels"][level]["size"]

    def get_sword_damage(self):
        """Vrátí celkový damage meče včetně multiplikátorů."""
        level = self.weapons.get("sword", 0)
        if level == 0:
            return 0
        base = WEAPON_DEFS["sword"]["levels"][level]["damage"]
        return base * self.damage_mult * self.damage_boost

    def handle_input(self, camera=None):
        keys = pygame.key.get_pressed()
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
            self.vel_x *= 0.85
            self.vel_y *= 0.85
        else:
            self.vel_x = 0
            self.vel_y = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -PLAYER_SPEED
                if not self.attacking:
                    self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = PLAYER_SPEED
                if not self.attacking:
                    self.facing_right = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.vel_y = -PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel_y = PLAYER_SPEED

            # Normalizace diagonálního pohybu, aby nešel rychleji
            if self.vel_x != 0 and self.vel_y != 0:
                inv = 1 / math.sqrt(2)
                self.vel_x *= inv
                self.vel_y *= inv

        # Neustále sleduj myš pro úhel útoku
        if camera:
            mx, my = pygame.mouse.get_pos()
            # Zapracování ZOOMu do projekce myši
            world_mx = (mx / ZOOM) - camera.rect.x
            world_my = (my / ZOOM) - camera.rect.y
            dx = world_mx - self.rect.centerx
            dy = world_my - self.rect.centery
            self.attack_angle = math.degrees(math.atan2(dy, dx))
            if not self.attacking:
                self.facing_right = dx >= 0

        # Útok (automatický) - sword weapon z MegaBonk systému
        sword_level = self.weapons.get("sword", 0)
        if sword_level > 0 and self.attack_cooldown <= 0:
            sword_stats = WEAPON_DEFS["sword"]["levels"][sword_level]
            effective_cooldown = max(5, int(sword_stats["cooldown"] * self.cooldown_mult))
            self.attacking = True
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = effective_cooldown
            self.hit_enemies.clear()

            if not camera:
                self.attack_angle = 0 if self.facing_right else 180

    def move(self, blocks):
        # X
        self.rect.x += self.vel_x
        self.collide(self.vel_x, 0, blocks)
        # Y
        self.rect.y += self.vel_y
        self.collide(0, self.vel_y, blocks)

    def collide(self, vel_x, vel_y, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if vel_x > 0:
                    self.rect.right = block.rect.left
                    self.vel_x = 0
                elif vel_x < 0:
                    self.rect.left = block.rect.right
                    self.vel_x = 0
                if vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                elif vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

    def update(self, blocks, camera=None):
        if self.is_dead():
            self.vel_x = 0
            self.vel_y = 0
            self.current_animation = 'death'
            frames = self.animation_frames[self.current_animation]
            if int(self.frame_index) < len(frames) - 1:
                self.frame_index += self.animation_speed
            self.image = frames[int(self.frame_index)]
            return

        self.handle_input(camera)
        # top-down -> žádná gravitace ve hráči
        self.move(blocks)

        # Aktualizace útoku a cooldownu
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        # Health regen
        if self.health < self.max_health and not self.is_dead():
            self.health_regen_timer += 1
            if self.health_regen_timer >= self.health_regen_rate:
                self.heal(self.health_regen_amount)
                self.health_regen_timer = 0
        else:
            self.health_regen_timer = 0

        # Damage boost timer
        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= 1
            if self.damage_boost_timer <= 0:
                self.damage_boost = 1

        # Fire ring timer
        if self.fire_ring_active > 0:
            self.fire_ring_active -= 1

        # Lightning visual timer
        if self.lightning_timer > 0:
            self.lightning_timer -= 1
            if self.lightning_timer <= 0:
                self.lightning_bolts = []

        # Animace
        if self.attacking:
            self.current_animation = 'attack'
        elif self.vel_x != 0 or self.vel_y != 0:
            self.current_animation = 'walk'
        else:
            self.current_animation = 'idle'

        frames = self.animation_frames[self.current_animation]
        self.frame_index = (self.frame_index + self.animation_speed) % len(frames)
        self.image = frames[int(self.frame_index)]

        # Otočení podle směru
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # Hraniční kontrola světa je v main()

    def point_in_swing(self, px, py):
        ox, oy = self.rect.center
        dx = px - ox
        dy = py - oy
        dist = math.hypot(dx, dy)
        reach = self.get_sword_reach()
        if dist > reach * 2:
            return False
        ang = math.degrees(math.atan2(dy, dx))
        diff = (ang - self.attack_angle + 180) % 360 - 180
        return abs(diff) <= 90

    def attack_hits(self, enemy):
        if not self.attacking:
            return False
        ox, oy = self.rect.center
        ex, ey = enemy.rect.center
        dist = math.hypot(ex - ox, ey - oy)
        reach = self.get_sword_reach()
        if dist > reach * 2:
            return False
        return self.point_in_swing(ex, ey)

    def draw_attack(self, screen, camera):
        if self.attacking:
            center = camera.apply(self).center
            reach = self.get_sword_reach()
            arc_radius = reach * 1.8
            blade_length = reach * 1.6

            # Surface pro celý efekt
            surf_size = int(arc_radius * 4)
            swoosh_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

            progress = 1.0 - (self.attack_timer / ATTACK_DURATION)
            # Easing – zrychlení na začátku, zpomalení na konci
            eased = 1.0 - (1.0 - progress) ** 2.5

            half_swing = 60  # polovina úhlu švihu (celkem 120°)
            current_angle = self.attack_angle - half_swing + (half_swing * 2) * eased

            scx = surf_size // 2
            scy = surf_size // 2

            # Barva podle boostu
            if getattr(self, 'damage_boost_timer', 0) > 0:
                trail_color = (255, 140, 40)    # oranžová
                blade_color = (255, 200, 100)
                glow_color = (255, 100, 20)
            else:
                trail_color = (120, 200, 255)    # ledově modrá
                blade_color = (200, 230, 255)
                glow_color = (80, 160, 255)

            # ==========================================
            # 1) SWOOSH TRAIL – vějířovitý trail za čepelí
            # ==========================================
            trail_segments = 18
            trail_start_angle = self.attack_angle - half_swing
            trail_extent = (half_swing * 2) * eased

            if trail_extent > 2:
                # Vnější oblouk (ostrá hrana)
                for layer in range(3):
                    pts_outer = []
                    pts_inner = []
                    # Každá vrstva je tenčí a světlejší
                    layer_radius = arc_radius - layer * 4
                    layer_thickness_max = (arc_radius * 0.35) * (1.0 - layer * 0.3)

                    for i in range(trail_segments + 1):
                        t = i / trail_segments
                        a_deg = trail_start_angle + t * trail_extent
                        a_rad = math.radians(a_deg)

                        # Tloušťka roste od nuly na začátku k maximu uprostřed a klesá
                        # ale přední hrana (kde je čepel) je silnější
                        shape = math.sin(t * math.pi) ** 0.6
                        fade = t  # trail se zesiluje směrem k čepeli
                        thickness = layer_thickness_max * shape * max(0.15, fade)

                        ox = scx + math.cos(a_rad) * layer_radius
                        oy = scy + math.sin(a_rad) * layer_radius
                        pts_outer.append((ox, oy))

                        ix = scx + math.cos(a_rad) * (layer_radius - thickness)
                        iy = scy + math.sin(a_rad) * (layer_radius - thickness)
                        pts_inner.append((ix, iy))

                    pts_inner.reverse()
                    poly = pts_outer + pts_inner

                    if len(poly) >= 3:
                        # Vnější vrstva = trail_color, vnitřní = bílá
                        if layer == 0:
                            a = max(0, int(130 * (1.0 - progress * 0.7)))
                            col = (*trail_color, a)
                        elif layer == 1:
                            a = max(0, int(180 * (1.0 - progress * 0.6)))
                            col = (*blade_color, a)
                        else:
                            a = max(0, int(220 * (1.0 - progress * 0.5)))
                            col = (255, 255, 255, a)
                        pygame.draw.polygon(swoosh_surf, col, poly)

            # ==========================================
            # 2) MEČI / BLADE – vykreslení samotného meče
            # ==========================================
            blade_angle_rad = math.radians(current_angle)

            # Pozice špičky a base meče
            tip_x = scx + math.cos(blade_angle_rad) * blade_length
            tip_y = scy + math.sin(blade_angle_rad) * blade_length
            guard_x = scx + math.cos(blade_angle_rad) * (blade_length * 0.3)
            guard_y = scy + math.sin(blade_angle_rad) * (blade_length * 0.3)
            pommel_x = scx + math.cos(blade_angle_rad) * (blade_length * 0.12)
            pommel_y = scy + math.sin(blade_angle_rad) * (blade_length * 0.12)

            # Kolmý vektor pro šířku čepele
            perp_x = -math.sin(blade_angle_rad)
            perp_y = math.cos(blade_angle_rad)

            blade_width = 4.0
            guard_width = 8.0

            # Čepel (lichoběžník – úzká u špičky, širší u záštity)
            blade_poly = [
                (tip_x + perp_x * 1, tip_y + perp_y * 1),
                (tip_x - perp_x * 1, tip_y - perp_y * 1),
                (guard_x - perp_x * blade_width, guard_y - perp_y * blade_width),
                (guard_x + perp_x * blade_width, guard_y + perp_y * blade_width),
            ]
            # Stín čepele (tmavší)
            pygame.draw.polygon(swoosh_surf, (140, 150, 170, 220), blade_poly)
            # Světlý lesk na čepeli
            highlight_poly = [
                (tip_x + perp_x * 0.5, tip_y + perp_y * 0.5),
                (tip_x - perp_x * 0.3, tip_y - perp_y * 0.3),
                (guard_x - perp_x * (blade_width * 0.4), guard_y - perp_y * (blade_width * 0.4)),
                (guard_x + perp_x * (blade_width * 0.6), guard_y + perp_y * (blade_width * 0.6)),
            ]
            pygame.draw.polygon(swoosh_surf, (220, 230, 245, 240), highlight_poly)

            # Záštita (guard) – krátká příčka
            guard_pts = [
                (guard_x + perp_x * guard_width, guard_y + perp_y * guard_width),
                (guard_x - perp_x * guard_width, guard_y - perp_y * guard_width),
                (guard_x - perp_x * guard_width - math.cos(blade_angle_rad) * 2,
                 guard_y - perp_y * guard_width - math.sin(blade_angle_rad) * 2),
                (guard_x + perp_x * guard_width - math.cos(blade_angle_rad) * 2,
                 guard_y + perp_y * guard_width - math.sin(blade_angle_rad) * 2),
            ]
            pygame.draw.polygon(swoosh_surf, (200, 170, 50, 230), guard_pts)

            # Rukojeť
            pygame.draw.line(swoosh_surf, (110, 70, 30, 220),
                             (int(guard_x), int(guard_y)),
                             (int(pommel_x), int(pommel_y)), 4)
            # Hlavice
            pygame.draw.circle(swoosh_surf, (200, 170, 50, 200),
                               (int(pommel_x), int(pommel_y)), 3)

            # ==========================================
            # 3) GLOW na špičce čepele
            # ==========================================
            glow_alpha = max(0, int(160 * (1.0 - progress)))
            glow_r = int(12 + 6 * math.sin(progress * math.pi))
            if glow_r > 2:
                glow_s = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_s, (*glow_color, glow_alpha // 2), (glow_r * 2, glow_r * 2), glow_r * 2)
                pygame.draw.circle(glow_s, (255, 255, 255, glow_alpha), (glow_r * 2, glow_r * 2), glow_r)
                swoosh_surf.blit(glow_s, (int(tip_x) - glow_r * 2, int(tip_y) - glow_r * 2))

            # ==========================================
            # 4) JISKRY / sparks vyletující ze špičky
            # ==========================================
            if progress < 0.85:
                num_sparks = 4
                for s in range(num_sparks):
                    spark_spread = random.uniform(-0.5, 0.5)
                    spark_dist = random.uniform(4, 16)
                    spark_a = blade_angle_rad + spark_spread
                    sx = tip_x + math.cos(spark_a) * spark_dist
                    sy = tip_y + math.sin(spark_a) * spark_dist
                    spark_alpha = random.randint(120, 220)
                    spark_size = random.randint(1, 3)
                    spark_col = (255, 255, random.randint(150, 255), spark_alpha)
                    pygame.draw.circle(swoosh_surf, spark_col, (int(sx), int(sy)), spark_size)

            # ==========================================
            # 5) IMPACT FLASH na konci švihu
            # ==========================================
            if progress > 0.8:
                impact_progress = (progress - 0.8) / 0.2
                impact_alpha = max(0, int(100 * (1.0 - impact_progress)))
                impact_r = int(20 + 30 * impact_progress)
                if impact_alpha > 0 and impact_r > 0:
                    imp_surf = pygame.Surface((impact_r * 2, impact_r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(imp_surf, (*trail_color, impact_alpha // 3),
                                       (impact_r, impact_r), impact_r)
                    pygame.draw.circle(imp_surf, (255, 255, 255, impact_alpha // 2),
                                       (impact_r, impact_r), impact_r // 2)
                    # Pozice impactu = konec švihu
                    end_angle_rad = math.radians(self.attack_angle + half_swing)
                    imp_x = scx + math.cos(end_angle_rad) * arc_radius * 0.7
                    imp_y = scy + math.sin(end_angle_rad) * arc_radius * 0.7
                    swoosh_surf.blit(imp_surf, (int(imp_x) - impact_r, int(imp_y) - impact_r))

            screen.blit(swoosh_surf, swoosh_surf.get_rect(center=center))

    def draw_fire_ring(self, screen, camera):
        """Vykreslí fire ring efekt kolem hráče."""
        if self.fire_ring_active > 0:
            center = camera.apply(self).center
            max_dur = max(1, self.fire_ring_max_duration)
            progress = 1.0 - (self.fire_ring_active / max_dur)
            expand = min(1.0, progress * 4)  # rychlé rozšíření
            fr_radius = int(self.fire_ring_radius * expand)
            alpha = int(180 * (self.fire_ring_active / max_dur))

            if fr_radius > 5:
                fr_size = fr_radius * 2 + 30
                fr_surf = pygame.Surface((fr_size, fr_size), pygame.SRCALPHA)
                cp = (fr_size // 2, fr_size // 2)

                # Vnější kruh
                pygame.draw.circle(fr_surf, (255, 80, 0, max(0, alpha // 2)), cp, fr_radius, 5)
                # Vnitřní záře
                pygame.draw.circle(fr_surf, (255, 180, 50, max(0, alpha)), cp, max(0, fr_radius - 4), 3)

                # Ohnivé částice kolem kruhu
                num_particles = 12
                for i in range(num_particles):
                    angle = math.radians(i * (360 / num_particles) + self.fire_ring_active * 7)
                    px = cp[0] + int(math.cos(angle) * fr_radius)
                    py = cp[1] + int(math.sin(angle) * fr_radius)
                    p_alpha = max(0, min(255, alpha + 30))
                    c_val = 120 + (i * 25) % 80
                    pygame.draw.circle(fr_surf, (255, c_val, 0, p_alpha), (px, py), 5)
                    # Menší jiskra
                    px2 = cp[0] + int(math.cos(angle + 0.3) * (fr_radius - 8))
                    py2 = cp[1] + int(math.sin(angle + 0.3) * (fr_radius - 8))
                    pygame.draw.circle(fr_surf, (255, 255, 100, max(0, p_alpha // 2)), (px2, py2), 2)

                screen.blit(fr_surf, (center[0] - fr_size // 2, center[1] - fr_size // 2))

    def draw_lightning(self, screen, camera):
        """Vykreslí blesky mezi hráčem a zasaženými nepřáteli."""
        if self.lightning_timer > 0 and self.lightning_bolts:
            alpha_factor = self.lightning_timer / 15.0
            for (sx, sy), (ex, ey) in self.lightning_bolts:
                # Převod na souřadnice kamery
                s_screen = (int(sx + camera.rect.x), int(sy + camera.rect.y))
                e_screen = (int(ex + camera.rect.x), int(ey + camera.rect.y))

                # Zubaté body blesku
                points = [s_screen]
                segments = 6
                for i in range(1, segments):
                    t = i / segments
                    mx = int(s_screen[0] + (e_screen[0] - s_screen[0]) * t + random.randint(-10, 10))
                    my = int(s_screen[1] + (e_screen[1] - s_screen[1]) * t + random.randint(-10, 10))
                    points.append((mx, my))
                points.append(e_screen)

                # Hlavní blesk
                width = max(1, int(3 * alpha_factor))
                pygame.draw.lines(screen, (100, 180, 255), False, points, width)
                # Bílý střed
                pygame.draw.lines(screen, (220, 240, 255), False, points, max(1, width - 1))

                # Záře kolem cíle
                glow_radius = int(12 * alpha_factor)
                if glow_radius > 2:
                    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    glow_alpha = int(100 * alpha_factor)
                    pygame.draw.circle(glow_surf, (100, 180, 255, glow_alpha), (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surf, (e_screen[0] - glow_radius, e_screen[1] - glow_radius))

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.max_xp:
            self.xp -= self.max_xp
            self.level += 1
            self.max_xp = int(self.max_xp * 1.5)
            self.level_up_pending += 1

    def is_dead(self):
        return self.health <= 0

# Základní třída pro nepřítele
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type='walker'):
        super().__init__()
        self.enemy_type = enemy_type
        self.width = ENEMY_SIZE * 2 if enemy_type == 'boss' else ENEMY_SIZE
        self.height = ENEMY_SIZE * 2 if enemy_type == 'boss' else ENEMY_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = 0
        self.vel_y = 0
        
        # Set different health based on enemy type
        if self.enemy_type == 'walker':
            self.health = 30
            self.xp_value = 5
            self.speed = ENEMY_SPEED
            self.damage = 15
        elif self.enemy_type == 'flying':
            self.health = 20
            self.xp_value = 5
            self.speed = FLYING_ENEMY_SPEED
            self.damage = 10
        elif self.enemy_type == 'tank':
            self.health = 100
            self.xp_value = 15
            self.speed = ENEMY_SPEED * 0.6
            self.damage = 30
        elif self.enemy_type == 'fast':
            self.health = 10
            self.xp_value = 5
            self.speed = ENEMY_SPEED * 1.5
            self.damage = 5
        elif self.enemy_type == 'boss':
            self.health = 500
            self.xp_value = 150
            self.speed = ENEMY_SPEED * 0.8
            self.damage = 40
        else:
            self.health = 30  # default fallback
            self.xp_value = 5
            self.speed = ENEMY_SPEED
            self.damage = 15
        
        self.facing_right = random.choice([True, False])
        self.hit_flash = 0
        self.knockback_timer = 0

        # Vytvoření vzhledu
        self.image = pygame.Surface((self.width, self.height))
        self.draw_enemy()

    def draw_enemy(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        # Shadow
        pygame.draw.ellipse(self.image, (0, 0, 0, 80), (4, 24, 20, 6))

        if self.enemy_type == 'walker':
            # Slime / Zombie
            pygame.draw.rect(self.image, (34, 139, 34), (4, 8, 20, 18), border_radius=6)
            pygame.draw.rect(self.image, (0, 100, 0), (4, 8, 20, 18), 2, border_radius=6)
            pygame.draw.circle(self.image, (255, 0, 0), (10, 14), 3)
            pygame.draw.circle(self.image, (255, 0, 0), (18, 14), 3)
            pygame.draw.rect(self.image, (0, 0, 0), (10, 20, 8, 2))
        elif self.enemy_type == 'flying':
            # Bat
            pygame.draw.circle(self.image, (75, 0, 130), (14, 14), 8)
            pygame.draw.polygon(self.image, (138, 43, 226), [(6, 14), (-4, 4), (2, 20)])
            pygame.draw.polygon(self.image, (138, 43, 226), [(22, 14), (32, 4), (26, 20)])
            pygame.draw.circle(self.image, YELLOW, (11, 12), 2)
            pygame.draw.circle(self.image, YELLOW, (17, 12), 2)
        elif self.enemy_type == 'tank':
            # Golem
            pygame.draw.rect(self.image, (105, 105, 105), (2, 4, 24, 24), border_radius=4)
            pygame.draw.rect(self.image, (50, 50, 50), (2, 4, 24, 24), 3, border_radius=4)
            pygame.draw.circle(self.image, (255, 165, 0), (10, 10), 4)
            pygame.draw.circle(self.image, (255, 165, 0), (18, 10), 4)
            pygame.draw.rect(self.image, (0, 0, 0), (8, 18, 12, 4))
        elif self.enemy_type == 'fast':
            # Ghost/small eye
            pygame.draw.circle(self.image, (200, 200, 255, 180), (14, 14), 10)
            pygame.draw.circle(self.image, (255, 0, 0), (14, 14), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (14, 14), 2)
        elif self.enemy_type == 'boss':
            # Boss
            pygame.draw.rect(self.image, (150, 0, 0), (4, 4, self.width-8, self.height-8), border_radius=8)
            pygame.draw.rect(self.image, (50, 0, 0), (4, 4, self.width-8, self.height-8), 4, border_radius=8)
            pygame.draw.circle(self.image, (255, 255, 0), (self.width//3, self.height//3), 6)
            pygame.draw.circle(self.image, (255, 255, 0), (2*self.width//3, self.height//3), 6)
            pygame.draw.rect(self.image, (0, 0, 0), (self.width//4, 2*self.height//3, self.width//2, 8))
            
        mask = pygame.mask.from_surface(self.image)
        self.flash_image = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))



    def move(self, blocks):
        # X
        self.rect.x += self.vel_x
        self.collide(self.vel_x, 0, blocks)
        # Y
        self.rect.y += self.vel_y
        self.collide(0, self.vel_y, blocks)

    def collide(self, vel_x, vel_y, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if vel_x > 0:
                    self.rect.right = block.rect.left
                    self.vel_x = -self.speed
                    self.facing_right = False
                elif vel_x < 0:
                    self.rect.left = block.rect.right
                    self.vel_x = self.speed
                    self.facing_right = True
                if vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = -self.speed
                elif vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = self.speed

    def update(self, blocks, player=None):
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
            self.vel_x *= 0.85
            self.vel_y *= 0.85
        elif self.enemy_type in ['walker', 'tank', 'fast', 'boss']:
            # Chodec: pravidelně chase hráče, s malou plynulou korekcí
            if player:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    self.vel_x = (dx / dist) * self.speed
                    self.vel_y = (dy / dist) * self.speed
                else:
                    self.vel_x, self.vel_y = 0, 0
            else:
                if self.facing_right:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
                self.vel_y = 0
        elif self.enemy_type == 'flying':
            # Létající: sleduje hráče (jednoduché přiblížení)
            if player:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    self.vel_x = (dx / dist) * self.speed
                    self.vel_y = (dy / dist) * self.speed
                else:
                    self.vel_x = 0
                    self.vel_y = 0


        self.move(blocks)



    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 6

    def apply_knockback(self, source_rect):
        dx = self.rect.centerx - source_rect.centerx
        dy = self.rect.centery - source_rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            kb_strength = 12.0
            if self.enemy_type == 'tank':
                kb_strength = 4.0
            elif self.enemy_type == 'fast':
                kb_strength = 16.0
            elif self.enemy_type == 'boss':
                kb_strength = 1.0
            self.vel_x = (dx / dist) * kb_strength
            self.vel_y = (dy / dist) * kb_strength
            self.knockback_timer = 15

    def is_dead(self):
        return self.health <= 0

# Generátor dungeonu (místnosti a chodby)
def generate_dungeon(size):
    # Vytvoříme mřížku místností (každá místnost je slovník s x,y,w,h a dveřmi)
    rooms: List[RoomDict] = []
    for i in range(size):
        for j in range(size):
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = i * (ROOM_MAX_SIZE + 2) * BLOCK_SIZE  # rozestup mezi místnostmi
            y = j * (ROOM_MAX_SIZE + 2) * BLOCK_SIZE
            rooms.append({
                'x': x, 'y': y,
                'width': w * BLOCK_SIZE,
                'height': h * BLOCK_SIZE,
                'grid_x': i, 'grid_y': j,
                'doors': []  # seznam dveří (x,y) ve světových souřadnicích
            })

    # Propojení místností chodbami (jednoduché: každá místnost s pravým a dolním sousedem)

    for room in rooms:
        # Pravý soused
        right_room = next((r for r in rooms if r['grid_x'] == room['grid_x']+1 and r['grid_y'] == room['grid_y']), None)
        if right_room:
            door_y = room['y'] + ((room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE
            door1 = (room['x'] + room['width'] - BLOCK_SIZE, door_y)
            door2 = (right_room['x'], right_room['y'] + ((right_room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE)
            room['doors'].append(door1)
            right_room['doors'].append(door2)


        # Dolní soused
        down_room = next((r for r in rooms if r['grid_x'] == room['grid_x'] and r['grid_y'] == room['grid_y']+1), None)
        if down_room:
            door_x = room['x'] + ((room['width'] // 2) // BLOCK_SIZE) * BLOCK_SIZE
            door1 = (door_x, room['y'] + room['height'] - BLOCK_SIZE)
            door2 = (door_x, down_room['y'])
            room['doors'].append(door1)
            down_room['doors'].append(door2)


    # Místnost už nerenderujeme jako složitý dungeon; děláme otevřený travnatý svět s border stěnami.
    blocks = pygame.sprite.Group()
    placed = set()

    min_x = min(room['x'] for room in rooms)
    min_y = min(room['y'] for room in rooms)
    max_x = max(room['x'] + room['width'] for room in rooms)
    max_y = max(room['y'] + room['height'] for room in rooms)

    # Vodorovné stěny v horní a dolní hranici
    y_top = min_y - BLOCK_SIZE
    y_bottom = max_y + BLOCK_SIZE
    for bx in range(min_x - BLOCK_SIZE, max_x + 2*BLOCK_SIZE, BLOCK_SIZE):
        blocks.add(Block(bx, y_top, 'stone'))
        placed.add((bx, y_top))
        blocks.add(Block(bx, y_bottom, 'stone'))
        placed.add((bx, y_bottom))

    # Svislé stěny vlevo a vpravo
    x_left = min_x - BLOCK_SIZE
    x_right = max_x + BLOCK_SIZE
    for by in range(min_y - BLOCK_SIZE, max_y + 2*BLOCK_SIZE, BLOCK_SIZE):
        blocks.add(Block(x_left, by, 'stone'))
        placed.add((x_left, by))
        blocks.add(Block(x_right, by, 'stone'))
        placed.add((x_right, by))

    # Přidáme hranice světa (jednobloční zdi) tak, aby hráč nemohl vypadnout ven


    # Vodorovné hrany
    for bx in range(min_x - BLOCK_SIZE, max_x + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE):
        for by in [min_y - BLOCK_SIZE, max_y + BLOCK_SIZE]:
            if (bx, by) not in placed:
                blocks.add(Block(bx, by, 'stone'))
                placed.add((bx, by))

    # Svislé hrany
    for by in range(min_y - BLOCK_SIZE, max_y + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE):
        for bx in [min_x - BLOCK_SIZE, max_x + BLOCK_SIZE]:
            if (bx, by) not in placed:
                blocks.add(Block(bx, by, 'stone'))
                placed.add((bx, by))

    items = pygame.sprite.Group()

    return blocks, items, rooms

def spawn_at_screen_edge(camera, offset):
    """Vrátí náhodnou pozici za okrajem kamery."""
    cam_x = -camera.rect.x
    cam_y = -camera.rect.y
    cam_w = int(WINDOW_WIDTH / ZOOM)
    cam_h = int(WINDOW_HEIGHT / ZOOM)
    edge = random.randint(0, 3)
    if edge == 0:
        sx = random.randint(cam_x - offset, cam_x + cam_w + offset)
        sy = cam_y - offset
    elif edge == 1:
        sx = cam_x + cam_w + offset
        sy = random.randint(cam_y - offset, cam_y + cam_h + offset)
    elif edge == 2:
        sx = random.randint(cam_x - offset, cam_x + cam_w + offset)
        sy = cam_y + cam_h + offset
    else:
        sx = cam_x - offset
        sy = random.randint(cam_y - offset, cam_y + cam_h + offset)
    sx = max(BLOCK_SIZE, min(sx, WORLD_WIDTH_PX - BLOCK_SIZE))
    sy = max(BLOCK_SIZE, min(sy, WORLD_HEIGHT_PX - BLOCK_SIZE))
    return sx, sy

def show_death_screen(screen, score, wave, menu_font, info_font):
    options = ["Retry", "Main Menu"]
    selected = 0
    clock = pygame.time.Clock()
    btn_font = pygame.font.Font(None, 60)
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    while True:
        mx, my = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return options[selected].lower()

        title_surf = menu_font.render("YOU DIED", True, (255, 50, 50))
        title_shadow = menu_font.render("YOU DIED", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(4, 4))
        screen.blit(title_surf, title_rect)

        stats_surf = info_font.render(f"Score: {score}   |   Wave: {wave}", True, WHITE)
        stats_rect = stats_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4 + 70))
        screen.blit(stats_surf, stats_rect)

        button_width = 300
        button_height = 80
        for idx, option in enumerate(options):
            btn_rect = pygame.Rect(0, 0, button_width, button_height)
            btn_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 110)

            if btn_rect.collidepoint(mx, my):
                selected = idx
                if clicked:
                    return options[selected].lower()

            color_bg = (150, 50, 50) if idx == selected else (80, 30, 30)
            color_text = WHITE if idx == selected else (200, 200, 200)

            pygame.draw.rect(screen, color_bg, btn_rect, border_radius=15)
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)

            option_surf = btn_font.render(option, True, color_text)
            option_rect = option_surf.get_rect(center=btn_rect.center)
            screen.blit(option_surf, option_rect)

        pygame.display.flip()
        clock.tick(FPS)

# =============================================
# Vykreslení level-up obrazovky (MegaBonk style)
# =============================================

def draw_level_up_screen(screen, upgrades_offered, player, fonts):
    """Vykreslí MegaBonk-style level-up obrazovku s kartami zbraní/tomů."""
    font_lg, font_ui, font_sm, font_rar, font_desc = fonts

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    # Titulek
    title = font_lg.render('LEVEL UP!', True, (255, 215, 0))
    title_shadow = font_lg.render('LEVEL UP!', True, (80, 60, 0))
    screen.blit(title_shadow, (WINDOW_WIDTH // 2 - title.get_width() // 2 + 3, 53))
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))

    subtitle = font_ui.render('Choose an upgrade:', True, (200, 200, 200))
    screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 120))

    if not upgrades_offered:
        no_upg = font_sm.render("No upgrades available!", True, (200, 100, 100))
        screen.blit(no_upg, (WINDOW_WIDTH // 2 - no_upg.get_width() // 2, WINDOW_HEIGHT // 2))
        return

    card_count = len(upgrades_offered)
    card_w, card_h, spacing = 280, 400, 45
    total_w = card_count * card_w + (card_count - 1) * spacing
    start_x = (WINDOW_WIDTH - total_w) // 2
    start_y = (WINDOW_HEIGHT - card_h) // 2 + 15
    mx, my = pygame.mouse.get_pos()

    for idx, upgrade in enumerate(upgrades_offered):
        cx = start_x + idx * (card_w + spacing)
        rect = pygame.Rect(cx, start_y, card_w, card_h)
        hovered = rect.collidepoint(mx, my)

        base_col = RARITY_COLORS.get(upgrade["rarity"], WHITE)

        # Glow efekt při hoveru
        if hovered:
            glow_surf = pygame.Surface((card_w + 24, card_h + 24), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*base_col, 50), (0, 0, card_w + 24, card_h + 24), border_radius=16)
            screen.blit(glow_surf, (cx - 12, start_y - 12))
            # Druhá vrstva záře
            glow_surf2 = pygame.Surface((card_w + 12, card_h + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf2, (*base_col, 30), (0, 0, card_w + 12, card_h + 12), border_radius=14)
            screen.blit(glow_surf2, (cx - 6, start_y - 6))

        # Pozadí karty
        bg_r = min(255, base_col[0] // 5 + 25)
        bg_g = min(255, base_col[1] // 5 + 25)
        bg_b = min(255, base_col[2] // 5 + 25)
        if hovered:
            bg_r = min(255, bg_r + 15)
            bg_g = min(255, bg_g + 15)
            bg_b = min(255, bg_b + 15)
        bg_col = (bg_r, bg_g, bg_b)

        pygame.draw.rect(screen, bg_col, rect, border_radius=12)

        # Gradient efekt na kartě (horní polovina světlejší)
        grad_surf = pygame.Surface((card_w, card_h // 2), pygame.SRCALPHA)
        grad_surf.fill((*base_col, 15))
        screen.blit(grad_surf, (cx, start_y))

        # Okraj karty
        border_w = 3 if not hovered else 4
        pygame.draw.rect(screen, base_col, rect, border_w, border_radius=12)

        # Ikona - kruh nahoře
        icon_y = rect.top + 70
        icon_color = upgrade.get("icon_color", base_col)

        # Kruhy pozadí ikony
        pygame.draw.circle(screen, (0, 0, 0, 80), (rect.centerx + 2, icon_y + 2), 36)
        pygame.draw.circle(screen, (icon_color[0] // 3, icon_color[1] // 3, icon_color[2] // 3), (rect.centerx, icon_y), 36)
        pygame.draw.circle(screen, icon_color, (rect.centerx, icon_y), 30)
        pygame.draw.circle(screen, (255, 255, 255), (rect.centerx, icon_y), 30, 2)

        # Ikona uvnitř kruhu
        draw_upgrade_icon(screen, upgrade["id"], rect.centerx, icon_y)

        # Typ label (WEAPON / TOME)
        is_weapon = "weapon" in upgrade["type"]
        type_label = "WEAPON" if is_weapon else "TOME"
        type_col = (255, 200, 100) if is_weapon else (100, 255, 200)
        type_surf = font_desc.render(type_label, True, type_col)
        screen.blit(type_surf, (rect.centerx - type_surf.get_width() // 2, rect.top + 115))

        # Název
        name_surf = font_sm.render(upgrade['name'], True, WHITE)
        screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.top + 140))

        # Rarity
        rar_surf = font_rar.render(upgrade['rarity'], True, base_col)
        screen.blit(rar_surf, (rect.centerx - rar_surf.get_width() // 2, rect.top + 170))

        # Level info
        if upgrade['current_level'] == 0:
            level_text = "NEW!"
            level_col = (100, 255, 100)
        else:
            level_text = f"Lv.{upgrade['current_level']}  ->  Lv.{upgrade['next_level']}"
            level_col = (255, 255, 100)
        level_surf = font_rar.render(level_text, True, level_col)
        screen.blit(level_surf, (rect.centerx - level_surf.get_width() // 2, rect.top + 200))

        # Oddělovací čára
        pygame.draw.line(screen, base_col, (rect.left + 25, rect.top + 235), (rect.right - 25, rect.top + 235), 1)

        # Popis
        desc_surf = font_desc.render(upgrade['desc'], True, (210, 210, 210))
        screen.blit(desc_surf, (rect.centerx - desc_surf.get_width() // 2, rect.top + 255))

        # MAX level indikátor
        if upgrade.get("next_level", 0) >= MAX_WEAPON_LEVEL and is_weapon:
            max_surf = font_desc.render("* MAX LEVEL *", True, (255, 215, 0))
            screen.blit(max_surf, (rect.centerx - max_surf.get_width() // 2, rect.top + 290))

        # Weapon slot info
        if is_weapon:
            slots_used = len(player.weapons)
            if upgrade["type"] == "weapon_new":
                slot_text = f"Slots: {slots_used}/{MAX_WEAPON_SLOTS}"
            else:
                slot_text = f"Slots: {slots_used}/{MAX_WEAPON_SLOTS}"
            slot_surf = font_desc.render(slot_text, True, (150, 150, 150))
            screen.blit(slot_surf, (rect.centerx - slot_surf.get_width() // 2, rect.bottom - 40))

    # Reroll tlačítko
    reroll_cost = player.reroll_cost
    reroll_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, start_y + card_h + 25, 240, 50)
    reroll_hovered = reroll_rect.collidepoint(mx, my)
    can_reroll = player.money >= reroll_cost

    reroll_bg = (80, 65, 20) if can_reroll else (45, 45, 45)
    if reroll_hovered and can_reroll:
        reroll_bg = (120, 95, 30)
    pygame.draw.rect(screen, reroll_bg, reroll_rect, border_radius=10)

    reroll_border_col = (255, 215, 0) if can_reroll else (100, 100, 100)
    pygame.draw.rect(screen, reroll_border_col, reroll_rect, 2, border_radius=10)

    reroll_text_col = (255, 215, 0) if can_reroll else (100, 100, 100)
    reroll_text = font_rar.render(f"Reroll  ({reroll_cost} coins)  [R]", True, reroll_text_col)
    screen.blit(reroll_text, (reroll_rect.centerx - reroll_text.get_width() // 2, reroll_rect.centery - reroll_text.get_height() // 2))

    return start_x, start_y, card_w, card_h, spacing, reroll_rect


# Hlavní funkce hry
def main(character_id="knight"):
    global WORLD_WIDTH_PX, WORLD_HEIGHT_PX
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Cachované fonty (vytvořené jednou, ne každý snímek)
    font_ui = pygame.font.Font(None, 36)
    font_lg = pygame.font.Font(None, 74)
    font_sm = pygame.font.Font(None, 36)
    font_rar = pygame.font.Font(None, 28)
    font_desc = pygame.font.Font(None, 24)
    fonts = (font_lg, font_ui, font_sm, font_rar, font_desc)

    # Generování dungeonu
    blocks, items, rooms = generate_dungeon(DUNGEON_SIZE)
    # Velikost světa (maximální rozsah místností)
    max_x = max(room['x'] + room['width'] for room in rooms)
    max_y = max(room['y'] + room['height'] for room in rooms)
    WORLD_WIDTH_PX = max_x + BLOCK_SIZE
    WORLD_HEIGHT_PX = max_y + BLOCK_SIZE

    # Najdeme startovní místnost (první)
    start_room = rooms[0]
    start_x = start_room['x'] + start_room['width'] // 2
    start_y = start_room['y'] + start_room['height'] // 2
    player = Player(start_x, start_y, character_id)

    # Spawn nepřátel (startovní místnost bez nepřátel)
    enemies = pygame.sprite.Group()
    for room in rooms:
        if room == start_room:
            continue
        if random.random() < 0.7:  # 70% šance na nepřítele v ostatních místnostech
            ex = room['x'] + random.randint(2, (room['width']//BLOCK_SIZE)-3) * BLOCK_SIZE
            ey = room['y'] + random.randint(2, (room['height']//BLOCK_SIZE)-3) * BLOCK_SIZE
            enemy_type = random.choices(['walker', 'flying'], weights=[0.7, 0.3])[0]
            enemy = Enemy(ex, ey, enemy_type)
            enemies.add(enemy)

    # Projektily (shurikeny atd.)
    projectiles = pygame.sprite.Group()

    # Kamera
    camera = Camera(WORLD_WIDTH_PX, WORLD_HEIGHT_PX)

    # Neustálý spread nepřátel
    spawn_timer = 0
    current_spawn_interval = ENEMY_SPAWN_INTERVAL
    wave_number = 1
    wave_timer = 0
    total_spawns = 0

    # Herní smyčka
    running = True
    score: int = 0
    death_timer = 0
    is_level_up_screen = False
    upgrades_offered = []

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_level_up_screen and upgrades_offered:
                    mx, my = pygame.mouse.get_pos()
                    card_count = len(upgrades_offered)
                    card_w, card_h, spacing = 280, 400, 45
                    total_w = card_count * card_w + (card_count - 1) * spacing
                    lu_start_x = (WINDOW_WIDTH - total_w) // 2
                    lu_start_y = (WINDOW_HEIGHT - card_h) // 2 + 15

                    # Kontrola kliknutí na karty
                    for idx, upgrade in enumerate(upgrades_offered):
                        cx = lu_start_x + idx * (card_w + spacing)
                        rect = pygame.Rect(cx, lu_start_y, card_w, card_h)
                        if rect.collidepoint(mx, my):
                            apply_upgrade(player, upgrade)
                            player.level_up_pending -= 1
                            is_level_up_screen = False
                            break

                    # Kontrola reroll tlačítka
                    reroll_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, lu_start_y + card_h + 25, 240, 50)
                    if reroll_rect.collidepoint(mx, my):
                        if player.money >= player.reroll_cost:
                            player.money -= player.reroll_cost
                            player.reroll_cost += 2
                            upgrades_offered = generate_upgrade_offers(player)

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    else:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
                elif event.key == pygame.K_r and is_level_up_screen:
                    # Reroll klávesou R
                    if player.money >= player.reroll_cost:
                        player.money -= player.reroll_cost
                        player.reroll_cost += 2
                        upgrades_offered = generate_upgrade_offers(player)

        # Aktualizace
        if player.level_up_pending > 0 and not is_level_up_screen:
            is_level_up_screen = True
            player.reroll_cost = REROLL_BASE_COST  # Reset reroll cost při novém level-upu
            upgrades_offered = generate_upgrade_offers(player)

        if not is_level_up_screen:
            player.update(blocks, camera)
            enemies.update(blocks, player)
            items.update(player)
            projectiles.update()

            # =============================================
            # Weapon fire logic (MegaBonk styl)
            # =============================================
            for weapon_id, level in player.weapons.items():
                if weapon_id == "sword":
                    continue  # meč je řešen v handle_input

                if weapon_id not in player.weapon_timers:
                    player.weapon_timers[weapon_id] = 0

                player.weapon_timers[weapon_id] -= 1
                if player.weapon_timers[weapon_id] <= 0:
                    stats = WEAPON_DEFS[weapon_id]["levels"][level]
                    effective_cd = max(5, int(stats["cooldown"] * player.cooldown_mult))
                    player.weapon_timers[weapon_id] = effective_cd

                    if weapon_id == "shuriken":
                        count = stats["count"]
                        # Najdi nejbližšího nepřítele
                        nearest = None
                        min_dist = float('inf')
                        for e in enemies:
                            d = math.hypot(e.rect.centerx - player.rect.centerx,
                                           e.rect.centery - player.rect.centery)
                            if d < min_dist:
                                min_dist = d
                                nearest = e

                        for i in range(count):
                            if nearest and count <= 2:
                                base_angle = math.degrees(math.atan2(
                                    nearest.rect.centery - player.rect.centery,
                                    nearest.rect.centerx - player.rect.centerx))
                                angle = base_angle + (i - (count - 1) / 2) * 25
                            elif nearest:
                                base_angle = math.degrees(math.atan2(
                                    nearest.rect.centery - player.rect.centery,
                                    nearest.rect.centerx - player.rect.centerx))
                                angle = base_angle + (i - (count - 1) / 2) * (360 / count)
                            else:
                                angle = (360 / count) * i + random.uniform(-15, 15)

                            proj_damage = stats["damage"] * player.damage_mult
                            proj = ShurikenProjectile(
                                player.rect.centerx, player.rect.centery,
                                angle, stats["speed"], proj_damage)
                            projectiles.add(proj)

                    elif weapon_id == "fire_ring":
                        player.fire_ring_active = stats["duration"]
                        player.fire_ring_radius = stats["radius"]
                        player.fire_ring_damage = stats["damage"] * player.damage_mult
                        player.fire_ring_max_duration = stats["duration"]

                    elif weapon_id == "lightning":
                        targets_count = stats["targets"]
                        enemy_list = sorted(
                            enemies.sprites(),
                            key=lambda e: math.hypot(
                                e.rect.centerx - player.rect.centerx,
                                e.rect.centery - player.rect.centery))
                        player.lightning_bolts = []
                        lt_damage = stats["damage"] * player.damage_mult
                        for e in enemy_list[:targets_count]:
                            e.take_damage(lt_damage)
                            e.hit_flash = 8
                            if hasattr(e, 'apply_knockback'):
                                e.apply_knockback(player.rect)
                            player.lightning_bolts.append(
                                (player.rect.center, e.rect.center))
                            if e.is_dead():
                                items.add(Item(e.rect.x, e.rect.y, 'xp', xp_value=e.xp_value))
                                if random.random() < 0.3:
                                    items.add(Item(e.rect.x + random.randint(-10, 10),
                                                   e.rect.y + random.randint(-10, 10),
                                                   'money', xp_value=random.randint(1, 3)))
                                e.kill()
                                score += 10
                        player.lightning_timer = 15

            # Fire ring damage tick
            if player.fire_ring_active > 0 and player.fire_ring_active % 10 == 0:
                for e in list(enemies):
                    dist = math.hypot(e.rect.centerx - player.rect.centerx,
                                      e.rect.centery - player.rect.centery)
                    if dist < player.fire_ring_radius:
                        e.take_damage(player.fire_ring_damage)
                        e.hit_flash = 4
                        if e.is_dead():
                            items.add(Item(e.rect.x, e.rect.y, 'xp', xp_value=e.xp_value))
                            if random.random() < 0.3:
                                items.add(Item(e.rect.x + random.randint(-10, 10),
                                               e.rect.y + random.randint(-10, 10),
                                               'money', xp_value=random.randint(1, 3)))
                            e.kill()
                            score += 10

            # Shuriken kolize s nepřáteli
            for proj in list(projectiles):
                if isinstance(proj, ShurikenProjectile):
                    for e in list(enemies):
                        if e not in proj.hit_enemies and proj.rect.colliderect(e.rect):
                            proj.hit_enemies.add(e)
                            e.take_damage(proj.damage)
                            e.hit_flash = 6
                            if hasattr(e, 'apply_knockback'):
                                e.apply_knockback(proj.rect)
                            if e.is_dead():
                                items.add(Item(e.rect.x, e.rect.y, 'xp', xp_value=e.xp_value))
                                if random.random() < 0.3:
                                    items.add(Item(e.rect.x + random.randint(-10, 10),
                                                   e.rect.y + random.randint(-10, 10),
                                                   'money', xp_value=random.randint(1, 3)))
                                e.kill()
                                score += 10

            # Wave timer
            wave_timer += 1
            if wave_timer >= WAVE_DURATION:
                wave_timer = 0
                wave_number += 1
                current_spawn_interval = ENEMY_SPAWN_INTERVAL
                
                # Boss spawn na konci vlny
                bx, by = spawn_at_screen_edge(camera, ENEMY_SIZE * 3)
                boss = Enemy(bx, by, 'boss')
                boss.health += (wave_number - 2) * 200
                boss.damage += (wave_number - 2) * 10
                enemies.add(boss)

            # Spawn nepřátel v čase (wave style)
            spawn_timer += 1  # type: ignore
            if spawn_timer >= current_spawn_interval:
                spawn_timer = 0
                total_spawns += 1
                current_spawn_interval = max(15, int(current_spawn_interval * ENEMY_SPAWN_ACCELERATION))  # type: ignore

                spawn_count = int(min(ENEMY_MAX_PER_WAVE, ENEMY_WAVE_BASE + (total_spawns - 1) * ENEMY_WAVE_GROWTH))
                spawned = 0
                attempts = 0

                while spawned < spawn_count and attempts < spawn_count * 8:
                    if len(enemies) >= ENEMY_MAX_ON_MAP:
                        break
                    attempts += 1
                
                    sx, sy = spawn_at_screen_edge(camera, ENEMY_SIZE + 20)

                    if math.hypot(sx - player.rect.centerx, sy - player.rect.centery) < ENEMY_SPAWN_RADIUS_MIN:  # type: ignore
                        continue

                    enemy_types = ['walker', 'flying', 'tank', 'fast']
                    wave_type_index = (wave_number - 1) % len(enemy_types)
                    enemy_type = enemy_types[wave_type_index]
                    enemies.add(Enemy(sx, sy, enemy_type))  # type: ignore
                    spawned += 1  # type: ignore

            # Světové hranice: hráč a nepřátelé nesmí mimo
            if player.rect.left < 0:
                player.rect.left = 0
                player.vel_x = 0
            if player.rect.right > WORLD_WIDTH_PX:
                player.rect.right = WORLD_WIDTH_PX
                player.vel_x = 0
            if player.rect.top < 0:
                player.rect.top = 0
                player.vel_y = 0

            if player.rect.top > WORLD_HEIGHT_PX + 5*BLOCK_SIZE:
                # pokud spadne hráč hodně dolů mimo mapu, resetujeme pozici
                player.rect.x = start_x
                player.rect.y = start_y
                player.vel_x = 0
                player.vel_y = 0

            # Odstranění nepřátel mimo svět
            for spr in list(enemies):  # type: ignore
                if isinstance(spr, Enemy):
                    if (spr.rect.right < 0 or spr.rect.left > WORLD_WIDTH_PX or
                        spr.rect.top < 0 or spr.rect.bottom > WORLD_HEIGHT_PX + 5*BLOCK_SIZE):
                        spr.kill()

            # Kolize hráče s nepřáteli
            for spr in enemies:  # type: ignore
                if isinstance(spr, Enemy) and player.rect.colliderect(spr.rect):  # type: ignore
                    if player.hit_cooldown <= 0:
                        player.take_damage(spr.damage)
                        player.hit_cooldown = PLAYER_HIT_COOLDOWN
                        # odskok pouze při zranění a mírnější (1.5x speed a 7 snímků)
                        if player.rect.centerx < spr.rect.centerx:  # type: ignore
                            player.vel_x = -PLAYER_SPEED * 1.5
                        else:
                            player.vel_x = PLAYER_SPEED * 1.5
                        if player.rect.centery < spr.rect.centery:  # type: ignore
                            player.vel_y = -PLAYER_SPEED * 1.5
                        else:
                            player.vel_y = PLAYER_SPEED * 1.5
                        player.knockback_timer = 7

            # Kolize útoku (meč) s nepřáteli - používá sword weapon stats
            if player.attacking:
                sword_damage = player.get_sword_damage()
                for spr in list(enemies):  # type: ignore
                    if isinstance(spr, Enemy) and spr not in player.hit_enemies and player.attack_hits(spr):  # type: ignore
                        player.hit_enemies.add(spr)
                        spr.take_damage(sword_damage)
                        if hasattr(spr, 'apply_knockback'):
                            spr.apply_knockback(player.rect)
                        if spr.is_dead():
                            items.add(Item(spr.rect.x, spr.rect.y, 'xp', xp_value=spr.xp_value))
                            if random.random() < 0.3:
                                items.add(Item(spr.rect.x + random.randint(-10, 10), spr.rect.y + random.randint(-10, 10), 'money', xp_value=random.randint(1, 3)))
                            spr.kill()  # type: ignore
                            score += 10  # type: ignore

            # Kolize s předměty
            item_hits = pygame.sprite.spritecollide(player, items, True)
            for item in item_hits:
                item.apply(player)



            # Kamera
            camera.update(player)


        # Vytvoření menšího plátna pro renderování hry (pro zoom)
        cam_w = int(WINDOW_WIDTH / ZOOM)
        cam_h = int(WINDOW_HEIGHT / ZOOM)
        display_surface = pygame.Surface((cam_w, cam_h))
        
        # Kreslení travnatého pozadí
        display_surface.fill((34, 110, 34))
        bg_offset_x = camera.rect.x % 64
        bg_offset_y = camera.rect.y % 64
        for i in range(-64, cam_w + 64, 64):
            for j in range(-64, cam_h + 64, 64):
                pygame.draw.rect(display_surface, (30, 100, 30), (i + bg_offset_x, j + bg_offset_y, 32, 32))
                pygame.draw.rect(display_surface, (30, 100, 30), (i + 32 + bg_offset_x, j + 32 + bg_offset_y, 32, 32))

        # Obdélník pro culling (vykreslení jen na obrazovce)
        screen_rect = pygame.Rect(0, 0, cam_w, cam_h)

        # Kreslení bloků v kameře
        for block in blocks:
            screen_pos = camera.apply(block)
            if screen_rect.colliderect(screen_pos):
                display_surface.blit(block.image, screen_pos)

        # Kreslení předmětů
        for item in items:
            display_surface.blit(item.image, camera.apply(item))

        # Kreslení projektilů (shurikeny)
        for proj in projectiles:
            proj_pos = camera.apply(proj)
            if screen_rect.colliderect(proj_pos):
                display_surface.blit(proj.image, proj_pos)

        # Kreslení nepřátel
        for enemy in enemies:
            if getattr(enemy, 'hit_flash', 0) > 0 and hasattr(enemy, 'flash_image'):
                display_surface.blit(enemy.flash_image, camera.apply(enemy))
            else:
                display_surface.blit(enemy.image, camera.apply(enemy))

        # Kreslení hráče
        if player.hit_cooldown > 0 and (player.hit_cooldown // 4) % 2 == 0:
            mask = pygame.mask.from_surface(player.image)
            flash_image = mask.to_surface(setcolor=(255, 50, 50, 255), unsetcolor=(0, 0, 0, 0))
            display_surface.blit(flash_image, camera.apply(player))
        else:
            display_surface.blit(player.image, camera.apply(player))

        # Kreslení útoku (meč swoosh)
        player.draw_attack(display_surface, camera)

        # Kreslení fire ring efektu
        player.draw_fire_ring(display_surface, camera)

        # Kreslení lightning efektu
        player.draw_lightning(display_surface, camera)
        
        # Škálování kamery na celou obrazovku
        scaled_surf = pygame.transform.scale(display_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(scaled_surf, (0, 0))

        # UI

        wave_time_left = (WAVE_DURATION - wave_timer) // FPS
        minutes = wave_time_left // 60
        seconds = wave_time_left % 60
        wave_text = font_ui.render(f"Wave: {wave_number} ({minutes}:{seconds:02d})", True, ORANGE)
        screen.blit(wave_text, (WINDOW_WIDTH // 2 - wave_text.get_width() // 2, 10))
        level_text = font_ui.render(f"Level: {player.level} ({player.xp}/{player.max_xp} XP)", True, CYAN)
        screen.blit(level_text, (10, 10))
        health_text = font_ui.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
        screen.blit(health_text, (10, 50))
        score_text = font_ui.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 90))
        key_text = font_ui.render(f"Keys: {player.keys}", True, WHITE)
        screen.blit(key_text, (10, 130))
        money_text = font_ui.render(f"Coins: {player.money}", True, (255, 215, 0))
        screen.blit(money_text, (10, 170))

        # Sword damage display
        sword_dmg = int(player.get_sword_damage())
        damage_text = font_ui.render(f"Sword Dmg: {sword_dmg}", True, RED)
        screen.blit(damage_text, (10, 210))
        if player.damage_boost > 1:
            boost_text = font_ui.render(f"Damage Boost: {player.damage_boost_timer//60}s", True, YELLOW)
            screen.blit(boost_text, (10, 250))

        # Weapon slots display (pravý horní roh)
        wp_y = 10
        wp_x = WINDOW_WIDTH - 200
        wp_title = font_desc.render("Weapons:", True, (255, 200, 100))
        screen.blit(wp_title, (wp_x, wp_y))
        wp_y += 22
        for wid, wlevel in player.weapons.items():
            wname = WEAPON_DEFS[wid]["name"]
            wcol = WEAPON_DEFS[wid]["icon_color"]
            w_text = font_desc.render(f"{wname} Lv.{wlevel}", True, wcol)
            screen.blit(w_text, (wp_x, wp_y))
            wp_y += 20

        # Tome display
        if player.tomes:
            wp_y += 5
            tome_title = font_desc.render("Tomes:", True, (100, 255, 200))
            screen.blit(tome_title, (wp_x, wp_y))
            wp_y += 22
            for tid, tlevel in player.tomes.items():
                tname = TOME_DEFS[tid]["name"]
                tcol = TOME_DEFS[tid]["icon_color"]
                t_text = font_desc.render(f"{tname} x{tlevel}", True, tcol)
                screen.blit(t_text, (wp_x, wp_y))
                wp_y += 20

        # Level-up screen
        if is_level_up_screen:
            draw_level_up_screen(screen, upgrades_offered, player, fonts)

        pygame.display.flip()

        # Konec hry (smrt)
        if player.is_dead():
            death_timer += 1
            if death_timer > 90:  # ~1.5 sec do zobrazení death screenu
                menu_font = pygame.font.Font(None, 100)
                info_font = pygame.font.Font(None, 40)
                action = show_death_screen(screen, score, wave_number, menu_font, info_font)
                if action == "retry":
                    return "retry"
                else:
                    return "menu"
                    
    return "quit"

# =============================================
# Character Select Screen
# =============================================
def show_character_select(screen, current_character="knight"):
    """Zobrazí obrazovku výběru postavy s animovanými náhledy."""
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 80)
    name_font = pygame.font.Font(None, 48)
    desc_font = pygame.font.Font(None, 28)
    btn_font = pygame.font.Font(None, 50)

    char_ids = list(CHARACTER_DEFS.keys())
    selected = char_ids.index(current_character) if current_character in char_ids else 0

    # Předvykreslení náhledů postav (zvětšené 5×)
    scale = 5
    previews = {}
    walk_frames = {}
    for cid in char_ids:
        cdef = CHARACTER_DEFS[cid]
        # Idle frame
        surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        draw_character_sprite(surf, cid, cdef)
        previews[cid] = pygame.transform.scale(surf, (PLAYER_WIDTH * scale, PLAYER_HEIGHT * scale))
        # Walk frames
        frames = []
        for step in range(4):
            ws = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            draw_character_sprite(ws, cid, cdef, is_walking=True, step=step)
            frames.append(pygame.transform.scale(ws, (PLAYER_WIDTH * scale, PLAYER_HEIGHT * scale)))
        walk_frames[cid] = frames

    anim_timer = 0

    # Částice pozadí
    particles = []
    for _ in range(40):
        particles.append([
            random.randint(0, WINDOW_WIDTH),
            random.randint(0, WINDOW_HEIGHT),
            random.uniform(0.3, 1.5),
            random.randint(30, 80)
        ])

    while True:
        mx, my = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % len(char_ids)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % len(char_ids)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return char_ids[selected]
                elif event.key == pygame.K_ESCAPE:
                    return current_character

        anim_timer += 1
        anim_frame = (anim_timer // 10) % 4

        # Update particles
        for p in particles:
            p[1] -= p[2]
            if p[1] < -10:
                p[1] = WINDOW_HEIGHT + 10
                p[0] = random.randint(0, WINDOW_WIDTH)

        # Pozadí
        screen.fill((15, 15, 25))
        for p in particles:
            pygame.draw.circle(screen, (p[3], p[3], p[3] + 20),
                               (int(p[0]), int(p[1])), int(p[2] * 2))

        # Titulek
        title = title_font.render("SELECT CHARACTER", True, (255, 215, 0))
        title_shadow = title_font.render("SELECT CHARACTER", True, (80, 60, 0))
        screen.blit(title_shadow, (WINDOW_WIDTH // 2 - title.get_width() // 2 + 3, 53))
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))

        # Karty postav
        card_w, card_h = 280, 420
        spacing = 40
        total_w = len(char_ids) * card_w + (len(char_ids) - 1) * spacing
        start_x = (WINDOW_WIDTH - total_w) // 2
        start_y = (WINDOW_HEIGHT - card_h) // 2 + 20

        for idx, cid in enumerate(char_ids):
            cdef = CHARACTER_DEFS[cid]
            cx = start_x + idx * (card_w + spacing)
            rect = pygame.Rect(cx, start_y, card_w, card_h)
            is_selected = (idx == selected)
            hovered = rect.collidepoint(mx, my)

            if hovered and clicked:
                selected = idx

            # Glow efekt (vybraná)
            if is_selected:
                glow_surf = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
                glow_pulse = 30 + int(15 * math.sin(anim_timer * 0.05))
                pygame.draw.rect(glow_surf, (255, 215, 0, glow_pulse),
                                 (0, 0, card_w + 20, card_h + 20), border_radius=16)
                screen.blit(glow_surf, (cx - 10, start_y - 10))

            # Pozadí karty
            bg = (45, 42, 60) if is_selected else (35, 35, 55)
            if hovered and not is_selected:
                bg = (40, 40, 60)
            pygame.draw.rect(screen, bg, rect, border_radius=12)

            # Barevný gradient nahoře
            grad = pygame.Surface((card_w, card_h // 3), pygame.SRCALPHA)
            grad.fill((*cdef["shirt"], 20))
            screen.blit(grad, (cx, start_y))

            # Okraj
            border_col = (255, 215, 0) if is_selected else (80, 80, 100)
            border_w = 3 if is_selected else 2
            pygame.draw.rect(screen, border_col, rect, border_w, border_radius=12)

            # Náhled postavy
            preview_y = start_y + 55
            if is_selected:
                frame = walk_frames[cid][anim_frame]
            else:
                frame = previews[cid]
            preview_rect = frame.get_rect(center=(rect.centerx, preview_y + PLAYER_HEIGHT * scale // 2))
            screen.blit(frame, preview_rect)

            # Podstavec pod postavou
            plat_y = preview_y + PLAYER_HEIGHT * scale - 5
            plat_surf = pygame.Surface((70, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(plat_surf, (0, 0, 0, 60), (0, 0, 70, 12))
            screen.blit(plat_surf, (rect.centerx - 35, plat_y))

            # Jméno
            name_col = (255, 255, 255) if is_selected else (180, 180, 180)
            name_surf = name_font.render(cdef["name"], True, name_col)
            screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, start_y + card_h - 120))

            # Oddělovací čára
            sep_col = (255, 215, 0) if is_selected else (60, 60, 80)
            pygame.draw.line(screen, sep_col,
                             (cx + 30, start_y + card_h - 95),
                             (cx + card_w - 30, start_y + card_h - 95), 1)

            # Popis
            desc_surf = desc_font.render(cdef["desc"], True, (160, 160, 180))
            screen.blit(desc_surf, (rect.centerx - desc_surf.get_width() // 2, start_y + card_h - 75))

            # "SELECTED" badge
            if is_selected:
                sel_surf = desc_font.render("\u2714 SELECTED", True, (255, 215, 0))
                screen.blit(sel_surf, (rect.centerx - sel_surf.get_width() // 2, start_y + card_h - 40))

        # Tlačítko Confirm
        confirm_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, start_y + card_h + 40, 300, 60)
        confirm_hover = confirm_rect.collidepoint(mx, my)
        confirm_bg = (60, 140, 60) if confirm_hover else (40, 100, 40)
        pygame.draw.rect(screen, confirm_bg, confirm_rect, border_radius=12)
        pygame.draw.rect(screen, (100, 220, 100), confirm_rect, 2, border_radius=12)
        confirm_text = btn_font.render("Confirm", True, WHITE)
        screen.blit(confirm_text, (confirm_rect.centerx - confirm_text.get_width() // 2,
                                   confirm_rect.centery - confirm_text.get_height() // 2))
        if confirm_hover and clicked:
            return char_ids[selected]

        # Tlačítko Back
        back_rect = pygame.Rect(30, WINDOW_HEIGHT - 70, 120, 45)
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (70, 50, 50) if back_hover else (50, 35, 35)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 100, 100), back_rect, 2, border_radius=8)
        back_text = desc_font.render("< Back", True, (200, 200, 200))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2,
                                back_rect.centery - back_text.get_height() // 2))
        if back_hover and clicked:
            return current_character

        # Hints
        hint = desc_font.render("A/D to browse  |  Enter to confirm  |  Esc to go back",
                                True, (100, 100, 120))
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, WINDOW_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)


# Hlavní menu
def main_menu(selected_character="knight"):
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    menu_font = pygame.font.Font(None, 100)
    info_font = pygame.font.Font(None, 40)
    btn_font = pygame.font.Font(None, 60)
    char_font = pygame.font.Font(None, 28)
    options = ["Start Game", "Characters", "Quit"]
    selected = 0

    # Animace pro pozadí menu
    particles = []
    for _ in range(50):
        particles.append([random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT),
                          random.uniform(0.5, 2.0)])

    # Mini náhled aktuální postavy
    def make_preview(cid):
        cdef = CHARACTER_DEFS.get(cid, CHARACTER_DEFS["knight"])
        surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        draw_character_sprite(surf, cid, cdef)
        return pygame.transform.scale(surf, (PLAYER_WIDTH * 3, PLAYER_HEIGHT * 3))

    char_preview = make_preview(selected_character)

    while True:
        mx, my = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if options[selected] == "Start Game":
                        return ("start", selected_character)
                    elif options[selected] == "Characters":
                        selected_character = show_character_select(screen, selected_character)
                        char_preview = make_preview(selected_character)
                    else:
                        pygame.quit()
                        sys.exit()

        # Update částic
        for p in particles:
            p[1] -= p[2]
            if p[1] < -10:
                p[1] = WINDOW_HEIGHT + 10
                p[0] = random.randint(0, WINDOW_WIDTH)

        screen.fill((20, 30, 20))

        for p in particles:
            pygame.draw.circle(screen, (50, 80, 50), (int(p[0]), int(p[1])), int(p[2] * 2))

        # Titulek
        title_surf = menu_font.render(TITLE, True, (255, 215, 0))
        title_shadow = menu_font.render(TITLE, True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(4, 4))
        screen.blit(title_surf, title_rect)

        # Mini náhled aktuální postavy vedle titulku
        char_name = CHARACTER_DEFS.get(selected_character, CHARACTER_DEFS["knight"])["name"]
        preview_x = WINDOW_WIDTH // 2 + title_surf.get_width() // 2 + 30
        preview_y = WINDOW_HEIGHT // 4 - PLAYER_HEIGHT * 3 // 2
        screen.blit(char_preview, (preview_x, preview_y))
        char_label = char_font.render(char_name, True, (180, 200, 180))
        screen.blit(char_label, (preview_x + PLAYER_WIDTH * 3 // 2 - char_label.get_width() // 2,
                                 preview_y + PLAYER_HEIGHT * 3 + 5))

        # Kreslení tlačítek
        button_width = 300
        button_height = 80
        btn_start_y = WINDOW_HEIGHT // 2 - 40
        for idx, option in enumerate(options):
            btn_rect = pygame.Rect(0, 0, button_width, button_height)
            btn_rect.center = (WINDOW_WIDTH // 2, btn_start_y + idx * 100)

            if btn_rect.collidepoint(mx, my):
                selected = idx
                if clicked:
                    if options[selected] == "Start Game":
                        return ("start", selected_character)
                    elif options[selected] == "Characters":
                        selected_character = show_character_select(screen, selected_character)
                        char_preview = make_preview(selected_character)
                    else:
                        pygame.quit()
                        sys.exit()

            color_bg = (50, 150, 50) if idx == selected else (30, 80, 30)
            color_text = WHITE if idx == selected else (200, 200, 200)

            pygame.draw.rect(screen, color_bg, btn_rect, border_radius=15)
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)

            option_surf = btn_font.render(option, True, color_text)
            option_rect = option_surf.get_rect(center=btn_rect.center)
            screen.blit(option_surf, option_rect)

        info_surf = info_font.render("Use W/S/Mouse to choose, Enter/Click to confirm",
                                     True, (100, 200, 100))
        info_rect = info_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
        screen.blit(info_surf, info_rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    selected_character = "knight"
    while True:
        result = main_menu(selected_character)
        if result is None:
            break
        action, selected_character = result
        if action == "quit":
            break

        while True:
            action = main(selected_character)
            if action == "retry":
                continue  # Spustí main() znovu se stejnou postavou
            elif action == "menu":
                break  # Vylítne zpátky do main_menu() smyčky
            elif action == "quit":
                pygame.quit()
                sys.exit()