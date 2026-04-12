import pygame
import random
import math
import sys
from typing import TypedDict, List, Tuple, cast

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

# Třída pro hráče (s animacemi)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
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
        surf.fill((0, 0, 0, 0))
        
        # Stín pod postavou (dynamický podle pohybu)
        shadow_w = 20 if not is_walking else 22
        shadow_x = 4 if not is_walking else 3
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (shadow_x, 23, shadow_w, 5))
        
        # Nohy s animací chůze (kalhoty a boty)
        leg_y = 19
        leg1_y = leg_y - (2 if is_walking and step in [0, 1] else 0)
        leg2_y = leg_y - (2 if is_walking and step in [2, 3] else 0)
        
        # Levá noha (zadní)
        pygame.draw.rect(surf, (20, 20, 80), (8, leg1_y, 4, 7))
        pygame.draw.rect(surf, (50, 50, 50), (7, leg1_y + 5, 6, 3), border_radius=1) # bota
        
        # Pravá noha (přední)
        pygame.draw.rect(surf, (20, 20, 80), (16, leg2_y, 4, 7))
        pygame.draw.rect(surf, (50, 50, 50), (15, leg2_y + 5, 6, 3), border_radius=1) # bota
        
        # Zadní ruka (za tělem)
        arm1_y = 12 - (1 if is_walking and step in [2, 3] else 0)
        pygame.draw.rect(surf, (0, 80, 180), (4, arm1_y, 4, 7), border_radius=2)
        pygame.draw.rect(surf, (255, 224, 189), (4, arm1_y + 5, 4, 3), border_radius=1) # ruka
        
        # Tělo
        pygame.draw.rect(surf, (0, 100, 220), (6, 10, 16, 10), border_radius=3)
        pygame.draw.rect(surf, (0, 80, 180), (6, 15, 16, 5), border_bottom_left_radius=3, border_bottom_right_radius=3) # stín
        
        # Opasek
        pygame.draw.rect(surf, (90, 45, 0), (6, 17, 16, 3)) 
        pygame.draw.rect(surf, (255, 215, 0), (12, 16, 4, 5), border_radius=1) # spona
        pygame.draw.rect(surf, (200, 150, 0), (13, 17, 2, 3))
        
        # Hlava
        pygame.draw.rect(surf, (255, 224, 189), (7, 2, 14, 11), border_radius=4)
        pygame.draw.rect(surf, (230, 190, 150), (7, 9, 14, 4), border_bottom_left_radius=4, border_bottom_right_radius=4) # stín na tváři
        
        # Vlasy
        pygame.draw.rect(surf, (80, 40, 0), (6, 0, 16, 4), border_top_left_radius=5, border_top_right_radius=5)
        pygame.draw.rect(surf, (80, 40, 0), (6, 3, 3, 5))
        pygame.draw.rect(surf, (80, 40, 0), (19, 3, 3, 4))
        pygame.draw.rect(surf, (100, 50, 0), (8, 0, 12, 2), border_radius=1) # odlesk
        
        # Oči
        pygame.draw.rect(surf, (255, 255, 255), (9, 6, 4, 4), border_radius=1)
        pygame.draw.rect(surf, (255, 255, 255), (15, 6, 4, 4), border_radius=1)
        
        pygame.draw.rect(surf, (20, 20, 30), (10, 7, 2, 2)) # zornička
        pygame.draw.rect(surf, (20, 20, 30), (16, 7, 2, 2)) # zornička
        
        # Přední ruka (před tělem)
        arm2_y = 12 - (1 if is_walking and step in [0, 1] else 0)
        pygame.draw.rect(surf, (0, 120, 255), (20, arm2_y, 4, 7), border_radius=2)
        pygame.draw.rect(surf, (255, 224, 189), (20, arm2_y + 5, 4, 3), border_radius=1) # ruka

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

        # Útok (automatický)
        if self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = BASE_ATTACK_COOLDOWN
            self.hit_enemies.clear()
            
            if camera:
                mx, my = pygame.mouse.get_pos()
                # Zapracování ZOOMu do projekce myši
                world_mx = (mx / ZOOM) - camera.rect.x
                world_my = (my / ZOOM) - camera.rect.y
                dx = world_mx - self.rect.centerx
                dy = world_my - self.rect.centery
                self.attack_angle = math.degrees(math.atan2(dy, dx))
                self.facing_right = dx >= 0
            else:
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

        # Damage boost timer
        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= 1
            if self.damage_boost_timer <= 0:
                self.damage_boost = 1

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

        # Hraniční kontrola světa (prevence pádu mimo mapu)
        if hasattr(self, 'rect'):
            if self.rect.left < 0:
                self.rect.left = 0
                self.vel_x = 0
            if self.rect.right > WORLD_WIDTH_PX:
                self.rect.right = WORLD_WIDTH_PX
                self.vel_x = 0
            if self.rect.top < 0:
                self.rect.top = 0
                self.vel_y = 0
            # Necháme hráče spadnout aby se mohl resetovat

    def point_in_swing(self, px, py):
        ox, oy = self.rect.center
        dx = px - ox
        dy = py - oy
        dist = math.hypot(dx, dy)
        if dist > ATTACK_SIZE * 2:
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
        if dist > ATTACK_SIZE * 2:
            return False
        return self.point_in_swing(ex, ey)

    def draw_attack(self, screen, camera):
        if self.attacking:
            center = camera.apply(self).center
            arc_radius = ATTACK_SIZE * 1.5
            
            # Větší plocha pro vykreslení srpu
            surf_size = int(arc_radius * 3)
            swoosh_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            
            progress = 1.0 - (self.attack_timer / ATTACK_DURATION)
            
            visual_attack_angle = -self.attack_angle
            start_deg = visual_attack_angle - 100
            
            # Celkový úhel švihu
            swing_extent = 200
            current_extent = swing_extent * progress
            end_deg = start_deg + current_extent
            
            points_outer = []
            points_inner = []
            
            scx = surf_size // 2
            scy = surf_size // 2
            
            segments = max(5, int(current_extent / 10))
            if segments > 0 and current_extent > 0:
                for i in range(segments + 1):
                    t = i / segments
                    angle_deg = start_deg + t * current_extent
                    angle_rad = math.radians(angle_deg)
                    
                    # Profil tloušťky
                    thickness_factor = math.sin(t * math.pi)
                    
                    # Tloušťka srpku (rozšiřuje se a zužuje)
                    current_thickness = arc_radius * 0.4 * thickness_factor
                    
                    # Vnější oblouk
                    ox = scx + math.cos(angle_rad) * arc_radius
                    oy = scy + math.sin(angle_rad) * arc_radius
                    points_outer.append((ox, oy))
                    
                    # Vnitřní oblouk
                    ix = scx + math.cos(angle_rad) * (arc_radius - current_thickness)
                    iy = scy + math.sin(angle_rad) * (arc_radius - current_thickness)
                    points_inner.append((ix, iy))
                
                points_inner.reverse()
                slash_polygon = points_outer + points_inner
                
                # Barva podle boostu útoku
                base_color = (100, 200, 255) # Cyan/modrá záře
                if getattr(self, 'damage_boost_timer', 0) > 0:
                    base_color = (255, 100, 50) # Zlatá/oranžová při boostu
                
                alpha_glow = max(0, int(200 * (1 - progress)))
                pygame.draw.polygon(swoosh_surf, (*base_color, alpha_glow), slash_polygon)
                
                # Bílý střed srpku pro ostřejší hranu
                points_core_outer = []
                points_core_inner = []
                for i in range(segments + 1):
                    t = i / segments
                    angle_deg = start_deg + t * current_extent
                    angle_rad = math.radians(angle_deg)
                    thickness_factor = math.sin(t * math.pi)
                    
                    core_thickness = arc_radius * 0.15 * thickness_factor
                    
                    ox = scx + math.cos(angle_rad) * (arc_radius - 2)
                    oy = scy + math.sin(angle_rad) * (arc_radius - 2)
                    ix = scx + math.cos(angle_rad) * (arc_radius - 2 - core_thickness)
                    iy = scy + math.sin(angle_rad) * (arc_radius - 2 - core_thickness)
                    
                    points_core_outer.append((ox, oy))
                    points_core_inner.insert(0, (ix, iy))
                    
                core_polygon = points_core_outer + points_core_inner
                alpha_core = max(0, min(255, int(255 * (1.2 - progress))))
                pygame.draw.polygon(swoosh_surf, (255, 255, 255, alpha_core), core_polygon)
            
            screen.blit(swoosh_surf, swoosh_surf.get_rect(center=center))

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

    def apply_gravity(self):
        # top-down režim; nepřítel nepotřebuje gravitační sílu
        pass

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
                # Omezení rychlosti
                self.vel_x = max(-self.speed, min(self.speed, self.vel_x))
                self.vel_y = max(-self.speed, min(self.speed, self.vel_y))

        self.apply_gravity()
        self.move(blocks)

        # Pokud nepřítel vyletí mimo svět, odstraníme ho
        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH_PX or self.rect.top < 0 or self.rect.top > WORLD_HEIGHT_PX + BLOCK_SIZE*5:
            self.kill()

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
    connections = []
    for room in rooms:
        # Pravý soused
        right_room = next((r for r in rooms if r['grid_x'] == room['grid_x']+1 and r['grid_y'] == room['grid_y']), None)
        if right_room:
            door_y = room['y'] + ((room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE
            door1 = (room['x'] + room['width'] - BLOCK_SIZE, door_y)
            door2 = (right_room['x'], right_room['y'] + ((right_room['height'] // 2) // BLOCK_SIZE) * BLOCK_SIZE)
            room['doors'].append(door1)
            right_room['doors'].append(door2)
            connections.append((door1, door2))

        # Dolní soused
        down_room = next((r for r in rooms if r['grid_x'] == room['grid_x'] and r['grid_y'] == room['grid_y']+1), None)
        if down_room:
            door_x = room['x'] + ((room['width'] // 2) // BLOCK_SIZE) * BLOCK_SIZE
            door1 = (door_x, room['y'] + room['height'] - BLOCK_SIZE)
            door2 = (door_x, down_room['y'])
            room['doors'].append(door1)
            down_room['doors'].append(door2)
            connections.append((door1, door2))

    # Místnost už nerenderujeme jako složitý dungeon; děláme otevřený travnatý svět s border stěnami.
    blocks = pygame.sprite.Group()
    block_map = {}

    min_x = min(room['x'] for room in rooms)
    min_y = min(room['y'] for room in rooms)
    max_x = max(room['x'] + room['width'] for room in rooms)
    max_y = max(room['y'] + room['height'] for room in rooms)

    # Vodorovné stěny v horní a dolní hranici
    y_top = min_y - BLOCK_SIZE
    y_bottom = max_y + BLOCK_SIZE
    for bx in range(min_x - BLOCK_SIZE, max_x + 2*BLOCK_SIZE, BLOCK_SIZE):
        block = Block(bx, y_top, 'stone')
        blocks.add(block)
        block_map[(bx, y_top)] = block
        block = Block(bx, y_bottom, 'stone')
        blocks.add(block)
        block_map[(bx, y_bottom)] = block

    # Svislé stěny vlevo a vpravo
    x_left = min_x - BLOCK_SIZE
    x_right = max_x + BLOCK_SIZE
    for by in range(min_y - BLOCK_SIZE, max_y + 2*BLOCK_SIZE, BLOCK_SIZE):
        block = Block(x_left, by, 'stone')
        blocks.add(block)
        block_map[(x_left, by)] = block
        block = Block(x_right, by, 'stone')
        blocks.add(block)
        block_map[(x_right, by)] = block

    # Přidáme hranice světa (jednobloční zdi) tak, aby hráč nemohl vypadnout ven
    min_x = min(room['x'] for room in rooms)
    min_y = min(room['y'] for room in rooms)
    max_x = max(room['x'] + room['width'] for room in rooms)
    max_y = max(room['y'] + room['height'] for room in rooms)

    # Vodorovné hrany
    for bx in range(min_x - BLOCK_SIZE, max_x + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE):
        for by in [min_y - BLOCK_SIZE, max_y + BLOCK_SIZE]:
            if (bx, by) not in block_map:
                block = Block(bx, by, 'stone')
                blocks.add(block)
                block_map[(bx, by)] = block

    # Svislé hrany
    for by in range(min_y - BLOCK_SIZE, max_y + BLOCK_SIZE + BLOCK_SIZE, BLOCK_SIZE):
        for bx in [min_x - BLOCK_SIZE, max_x + BLOCK_SIZE]:
            if (bx, by) not in block_map:
                block = Block(bx, by, 'stone')
                blocks.add(block)
                block_map[(bx, by)] = block

    items = pygame.sprite.Group()

    return blocks, items, rooms

def show_death_screen(screen, score, wave, menu_font, info_font):
    options = ["Retry", "Main Menu"]
    selected = 0
    clock = pygame.time.Clock()
    
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

            btn_font = pygame.font.Font(None, 60)
            option_surf = btn_font.render(option, True, color_text)
            option_rect = option_surf.get_rect(center=btn_rect.center)
            screen.blit(option_surf, option_rect)

        pygame.display.flip()
        clock.tick(FPS)

# Hlavní funkce hry
def main():
    global WORLD_WIDTH_PX, WORLD_HEIGHT_PX
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

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
    player = Player(start_x, start_y)

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
    UPGRADES_POOL = [
        {"name": "Minor Vitality", "rarity": "Common", "desc": "+5 Max HP", "stats": {"max_health": 5}},
        {"name": "Minor Strength", "rarity": "Common", "desc": "+1 Damage", "stats": {"damage": 1}},
        {"name": "Swiftness", "rarity": "Common", "desc": "+0.1 Speed", "stats": {"speed": 0.1}},
        
        {"name": "Warrior", "rarity": "Uncommon", "desc": "+2 Damage, -2 Max HP", "stats": {"damage": 2, "max_health": -2}},
        {"name": "Stamina", "rarity": "Uncommon", "desc": "+10 Max HP, Heal 10%", "stats": {"max_health": 10, "heal_pct": 0.1}},
        {"name": "Sprinter", "rarity": "Uncommon", "desc": "+0.3 Speed, -1 Dmg", "stats": {"speed": 0.3, "damage": -1}},
        
        {"name": "Vampire", "rarity": "Rare", "desc": "Heal 30%, +1 Dmg", "stats": {"heal_pct": 0.3, "damage": 1}},
        {"name": "Juggernaut", "rarity": "Rare", "desc": "+20 Max HP, -0.1 Speed", "stats": {"max_health": 20, "speed": -0.1}},
        {"name": "Assassin", "rarity": "Rare", "desc": "+3 Damage, -1 Cooldown", "stats": {"damage": 3, "cooldown": 1}},
        
        {"name": "Glass Cannon", "rarity": "Epic", "desc": "+5 Damage, -10 Max HP", "stats": {"damage": 5, "max_health": -10}},
        {"name": "Tank", "rarity": "Epic", "desc": "+30 Max HP, -0.2 Speed", "stats": {"max_health": 30, "speed": -0.2}},
        {"name": "Berserker", "rarity": "Epic", "desc": "+4 Dmg, +0.2 Spd, -5 HP", "stats": {"damage": 4, "speed": 0.2, "max_health": -5}},

        {"name": "God of War", "rarity": "Legendary", "desc": "+5 Dmg, +20 HP, +0.3 Spd", "stats": {"damage": 5, "max_health": 20, "speed": 0.3}},
        {"name": "Time Weaver", "rarity": "Legendary", "desc": "Cooldown -3, +0.5 Spd", "stats": {"cooldown": 3, "speed": 0.5}},
        {"name": "Immortal", "rarity": "Legendary", "desc": "+50 Max HP, Heal 100%", "stats": {"max_health": 50, "heal_pct": 1.0}}
    ]
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_level_up_screen:
                    mx, my = pygame.mouse.get_pos()
                    card_w, card_h, spacing = 250, 350, 50
                    start_x = (WINDOW_WIDTH - (3*card_w + 2*spacing)) // 2
                    start_y = (WINDOW_HEIGHT - card_h) // 2
                    for idx, upgrade in enumerate(upgrades_offered):
                        rect = pygame.Rect(start_x + idx*(card_w+spacing), start_y, card_w, card_h)
                        if rect.collidepoint(mx, my):
                            for stat, val in upgrade["stats"].items():
                                if stat == "max_health":
                                    player.max_health = max(1, player.max_health + val)
                                    player.health += val
                                elif stat == "damage":
                                    player.attack_damage += val
                                elif stat == "speed":
                                    global PLAYER_SPEED
                                    PLAYER_SPEED += val
                                elif stat == "heal_pct":
                                    player.heal(int(player.max_health * val))
                                elif stat == "cooldown":
                                    global BASE_ATTACK_COOLDOWN
                                    BASE_ATTACK_COOLDOWN = max(5, BASE_ATTACK_COOLDOWN - val)
                            
                            player.level_up_pending -= 1
                            is_level_up_screen = False
                            break
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

        # Aktualizace
        if player.level_up_pending > 0 and not is_level_up_screen:
            is_level_up_screen = True
            upgrades_offered = []
            pool_copy = list(UPGRADES_POOL)
            weights_map = {"Common": 50, "Uncommon": 25, "Rare": 15, "Epic": 8, "Legendary": 2}
            for _ in range(3):
                if not pool_copy: break
                w = [weights_map[u["rarity"]] for u in pool_copy]
                chosen = random.choices(pool_copy, weights=w, k=1)[0]
                upgrades_offered.append(chosen)
                pool_copy.remove(chosen)

        if not is_level_up_screen:
            player.update(blocks, camera)
            enemies.update(blocks, player)
            items.update(player)

            # Wave timer
            wave_timer += 1
            if wave_timer >= WAVE_DURATION:
                wave_timer = 0
                wave_number += 1
                current_spawn_interval = ENEMY_SPAWN_INTERVAL
                
                # Boss spawn na konci vlny
                cam_x = -camera.rect.x
                cam_y = -camera.rect.y
                cam_w = int(WINDOW_WIDTH / ZOOM)
                cam_h = int(WINDOW_HEIGHT / ZOOM)
                edge = random.randint(0, 3)
                offset = ENEMY_SIZE * 3
                if edge == 0:
                    bx = random.randint(cam_x - offset, cam_x + cam_w + offset)
                    by = cam_y - offset
                elif edge == 1:
                    bx = cam_x + cam_w + offset
                    by = random.randint(cam_y - offset, cam_y + cam_h + offset)
                elif edge == 2:
                    bx = random.randint(cam_x - offset, cam_x + cam_w + offset)
                    by = cam_y + cam_h + offset
                else:
                    bx = cam_x - offset
                    by = random.randint(cam_y - offset, cam_y + cam_h + offset)
                
                bx = max(BLOCK_SIZE, min(bx, WORLD_WIDTH_PX - BLOCK_SIZE))
                by = max(BLOCK_SIZE, min(by, WORLD_HEIGHT_PX - BLOCK_SIZE))
                
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
                
                    # Zjištění okraje kamery
                    cam_x = -camera.rect.x
                    cam_y = -camera.rect.y
                    cam_w = int(WINDOW_WIDTH / ZOOM)
                    cam_h = int(WINDOW_HEIGHT / ZOOM)
                
                    edge = random.randint(0, 3)
                    offset = ENEMY_SIZE + 20 # kousek mimo obrazovku
                
                    # Vygenerujeme mimo kameru, aby hráče obkličovali plynule
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

                    # Omezíme v rámci herní mapy
                    sx = max(BLOCK_SIZE, min(sx, WORLD_WIDTH_PX - BLOCK_SIZE))
                    sy = max(BLOCK_SIZE, min(sy, WORLD_HEIGHT_PX - BLOCK_SIZE))

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

            for spr in enemies:  # type: ignore
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

            # Kolize útoku s nepřáteli
            if player.attacking:
                for spr in list(enemies):  # type: ignore
                    if isinstance(spr, Enemy) and spr not in player.hit_enemies and player.attack_hits(spr):  # type: ignore
                        player.hit_enemies.add(spr)
                        spr.take_damage(player.attack_damage * player.damage_boost)
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

            # Smazání mrtvých nepřátel
            for spr in list(enemies):  # type: ignore
                if isinstance(spr, Enemy) and spr.is_dead():
                    items.add(Item(spr.rect.x, spr.rect.y, 'xp', xp_value=spr.xp_value))
                    if random.random() < 0.3:
                        items.add(Item(spr.rect.x + random.randint(-10, 10), spr.rect.y + random.randint(-10, 10), 'money', xp_value=random.randint(1, 3)))
                    spr.kill()  # type: ignore
                    score += 10  # type: ignore

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

        # Kreslení útoku
        player.draw_attack(display_surface, camera)
        
        # Škálování kamery na celou obrazovku
        scaled_surf = pygame.transform.scale(display_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(scaled_surf, (0, 0))

        # UI
        font = pygame.font.Font(None, 36)
        wave_time_left = (WAVE_DURATION - wave_timer) // FPS
        minutes = wave_time_left // 60
        seconds = wave_time_left % 60
        wave_text = font.render(f"Wave: {wave_number} ({minutes}:{seconds:02d})", True, ORANGE)
        screen.blit(wave_text, (WINDOW_WIDTH // 2 - wave_text.get_width() // 2, 10))
        level_text = font.render(f"Level: {player.level} ({player.xp}/{player.max_xp} XP)", True, CYAN)
        screen.blit(level_text, (10, 10))
        health_text = font.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
        screen.blit(health_text, (10, 50))
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 90))
        key_text = font.render(f"Keys: {player.keys}", True, WHITE)
        screen.blit(key_text, (10, 130))
        money_text = font.render(f"Money: {player.money}", True, (255, 215, 0))
        screen.blit(money_text, (10, 170))
        dmg_val = player.attack_damage * player.damage_boost
        damage_text = font.render(f"Damage: {dmg_val}", True, RED)
        screen.blit(damage_text, (10, 210))
        if player.damage_boost > 1:
            boost_text = font.render(f"Damage Boost: {player.damage_boost_timer//60}s", True, YELLOW)
            screen.blit(boost_text, (10, 250))

        if is_level_up_screen:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            font_lg = pygame.font.Font(None, 74)
            title = font_lg.render('LEVEL UP! Choose Upgrade:', True, WHITE)
            screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
            card_w, card_h, spacing = 250, 350, 50
            start_x = (WINDOW_WIDTH - (3*card_w + 2*spacing)) // 2
            start_y = (WINDOW_HEIGHT - card_h) // 2
            font_sm = pygame.font.Font(None, 36)
            mx, my = pygame.mouse.get_pos()
            for idx, upgrade in enumerate(upgrades_offered):
                rect = pygame.Rect(start_x + idx*(card_w+spacing), start_y, card_w, card_h)
                base_col = RARITY_COLORS.get(upgrade["rarity"], WHITE)
                bg_col = (base_col[0]//4, base_col[1]//4, base_col[2]//4) if not rect.collidepoint(mx, my) else (base_col[0]//3, base_col[1]//3, base_col[2]//3)
                
                pygame.draw.rect(screen, bg_col, rect, border_radius=10)
                pygame.draw.rect(screen, base_col, rect, 4, border_radius=10)
                
                name_surf = font_sm.render(upgrade['name'], True, WHITE)
                screen.blit(name_surf, (rect.centerx - name_surf.get_width()//2, rect.top + 30))
                
                rar_surf = pygame.font.Font(None, 28).render(upgrade['rarity'], True, base_col)
                screen.blit(rar_surf, (rect.centerx - rar_surf.get_width()//2, rect.top + 65))
                
                desc_font = pygame.font.Font(None, 24)
                parts = upgrade['desc'].split(", ")
                for i, part in enumerate(parts):
                    d_surf = desc_font.render(part, True, (200, 200, 200))
                    screen.blit(d_surf, (rect.centerx - d_surf.get_width()//2, rect.centery + (i * 25) - 20))

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

# Hlavní menu
def main_menu():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    menu_font = pygame.font.Font(None, 100)
    info_font = pygame.font.Font(None, 40)
    options = ["Start Game", "Quit"]
    selected = 0
    
    # Animace pro pozadí menu
    particles = []
    for _ in range(50):
        particles.append([random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), random.uniform(0.5, 2.0)])

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
                        return "start"
                    else:
                        pygame.quit()
                        sys.exit()

        # Update částic
        for p in particles:
            p[1] -= p[2]
            if p[1] < -10:
                p[1] = WINDOW_HEIGHT + 10
                p[0] = random.randint(0, WINDOW_WIDTH)

        screen.fill((20, 30, 20)) # Tmavě zelený nádech
        
        for p in particles:
            pygame.draw.circle(screen, (50, 80, 50), (int(p[0]), int(p[1])), int(p[2]*2))

        # Titulek
        title_surf = menu_font.render(TITLE, True, (255, 215, 0))
        title_shadow = menu_font.render(TITLE, True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        screen.blit(title_shadow, title_rect.move(4, 4))
        screen.blit(title_surf, title_rect)

        # Kreslení tlačítek
        button_width = 300
        button_height = 80
        for idx, option in enumerate(options):
            btn_rect = pygame.Rect(0, 0, button_width, button_height)
            btn_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 110)

            # Detekce myši
            if btn_rect.collidepoint(mx, my):
                selected = idx
                if clicked:
                    if options[selected] == "Start Game":
                        return "start"
                    else:
                        pygame.quit()
                        sys.exit()

            color_bg = (50, 150, 50) if idx == selected else (30, 80, 30)
            color_text = WHITE if idx == selected else (200, 200, 200)

            pygame.draw.rect(screen, color_bg, btn_rect, border_radius=15)
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)

            btn_font = pygame.font.Font(None, 60)
            option_surf = btn_font.render(option, True, color_text)
            option_rect = option_surf.get_rect(center=btn_rect.center)
            screen.blit(option_surf, option_rect)

        info_surf = info_font.render("Use W/S/Mouse to choose, Enter/Click to confirm", True, (100, 200, 100))
        info_rect = info_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
        screen.blit(info_surf, info_rect)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    while True:
        action = main_menu()
        if action == "quit":
            break
        
        while True:
            action = main()
            if action == "retry":
                continue # Spustí main() znovu
            elif action == "menu":
                break # Vylítne zpátky do main_menu() smyčky
            elif action == "quit":
                pygame.quit()
                sys.exit()