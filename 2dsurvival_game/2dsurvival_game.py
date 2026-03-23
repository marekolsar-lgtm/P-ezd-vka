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

# Konstanty
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TITLE = "Survival Game"
FPS = 60

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
PLAYER_JUMP_POWER = -15
GRAVITY = 0.8
MAX_FALL_SPEED = 20

# Nepřátelé
ENEMY_SIZE = 28
ENEMY_SPEED = 2
FLYING_ENEMY_SPEED = 1
ENEMY_SPAWN_INTERVAL = 180  # snímků mezi spawnem (3s při 60FPS)
ENEMY_SPAWN_RADIUS_MIN = 300  # minimální vzdálenost od hráče při spawnu
ENEMY_SPAWN_ACCELERATION = 0.985  # zrychlování intervalu (max speed za cca 5 minut)
ENEMY_WAVE_BASE = 1  # začátek po jednom
ENEMY_WAVE_GROWTH = 0.05  # přidá enemáka každých 20 vln (pomalejší škálování)
ENEMY_MAX_PER_WAVE = 10  # do maxima 10
WAVE_DURATION = 7200  # 2 minuty při 60 FPS

# Útok
ATTACK_DURATION = 10
ATTACK_SIZE = 40
ATTACK_DAMAGE = 1
BASE_ATTACK_COOLDOWN = 20  # počet snímků mezi útoky

