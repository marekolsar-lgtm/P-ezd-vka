import sys
import random

def patch():
    with open("2dsurvival_game.py", "r", encoding='utf-8') as f:
        content = f.read()

    # 1. Player.__init__
    if "self.level_up_pending = 0" not in content:
        content = content.replace("self.hit_enemies = set()", "self.hit_enemies = set()\n        self.level_up_pending = 0")

    # 2. Player.add_xp
    old_add_xp = """    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.max_xp:
            self.xp -= self.max_xp
            self.level += 1
            self.max_xp = int(self.max_xp * 1.5)
            self.max_health += 1
            self.health = self.max_health"""
    new_add_xp = """    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.max_xp:
            self.xp -= self.max_xp
            self.level += 1
            self.max_xp = int(self.max_xp * 1.5)
            self.level_up_pending += 1"""
    content = content.replace(old_add_xp, new_add_xp)

    # 3. Main variables
    if "UPGRADES_POOL" not in content:
        old_score = "    score: int = 0\n    while running:"
        new_score = """    score: int = 0
    is_level_up_screen = False
    upgrades_offered = []
    UPGRADES_POOL = [
        {"name": "Max Health +20", "type": "max_health", "value": 20},
        {"name": "Damage +5", "type": "damage", "value": 5},
        {"name": "Speed +0.5", "type": "speed", "value": 0.5},
        {"name": "Heal 50%", "type": "heal", "value": 0.5},
        {"name": "Cooldown -4", "type": "cooldown", "value": 4},
    ]
    while running:"""
        content = content.replace(old_score, new_score)

    # 4. Main event loop MOUSEBUTTONDOWN
    if "if is_level_up_screen:" not in content.split("event.type == pygame.MOUSEBUTTONDOWN")[0]:
        old_mb = "for event in pygame.event.get():"
        new_mb = """for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_level_up_screen:
                    mx, my = pygame.mouse.get_pos()
                    card_w, card_h, spacing = 250, 350, 50
                    start_x = (WINDOW_WIDTH - (3*card_w + 2*spacing)) // 2
                    start_y = (WINDOW_HEIGHT - card_h) // 2
                    for idx, upgrade in enumerate(upgrades_offered):
                        rect = pygame.Rect(start_x + idx*(card_w+spacing), start_y, card_w, card_h)
                        if rect.collidepoint(mx, my):
                            if upgrade["type"] == "max_health":
                                player.max_health += upgrade["value"]
                                player.health += upgrade["value"]
                            elif upgrade["type"] == "damage":
                                global ATTACK_DAMAGE
                                ATTACK_DAMAGE += upgrade["value"]
                            elif upgrade["type"] == "speed":
                                global PLAYER_SPEED
                                PLAYER_SPEED += upgrade["value"]
                            elif upgrade["type"] == "heal":
                                player.heal(int(player.max_health * upgrade["value"]))
                            elif upgrade["type"] == "cooldown":
                                global BASE_ATTACK_COOLDOWN
                                BASE_ATTACK_COOLDOWN = max(10, BASE_ATTACK_COOLDOWN - upgrade["value"])
                            player.level_up_pending -= 1
                            is_level_up_screen = False
                            break"""
        content = content.replace(old_mb, new_mb)

    # 5. Indent the entire update block
    start_marker = "        # Aktualizace\n"
    end_marker = "        # Kreslení travnatého pozadí\n"

    if "if not is_level_up_screen:" not in content.split(start_marker)[-1][:200]:
        parts = content.split(start_marker)
        if len(parts) == 2:
            subparts = parts[1].split(end_marker)
            if len(subparts) == 2:
                block_to_indent = subparts[0]
                indented_block = "\n".join(["    " + line if line.strip() else line for line in block_to_indent.split("\n")[:-1]]) + "\n"
                
                new_block = f"""        # Aktualizace
        if player.level_up_pending > 0 and not is_level_up_screen:
            is_level_up_screen = True
            upgrades_offered = random.sample(UPGRADES_POOL, 3)

        if not is_level_up_screen:
{indented_block}
{end_marker}{subparts[1]}"""
                content = parts[0] + new_block

    # 6. UI drawing
    if "font_lg = pygame.font.Font(None, 74)" not in content:
        old_flip = "        pygame.display.flip()"
        new_flip = """        if is_level_up_screen:
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
                color = (80, 80, 80) if not rect.collidepoint(mx, my) else (120, 120, 120)
                pygame.draw.rect(screen, color, rect, border_radius=10)
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=10)
                text = font_sm.render(upgrade['name'], True, WHITE)
                screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))

        pygame.display.flip()"""
        content = content.replace(old_flip, new_flip)

    with open("2dsurvival_game.py", "w", encoding='utf-8') as f:
        f.write(content)
    print("PATCHED")

patch()
