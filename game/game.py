import pygame
import random
import math

# Inicializace Pygame
pygame.init()

# Konstanty
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TITLE = "Terraria Roguelike"
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
SHOOTER_ENEMY_SPEED = 0.5
PROJECTILE_SPEED = 5

# Útok
ATTACK_DURATION = 10
ATTACK_SIZE = 40
ATTACK_DAMAGE = 1
BASE_ATTACK_COOLDOWN = 20  # počet snímků mezi útoky

# Zdraví hráče
PLAYER_MAX_HEALTH = 5

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
            return entity.rect.move(-self.rect.x, -self.rect.y)
        else:
            # pro útok (rect)
            return entity.move(-self.rect.x, -self.rect.y)

    def update(self, target):
        x = -target.rect.centerx + WINDOW_WIDTH // 2
        y = -target.rect.centery + WINDOW_HEIGHT // 2

        x = min(0, x)
        x = max(-(self.width - WINDOW_WIDTH), x)
        y = min(0, y)
        y = max(-(self.height - WINDOW_HEIGHT), y)

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
            self.image.fill(BROWN)
            # přidáme tečky (kamínky)
            for _ in range(5):
                dx = random.randint(4, BLOCK_SIZE-8)
                dy = random.randint(4, BLOCK_SIZE-8)
                pygame.draw.circle(self.image, (101, 67, 33), (dx, dy), 2)
        elif self.block_type == 'stone':
            self.image.fill(GRAY)
            # šedé odstíny
            for _ in range(8):
                dx = random.randint(2, BLOCK_SIZE-4)
                dy = random.randint(2, BLOCK_SIZE-4)
                pygame.draw.line(self.image, (100, 100, 100), (dx, dy), (dx+3, dy+3), 1)
        elif self.block_type == 'grass':
            self.image.fill(BROWN)
            # tráva nahoře
            pygame.draw.rect(self.image, (34, 139, 34), (0, 0, BLOCK_SIZE, 6))
            # stébla
            for i in range(4):
                x = i * 8 + 4
                pygame.draw.line(self.image, (0, 100, 0), (x, 6), (x-3, 12), 2)
        elif self.block_type == 'wood':
            self.image.fill((160, 82, 45))
            # kresba dřeva
            for i in range(3):
                y = i * 10 + 5
                pygame.draw.line(self.image, (140, 70, 30), (2, y), (BLOCK_SIZE-2, y), 2)
        else:  # default
            self.image.fill(WHITE)

# Třída pro předmět
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type='health'):
        super().__init__()
        self.item_type = item_type
        self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x + BLOCK_SIZE//2, y + BLOCK_SIZE//2))
        self.draw_item()

    def draw_item(self):
        if self.item_type == 'health':
            # červený kříž
            self.image.fill((0, 0, 0, 0))  # průhledné pozadí
            pygame.draw.rect(self.image, RED, (4, 10, 16, 4))
            pygame.draw.rect(self.image, RED, (10, 4, 4, 16))
        elif self.item_type == 'damage_boost':
            # žlutý meč
            self.image.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.image, YELLOW, [(12, 2), (22, 12), (18, 16), (8, 6)])
            pygame.draw.rect(self.image, YELLOW, (6, 14, 12, 6))
        elif self.item_type == 'key':
            # klíč
            self.image.fill((0, 0, 0, 0))
            pygame.draw.circle(self.image, ORANGE, (12, 8), 6)
            pygame.draw.rect(self.image, ORANGE, (8, 14, 8, 8))

    def apply(self, player):
        if self.item_type == 'health':
            player.heal(HEAL_AMOUNT)
        elif self.item_type == 'damage_boost':
            player.damage_boost = DAMAGE_BOOST
            player.damage_boost_timer = DAMAGE_BOOST_DURATION
        elif self.item_type == 'key':
            player.keys += 1
        self.kill()