# Zdraví hráče
PLAYER_MAX_HEALTH = 5
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

    def apply(self, entity):
        if hasattr(entity, 'rect'):
            return entity.rect.move(self.rect.x, self.rect.y)
        else:
            # pro útok (rect)
            return entity.move(self.rect.x, self.rect.y)

    def update(self, target):
        # Deadzone kamery, aby malý pohyb dolů neznamenal okamžitý velký posun
        x_deadzone = 120
        y_deadzone = 90

        target_x = -target.rect.centerx + WINDOW_WIDTH // 2
        target_y = -target.rect.centery + WINDOW_HEIGHT // 2

        x = self.rect.x
        y = self.rect.y

        # horizontální posun (idle, ale hladat hranice)
        if self.width > WINDOW_WIDTH:
            if target_x > x + x_deadzone:
                x = min(target_x - x_deadzone, 0)
            elif target_x < x - x_deadzone:
                x = max(target_x + x_deadzone, -(self.width - WINDOW_WIDTH))
            x = min(0, x)
            x = max(-(self.width - WINDOW_WIDTH), x)
        else:
            x = 0

        # vertikální posun (hladina, deadzone)
        if self.height > WINDOW_HEIGHT:
            if target_y > y + y_deadzone:
                y = min(target_y - y_deadzone, 0)
            elif target_y < y - y_deadzone:
                y = max(target_y + y_deadzone, -(self.height - WINDOW_HEIGHT))
            y = min(0, y)
            y = max(-(self.height - WINDOW_HEIGHT), y)
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
    def __init__(self, x, y, item_type='health'):
        super().__init__()
        self.item_type = item_type
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

    def apply(self, player):
        if self.item_type == 'health':
            player.heal(HEAL_AMOUNT)
        elif self.item_type == 'damage_boost':
            player.damage_boost = DAMAGE_BOOST
            player.damage_boost_timer = DAMAGE_BOOST_DURATION
        elif self.item_type == 'key':
            player.keys += 1
        self.kill()

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
        self.attack_hitbox = pygame.Rect(0, 0, ATTACK_SIZE, ATTACK_SIZE)
        self.facing_right = True  # pro animaci a útok
        self.attack_angle = 0
        self.damage_boost = 1
        self.damage_boost_timer = 0
        self.keys = 0
        self.hit_cooldown = 0
        self.xp = 0
        self.level = 1
        self.max_xp = 10

        # Animace
        self.animation_frames = {
            'idle': self.create_idle_frames(),
            'walk': self.create_walk_frames(),
            'jump': self.create_jump_frames(),
            'attack': self.create_attack_frames()
        }
        self.current_animation = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animation_frames['idle'][0]

    def draw_player_base(self, surf, is_walking=False, step=0):
        surf.fill((0, 0, 0, 0))
        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (4, 22, 20, 6))
        
        # Legs
        leg_y = 20
        leg1_y = leg_y - (2 if is_walking and step % 2 == 0 else 0)
        leg2_y = leg_y - (2 if is_walking and step % 2 == 1 else 0)
        pygame.draw.rect(surf, (30, 30, 100), (8, leg1_y, 4, 8))
        pygame.draw.rect(surf, (30, 30, 100), (16, leg2_y, 4, 8))
        
        # Body
        pygame.draw.rect(surf, (0, 120, 255), (6, 10, 16, 12), border_radius=3)
        pygame.draw.rect(surf, (150, 75, 0), (6, 18, 16, 3)) # Belt
        pygame.draw.rect(surf, (255, 215, 0), (12, 17, 4, 5)) # Buckle
        
        # Head
        pygame.draw.rect(surf, (255, 224, 189), (8, 2, 12, 10), border_radius=4)
        pygame.draw.rect(surf, (100, 50, 0), (7, 1, 14, 4), border_radius=2) # Hair
        
        # Eyes
        pygame.draw.rect(surf, (255, 255, 255), (10, 6, 3, 3))
        pygame.draw.rect(surf, (255, 255, 255), (16, 6, 3, 3))
        pygame.draw.rect(surf, (0, 0, 0), (11, 7, 2, 2))
        pygame.draw.rect(surf, (0, 0, 0), (17, 7, 2, 2))

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

    def create_jump_frames(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_player_base(surf)
        # surprised eyes
        pygame.draw.rect(surf, (0, 0, 0), (11, 5, 2, 2))
        pygame.draw.rect(surf, (0, 0, 0), (17, 5, 2, 2))
        return [surf]

    def create_attack_frames(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_player_base(surf)
        # sword
        pygame.draw.line(surf, (200, 200, 200), (14, 15), (26, 0), 4)
        pygame.draw.line(surf, (255, 255, 255), (15, 15), (27, 0), 1)
        pygame.draw.circle(surf, (150, 75, 0), (14, 15), 3)
        return [surf]

    def handle_input(self, camera=None):
        keys = pygame.key.get_pressed()
        mouse_btns = pygame.mouse.get_pressed()
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

        # Útok (klávesa E nebo levé tlačítko)
        if (keys[pygame.K_e] or mouse_btns[0]) and self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = BASE_ATTACK_COOLDOWN
            
            if camera:
                mx, my = pygame.mouse.get_pos()
                world_mx = mx - camera.rect.x
                world_my = my - camera.rect.y
                dx = world_mx - self.rect.centerx
                dy = world_my - self.rect.centery
                self.attack_angle = math.degrees(math.atan2(dy, dx))
                self.facing_right = dx >= 0
            else:
                self.attack_angle = 0 if self.facing_right else 180

    def apply_gravity(self):
        # Top-down režim: gravitaci nepotřebujeme
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
            
            swoosh_surf = pygame.Surface((arc_radius*2, arc_radius*2), pygame.SRCALPHA)
            
            progress = 1.0 - (self.attack_timer / ATTACK_DURATION)
            
            visual_attack_angle = -self.attack_angle
            start_deg = visual_attack_angle - 90
            end_deg = start_deg + 180 * progress
                
            start_rad = math.radians(start_deg)
            end_rad = math.radians(end_deg)
            
            if end_rad > start_rad + 0.05:
                rect = pygame.Rect(0, 0, arc_radius*2, arc_radius*2)
                pygame.draw.arc(swoosh_surf, (255, 50, 0, 80), rect, start_rad, end_rad, int(arc_radius * 0.5))
                pygame.draw.arc(swoosh_surf, (255, 150, 0, 150), rect, start_rad, end_rad, int(arc_radius * 0.25))
                pygame.draw.arc(swoosh_surf, (255, 255, 255, 255), rect, start_rad, end_rad, 4)
            
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
            self.max_health += 1
            self.health = self.max_health

    def is_dead(self):
        return self.health <= 0

# Základní třída pro nepřítele
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type='walker'):
        super().__init__()
        self.enemy_type = enemy_type
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = 0
        self.vel_y = 0
        
        # Set different health based on enemy type
        if self.enemy_type == 'walker':
            self.health = 3
            self.xp_value = 5
            self.speed = ENEMY_SPEED
        elif self.enemy_type == 'flying':
            self.health = 2
            self.xp_value = 5
            self.speed = FLYING_ENEMY_SPEED
        elif self.enemy_type == 'tank':
            self.health = 10
            self.xp_value = 15
            self.speed = ENEMY_SPEED * 0.6
        elif self.enemy_type == 'fast':
            self.health = 1
            self.xp_value = 5
            self.speed = ENEMY_SPEED * 1.5
        else:
            self.health = 3  # default fallback
            self.xp_value = 5
            self.speed = ENEMY_SPEED
        
        self.facing_right = random.choice([True, False])

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
        if self.enemy_type in ['walker', 'tank', 'fast']:
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

    # Pro účely ukázky přidáme pár předmětů do místnostíe
    items = pygame.sprite.Group()
    for room in rooms:
        if random.random() < 0.5:
            ix = room['x'] + random.randint(2, (room['width']//BLOCK_SIZE)-3) * BLOCK_SIZE
            iy = room['y'] + random.randint(2, (room['height']//BLOCK_SIZE)-3) * BLOCK_SIZE
            item_type = random.choice(['health', 'damage_boost', 'key'])
            item = Item(ix, iy, item_type)
            items.add(item)

    return blocks, items, rooms

# Hlavní funkce hry
def main():
    global WORLD_WIDTH_PX, WORLD_HEIGHT_PX
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
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
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    else:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)

        # Aktualizace
        player.update(blocks, camera)
        enemies.update(blocks, player)

        # Wave timer
        wave_timer += 1
        if wave_timer >= WAVE_DURATION:
            wave_timer = 0
            wave_number += 1

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
                attempts += 1
                
                # Zjištění okraje kamery
                cam_x = -camera.rect.x
                cam_y = -camera.rect.y
                
                edge = random.randint(0, 3)
                offset = ENEMY_SIZE + 20 # kousek mimo obrazovku
                
                # Vygenerujeme mimo kameru, aby hráče obkličovali plynule
                if edge == 0:
                    sx = random.randint(cam_x - offset, cam_x + WINDOW_WIDTH + offset)
                    sy = cam_y - offset
                elif edge == 1:
                    sx = cam_x + WINDOW_WIDTH + offset
                    sy = random.randint(cam_y - offset, cam_y + WINDOW_HEIGHT + offset)
                elif edge == 2:
                    sx = random.randint(cam_x - offset, cam_x + WINDOW_WIDTH + offset)
                    sy = cam_y + WINDOW_HEIGHT + offset
                else:
                    sx = cam_x - offset
                    sy = random.randint(cam_y - offset, cam_y + WINDOW_HEIGHT + offset)

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
                    player.take_damage(1)
                    player.hit_cooldown = PLAYER_HIT_COOLDOWN
                # odskok
                if player.rect.centerx < spr.rect.centerx:  # type: ignore
                    player.vel_x = -PLAYER_SPEED * 2
                else:
                    player.vel_x = PLAYER_SPEED * 2
                if player.rect.centery < spr.rect.centery:  # type: ignore
                    player.vel_y = -PLAYER_SPEED * 2
                else:
                    player.vel_y = PLAYER_SPEED * 2

        # Kolize útoku s nepřáteli
        if player.attacking:
            for spr in list(enemies):  # type: ignore
                if isinstance(spr, Enemy) and player.attack_hits(spr):  # type: ignore
                    spr.take_damage(ATTACK_DAMAGE * player.damage_boost)
                    if spr.is_dead():
                        player.add_xp(spr.xp_value)
                        spr.kill()  # type: ignore
                        score += 10  # type: ignore

        # Kolize s předměty
        item_hits = pygame.sprite.spritecollide(player, items, True)
        for item in item_hits:
            item.apply(player)

        # Smazání mrtvých nepřátel
        for spr in list(enemies):  # type: ignore
            if isinstance(spr, Enemy) and spr.is_dead():
                player.add_xp(spr.xp_value)
                spr.kill()  # type: ignore
                score += 10  # type: ignore

        # Kamera
        camera.update(player)

        # Kreslení travnatého pozadí
        screen.fill((34, 110, 34))
        bg_offset_x = camera.rect.x % 64
        bg_offset_y = camera.rect.y % 64
        for i in range(-64, WINDOW_WIDTH + 64, 64):
            for j in range(-64, WINDOW_HEIGHT + 64, 64):
                pygame.draw.rect(screen, (30, 100, 30), (i + bg_offset_x, j + bg_offset_y, 32, 32))
                pygame.draw.rect(screen, (30, 100, 30), (i + 32 + bg_offset_x, j + 32 + bg_offset_y, 32, 32))

        # Obdélník pro culling (vykreslení jen na obrazovce)
        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Kreslení bloků v kameře
        for block in blocks:
            screen_pos = camera.apply(block)
            if screen_rect.colliderect(screen_pos):
                screen.blit(block.image, screen_pos)

        # Kreslení předmětů
        for item in items:
            screen.blit(item.image, camera.apply(item))

        # Kreslení nepřátel
        for enemy in enemies:
            screen.blit(enemy.image, camera.apply(enemy))

        # Kreslení hráče
        screen.blit(player.image, camera.apply(player))

        # Kreslení útoku
        player.draw_attack(screen, camera)

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
        if player.damage_boost > 1:
            boost_text = font.render(f"Damage Boost: {player.damage_boost_timer//60}s", True, YELLOW)
            screen.blit(boost_text, (10, 170))

        pygame.display.flip()

        # Konec hry (smrt)
        if player.is_dead():
            print("Game Over! Score:", score)
            pygame.time.wait(2000)
            # Restart - nový dungeon
            blocks, items, rooms = generate_dungeon(DUNGEON_SIZE)
            max_x = max(room['x'] + room['width'] for room in rooms)
            max_y = max(room['y'] + room['height'] for room in rooms)
            WORLD_WIDTH_PX = max_x + BLOCK_SIZE * 5
            WORLD_HEIGHT_PX = max_y + BLOCK_SIZE * 5
            start_room = rooms[0]
            start_x = start_room['x'] + start_room['width'] // 2
            start_y = start_room['y'] + start_room['height'] // 2
            player = Player(start_x, start_y)
            enemies = pygame.sprite.Group()
            for room in rooms:
                if random.random() < 0.7:
                    ex = room['x'] + random.randint(2, (room['width']//BLOCK_SIZE)-3) * BLOCK_SIZE
                    ey = room['y'] + random.randint(2, (room['height']//BLOCK_SIZE)-3) * BLOCK_SIZE
                    enemy_type = random.choices(['walker', 'flying'], weights=[0.7, 0.3])[0]
                    enemy = Enemy(ex, ey, enemy_type)
                    enemies.add(enemy)
            spawn_timer = 0
            current_spawn_interval = ENEMY_SPAWN_INTERVAL
            wave_number = 1
            wave_timer = 0
            total_spawns = 0

# Hlavní menu
def main_menu():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    menu_font = pygame.font.Font(None, 72)
    info_font = pygame.font.Font(None, 28)
    options = ["Start Game", "Quit"]
    selected = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if options[selected] == "Start Game":
                        return
                    else:
                        pygame.quit()
                        sys.exit()

        screen.fill(BLACK)

        title_surf = menu_font.render(TITLE, True, WHITE)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        screen.blit(title_surf, title_rect)

        for idx, option in enumerate(options):
            color = YELLOW if idx == selected else WHITE
            option_surf = menu_font.render(option, True, color)
            option_rect = option_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 90))
            screen.blit(option_surf, option_rect)

        info_surf = info_font.render("Use W/S or Up/Down to choose, Enter to confirm", True, CYAN)
        info_rect = info_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
        screen.blit(info_surf, info_rect)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main_menu()
    main()