# Třída pro střelu (projektily)
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=PROJECTILE_SPEED):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction  # (dx, dy)
        self.speed = speed

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        # pokud vyletí mimo obraz, zničíme
        if (self.rect.x < -50 or self.rect.x > WORLD_WIDTH_PX + 50 or
            self.rect.y < -50 or self.rect.y > WORLD_HEIGHT_PX + 50):
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
        self.on_ground = False
        self.health = PLAYER_MAX_HEALTH
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_hitbox = pygame.Rect(0, 0, ATTACK_SIZE, ATTACK_SIZE)
        self.facing_right = True  # pro animaci a útok
        self.damage_boost = 1
        self.damage_boost_timer = 0
        self.keys = 0

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

    def create_idle_frames(self):
        frames = []
        # 2 snímky pro postávání
        for i in range(2):
            surf = pygame.Surface((self.width, self.height))
            surf.fill(BLUE)
            # oči
            eye_offset = 2 if i == 0 else -2
            pygame.draw.circle(surf, WHITE, (8 + eye_offset, 8), 3)
            pygame.draw.circle(surf, WHITE, (20 + eye_offset, 8), 3)
            pygame.draw.circle(surf, BLACK, (9 + eye_offset, 9), 1)
            pygame.draw.circle(surf, BLACK, (21 + eye_offset, 9), 1)
            frames.append(surf)
        return frames

    def create_walk_frames(self):
        frames = []
        for i in range(4):
            surf = pygame.Surface((self.width, self.height))
            surf.fill(BLUE)
            # posun nohou
            leg_offset = i * 4
            pygame.draw.rect(surf, (0, 0, 200), (6, 20, 5, 8))
            pygame.draw.rect(surf, (0, 0, 200), (17, 20, 5, 8))
            # oči
            pygame.draw.circle(surf, WHITE, (8, 8), 3)
            pygame.draw.circle(surf, WHITE, (20, 8), 3)
            pygame.draw.circle(surf, BLACK, (9, 9), 1)
            pygame.draw.circle(surf, BLACK, (21, 9), 1)
            frames.append(surf)
        return frames

    def create_jump_frames(self):
        surf = pygame.Surface((self.width, self.height))
        surf.fill(BLUE)
        # oči překvapené
        pygame.draw.circle(surf, WHITE, (8, 6), 3)
        pygame.draw.circle(surf, WHITE, (20, 6), 3)
        pygame.draw.circle(surf, BLACK, (9, 7), 1)
        pygame.draw.circle(surf, BLACK, (21, 7), 1)
        return [surf]

    def create_attack_frames(self):
        surf = pygame.Surface((self.width, self.height))
        surf.fill(BLUE)
        # meč
        pygame.draw.line(surf, WHITE, (self.width//2, 5), (self.width//2 + 15, -5), 3)
        return [surf]

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = PLAYER_JUMP_POWER
            self.on_ground = False

        # Útok (klávesa E)
        if keys[pygame.K_e] and self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = BASE_ATTACK_COOLDOWN
            # Hitbox podle směru
            if self.facing_right:
                self.attack_hitbox.topleft = (self.rect.right, self.rect.centery - ATTACK_SIZE//2)
            else:
                self.attack_hitbox.topleft = (self.rect.left - ATTACK_SIZE, self.rect.centery - ATTACK_SIZE//2)

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

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
                elif vel_x < 0:
                    self.rect.left = block.rect.right
                elif vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

    def update(self, blocks):
        self.handle_input()
        self.apply_gravity()
        self.move(blocks)

        # Aktualizace útoku a cooldownu
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Damage boost timer
        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= 1
            if self.damage_boost_timer <= 0:
                self.damage_boost = 1

        # Animace
        if self.attacking:
            self.current_animation = 'attack'
        elif not self.on_ground:
            self.current_animation = 'jump'
        elif self.vel_x != 0:
            self.current_animation = 'walk'
        else:
            self.current_animation = 'idle'

        frames = self.animation_frames[self.current_animation]
        self.frame_index = (self.frame_index + self.animation_speed) % len(frames)
        self.image = frames[int(self.frame_index)]

        # Otočení podle směru
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw_attack(self, screen, camera):
        if self.attacking:
            attack_rect = camera.apply(self.attack_hitbox)
            # Efekt meče (čára)
            start = (attack_rect.centerx, attack_rect.centery)
            end = (start[0] + 30 if self.facing_right else start[0] - 30, start[1])
            pygame.draw.line(screen, WHITE, start, end, 5)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health = min(self.health + amount, PLAYER_MAX_HEALTH)

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
        self.on_ground = False
        self.health = 3
        self.facing_right = random.choice([True, False])

        # Vytvoření vzhledu
        self.image = pygame.Surface((self.width, self.height))
        self.draw_enemy()

    def draw_enemy(self):
        self.image.fill(RED)
        if self.enemy_type == 'walker':
            # jednoduchý červený čtverec s očima
            pygame.draw.circle(self.image, WHITE, (8, 8), 3)
            pygame.draw.circle(self.image, WHITE, (20, 8), 3)
            pygame.draw.circle(self.image, BLACK, (9, 9), 1)
            pygame.draw.circle(self.image, BLACK, (21, 9), 1)
        elif self.enemy_type == 'flying':
            self.image.fill(PURPLE)
            # křídla
            pygame.draw.polygon(self.image, (150, 0, 150), [(4, 10), (0, 14), (4, 18)])
            pygame.draw.polygon(self.image, (150, 0, 150), [(24, 10), (28, 14), (24, 18)])
        elif self.enemy_type == 'shooter':
            self.image.fill(ORANGE)
            # hlaveň
            pygame.draw.rect(self.image, (200, 100, 0), (10, 6, 12, 4))

    def apply_gravity(self):
        if self.enemy_type != 'flying':
            self.vel_y += GRAVITY
            if self.vel_y > MAX_FALL_SPEED:
                self.vel_y = MAX_FALL_SPEED

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
                    self.vel_x = -ENEMY_SPEED
                    self.facing_right = False
                elif vel_x < 0:
                    self.rect.left = block.rect.right
                    self.vel_x = ENEMY_SPEED
                    self.facing_right = True
                elif vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

    def update(self, blocks, player=None, projectiles=None):
        if self.enemy_type == 'walker':
            # Chodec: pohybuje se vpřed a mění směr při kolizi
            if self.on_ground:
                if self.facing_right:
                    self.vel_x = ENEMY_SPEED
                else:
                    self.vel_x = -ENEMY_SPEED
        elif self.enemy_type == 'flying':
            # Létající: sleduje hráče (jednoduché přiblížení)
            if player:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    self.vel_x = (dx / dist) * FLYING_ENEMY_SPEED
                    self.vel_y = (dy / dist) * FLYING_ENEMY_SPEED
                else:
                    self.vel_x = 0
                    self.vel_y = 0
                # Omezení rychlosti
                self.vel_x = max(-FLYING_ENEMY_SPEED, min(FLYING_ENEMY_SPEED, self.vel_x))
                self.vel_y = max(-FLYING_ENEMY_SPEED, min(FLYING_ENEMY_SPEED, self.vel_y))
        elif self.enemy_type == 'shooter':
            # Střelec: pomalu se pohybuje a střílí na hráče
            if self.on_ground:
                if self.facing_right:
                    self.vel_x = SHOOTER_ENEMY_SPEED
                else:
                    self.vel_x = -SHOOTER_ENEMY_SPEED
            # Střelba (náhodná nebo periodická)
            if random.random() < 0.01 and player and projectiles is not None:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    direction = (dx/dist, dy/dist)
                    projectile = Projectile(self.rect.centerx, self.rect.centery, direction)
                    projectiles.add(projectile)

        self.apply_gravity()
        self.move(blocks)

    def take_damage(self, amount):
        self.health -= amount

    def is_dead(self):
        return self.health <= 0

# Generátor dungeonu (místnosti a chodby)
def generate_dungeon(size):
    # Vytvoříme mřížku místností (každá místnost je slovník s x,y,w,h a dveřmi)
    rooms = []
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
            # Spojovací chodba mezi room a right_room
            door1_x = room['x'] + room['width']
            door1_y = room['y'] + room['height'] // 2
            door2_x = right_room['x']
            door2_y = right_room['y'] + right_room['height'] // 2
            room['doors'].append((door1_x, door1_y))
            right_room['doors'].append((door2_x, door2_y))
            # vytvoříme chodbu (bloky) - pro jednoduchost jen přímá cesta, ale musíme vyplnit bloky
            # To uděláme později při vytváření bloků

        # Dolní soused
        down_room = next((r for r in rooms if r['grid_x'] == room['grid_x'] and r['grid_y'] == room['grid_y']+1), None)
        if down_room:
            door1_x = room['x'] + room['width'] // 2
            door1_y = room['y'] + room['height']
            door2_x = down_room['x'] + down_room['width'] // 2
            door2_y = down_room['y']
            room['doors'].append((door1_x, door1_y))
            down_room['doors'].append((door2_x, door2_y))

    # Nyní vytvoříme bloky pro místnosti a chodby
    blocks = pygame.sprite.Group()
    # Nejprve vyplníme všechny místnosti bloky (např. stone)
    for room in rooms:
        for bx in range(room['x'], room['x'] + room['width'], BLOCK_SIZE):
            for by in range(room['y'], room['y'] + room['height'], BLOCK_SIZE):
                # okraje místnosti jsou z kamene, vnitřek vzduch (nebo podlaha)
                if (bx == room['x'] or bx == room['x'] + room['width'] - BLOCK_SIZE or
                    by == room['y'] or by == room['y'] + room['height'] - BLOCK_SIZE):
                    # stěny
                    block = Block(bx, by, 'stone')
                else:
                    # podlaha (dirt) - jen spodní vrstva? Pro jednoduchost dáme podlahu na spodní řádek
                    if by == room['y'] + room['height'] - BLOCK_SIZE:
                        block = Block(bx, by, 'dirt')
                    else:
                        continue  # vzduch, žádný blok
                blocks.add(block)

    # Vytvoření chodeb (přímé cesty mezi dveřmi)
    # Pro každou místnost přidáme chodby k sousedům
    # Zde implementujeme jednoduše: horizontální a vertikální tunely
    for room in rooms:
        for door in room['doors']:
            # Zkontrolujeme, zda už není blok v místě dveří? Pro jednoduchost uděláme tunel
            # door je (x,y) - střed dveří. Potřebujeme vykopat tunel k sousední místnosti
            # Toto je zjednodušené, v praxi bychom řešili spojnice
            pass

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
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Generování dungeonu
    blocks, items, rooms = generate_dungeon(DUNGEON_SIZE)
    # Velikost světa (maximální rozsah místností)
    max_x = max(room['x'] + room['width'] for room in rooms)
    max_y = max(room['y'] + room['height'] for room in rooms)
    WORLD_WIDTH_PX = max_x + BLOCK_SIZE * 5
    WORLD_HEIGHT_PX = max_y + BLOCK_SIZE * 5

    # Najdeme startovní místnost (první)
    start_room = rooms[0]
    start_x = start_room['x'] + start_room['width'] // 2
    start_y = start_room['y'] + start_room['height'] // 2
    player = Player(start_x, start_y)

    # Spawn nepřátel
    enemies = pygame.sprite.Group()
    for room in rooms:
        if random.random() < 0.7:  # 70% šance na nepřítele v místnosti
            ex = room['x'] + random.randint(2, (room['width']//BLOCK_SIZE)-3) * BLOCK_SIZE
            ey = room['y'] + random.randint(2, (room['height']//BLOCK_SIZE)-3) * BLOCK_SIZE
            enemy_type = random.choices(['walker', 'flying', 'shooter'], weights=[0.6, 0.3, 0.1])[0]
            enemy = Enemy(ex, ey, enemy_type)
            enemies.add(enemy)

    # Skupina pro projektily
    projectiles = pygame.sprite.Group()

    # Kamera
    camera = Camera(WORLD_WIDTH_PX, WORLD_HEIGHT_PX)

    # Herní smyčka
    running = True
    score = 0
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Aktualizace
        player.update(blocks)
        enemies.update(blocks, player, projectiles)
        projectiles.update()

        # Kolize hráče s nepřáteli
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                player.take_damage(1)
                # odskok
                if player.rect.centerx < enemy.rect.centerx:
                    player.vel_x = -PLAYER_SPEED * 2
                else:
                    player.vel_x = PLAYER_SPEED * 2
                player.vel_y = -5

        # Kolize střel s hráčem
        for proj in projectiles:
            if player.rect.colliderect(proj.rect):
                player.take_damage(1)
                proj.kill()

        # Kolize útoku s nepřáteli
        if player.attacking:
            for enemy in enemies:
                if player.attack_hitbox.colliderect(enemy.rect):
                    enemy.take_damage(ATTACK_DAMAGE * player.damage_boost)
                    if enemy.is_dead():
                        enemy.kill()
                        score += 10

        # Kolize s předměty
        item_hits = pygame.sprite.spritecollide(player, items, True)
        for item in item_hits:
            item.apply(player)

        # Smazání mrtvých nepřátel
        for enemy in enemies:
            if enemy.is_dead():
                enemy.kill()
                score += 10

        # Kamera
        camera.update(player)

        # Kreslení
        screen.fill(BLACK)

        # Kreslení bloků v kameře
        for block in blocks:
            if camera.rect.colliderect(block.rect):
                screen.blit(block.image, camera.apply(block))

        # Kreslení předmětů
        for item in items:
            screen.blit(item.image, camera.apply(item))

        # Kreslení nepřátel
        for enemy in enemies:
            screen.blit(enemy.image, camera.apply(enemy))

        # Kreslení střel
        for proj in projectiles:
            screen.blit(proj.image, camera.apply(proj))

        # Kreslení hráče
        screen.blit(player.image, camera.apply(player))

        # Kreslení útoku
        player.draw_attack(screen, camera)

        # UI
        font = pygame.font.Font(None, 36)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_text, (10, 10))
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 50))
        key_text = font.render(f"Keys: {player.keys}", True, WHITE)
        screen.blit(key_text, (10, 90))
        if player.damage_boost > 1:
            boost_text = font.render(f"Damage Boost: {player.damage_boost_timer//60}s", True, YELLOW)
            screen.blit(boost_text, (10, 130))

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
                    enemy_type = random.choices(['walker', 'flying', 'shooter'], weights=[0.6, 0.3, 0.1])[0]
                    enemy = Enemy(ex, ey, enemy_type)
                    enemies.add(enemy)
            projectiles = pygame.sprite.Group()
            score = 0

    pygame.quit()

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