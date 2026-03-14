import sys
import random
import os

import pygame

# konfigurace hry
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
FPS = 10

# barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)

# obstacle config
NUM_OBSTACLES = 10  # how many random static blocks to add to each game

# special food config
GOLD_FOOD_CHANCE = 0.1  # chance that food is gold (gives extra points)
GOLD_SCORE_MULT = 3

# shield power-up config
SHIELD_CHANCE = 0.08  # chance a shield spawns after eating food

# debuff config
DEBUFF_SCORE_INTERVAL = 10  # every N points you must pick a random debuff

# points upgrade constants (each food pickup counts as extra points per level)
UPGRADE_COST = 100  # base cost for first level
UPGRADE_MAX_LEVEL = 6              # how many levels of points bonus we allow
UPGRADE_FILE = os.path.join(os.path.dirname(__file__), "upgrade.txt")  # stores integer level

# coin upgrade constants
COIN_UPGRADE_COST = 100  # base cost for first coin level
COIN_UPGRADE_MAX_LEVEL = 6
COIN_UPGRADE_FILE = os.path.join(os.path.dirname(__file__), "coin_upgrade.txt")

# cesta k souboru s penězi
BALANCE_FILE = os.path.join(os.path.dirname(__file__), "balance.txt")

# highscore file
HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.txt")


def draw_block(surface, color, pos):
    rect = pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, color, rect)


def show_debuff_choice(screen, font):
    """Pauses the game and forces the player to pick 1 of 3 random debuffs.

    The player does not see which debuff is which until chosen.
    Returns a debuff function (name, apply_fn) to apply.
    """

    def render_choice_prompt(selected: int | None = None):
        screen.fill(BLACK)
        title = font.render("Choose a mystery card", True, WHITE)
        instr = font.render("Press 1, 2 or 3 to pick (you'll see the result)", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, 140))

        for i in range(3):
            x = WIDTH // 2 - 240 + i * 240
            y = HEIGHT // 2 - 80
            rect = pygame.Rect(x, y, 160, 160)
            pygame.draw.rect(screen, WHITE, rect, 3)
            label = font.render(str(i + 1), True, WHITE)
            screen.blit(
                label, (x + rect.width // 2 - label.get_width() // 2, y + rect.height // 2 - label.get_height() // 2)
            )

        if selected is not None:
            picked = font.render(f"You picked card {selected + 1}!", True, WHITE)
            screen.blit(
                picked,
                (WIDTH // 2 - picked.get_width() // 2, HEIGHT // 2 + 120),
            )

        pygame.display.flip()

    # built-in debuffs (name, apply_fn)
    def make_debuff(name, fn):
        return (name, fn)

    def apply_speed(multiplier, state):
        state["speed_mult"] = multiplier

    def apply_points(multiplier, state):
        state["points_mult"] = multiplier

    def apply_more_obstacles(state):
        state["extra_obstacles"] += 5

    def apply_moving_obstacles(state):
        state["moving_obstacles"] = True

    def apply_reverse_controls(state):
        state["reverse_controls"] = True

    def apply_random_turn(state):
        state["random_turn"] = True

    def apply_fog(state):
        state["fog"] = True

    def apply_score_penalty(state):
        state["score_penalty"] += 20

    def apply_teleport(state):
        state["teleport"] = True

    all_debuffs = [
        make_debuff("Speed x2", lambda s: apply_speed(2, s)),
        make_debuff("Speed x3", lambda s: apply_speed(3, s)),
        make_debuff("Speed x4", lambda s: apply_speed(4, s)),
        make_debuff("Random turn", apply_random_turn),
        make_debuff("Foggy vision", apply_fog),
        make_debuff("Points ×0.5", lambda s: apply_points(0.5, s)),
        make_debuff("More obstacles", apply_more_obstacles),
        make_debuff("Moving obstacles", apply_moving_obstacles),
        make_debuff("Reverse controls", apply_reverse_controls),
        make_debuff("Score -20", apply_score_penalty),
        make_debuff("Teleport head", apply_teleport),
    ]

    choices = random.sample(all_debuffs, 3)

    render_choice_prompt()
    selected_index = None
    while selected_index is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    selected_index = 0
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    selected_index = 1
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    selected_index = 2
        if selected_index is not None:
            render_choice_prompt(selected_index)
            pygame.time.delay(500)
            name = choices[selected_index][0]
            show_message(screen, font, f"Debuff: {name}", 1500)
            return choices[selected_index]

    return choices[0]


def load_points_level() -> int:
    """Return current points upgrade level (0=no bonus)."""
    try:
        with open(UPGRADE_FILE, "r") as f:
            lvl = int(f.read().strip())
            return max(0, min(UPGRADE_MAX_LEVEL, lvl))
    except (FileNotFoundError, ValueError):
        return 0






def save_points_level(lvl: int) -> None:
    """Persist the points upgrade level (clamped)."""
    lvl = max(0, min(UPGRADE_MAX_LEVEL, lvl))
    with open(UPGRADE_FILE, "w") as f:
        f.write(str(lvl))


def load_coin_level() -> int:
    """Return current coin upgrade level (0=no bonus)."""
    try:
        with open(COIN_UPGRADE_FILE, "r") as f:
            lvl = int(f.read().strip())
            return max(0, min(COIN_UPGRADE_MAX_LEVEL, lvl))
    except (FileNotFoundError, ValueError):
        return 0


def save_coin_level(lvl: int) -> None:
    lvl = max(0, min(COIN_UPGRADE_MAX_LEVEL, lvl))
    with open(COIN_UPGRADE_FILE, "w") as f:
        f.write(str(lvl))


def main():
    pygame.init()
    # fullscreen map size
    info = pygame.display.Info()
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = info.current_w, info.current_h
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    # font pro vykreslení textu
    font = pygame.font.SysFont(None, 36)

    # načíst zůstatek peněz a stav upgradů (persistuje přes spuštění)
    balance = load_balance()
    highscore = load_highscore()
    points_level = load_points_level()
    coin_level = load_coin_level()

    # hlavní smyčka menu
    while True:
        choice = show_menu(screen, font, balance, clock, highscore)
        # reload state in case menu changed things
        balance = load_balance()
        highscore = load_highscore()
        points_level = load_points_level()
        coin_level = load_coin_level()
        if choice == "play":
            before = balance
            final_score = run_game(screen, clock, font, points_level)

            # update highscore
            if final_score > highscore:
                highscore = final_score
                save_highscore(highscore)
                show_message(screen, font, "NEW HIGHSCORE!", 2000)

            earned = calculate_money(final_score, coin_level)
            balance = before + earned
            save_balance(balance)
            print(
                f"Game over. Score {final_score}, earned {earned} coins. "
                f"Balance {before} -> {balance} coins."
            )
            # krátké zobrazení výsledků před návratem do menu
            show_message(
                screen,
                font,
                f"Score {final_score}, +{earned} (total {balance})",
                2000,
            )
        else:  # quit
            break

    # před úplným ukončením zajistit uložený zůstatek
    save_balance(balance)
    pygame.quit()
    sys.exit()


def place_food(snake, occupied=None):
    """Vybere náhodnou pozici pro jídlo, která nekoliduje s hadem nebo překážkami.

    Náhodně může být jídlo zlaté (gold), které dává více bodů.
    """
    if occupied is None:
        occupied = []
    max_x = WIDTH // BLOCK_SIZE
    max_y = HEIGHT // BLOCK_SIZE
    while True:
        x = random.randint(0, max_x - 1) * BLOCK_SIZE
        y = random.randint(0, max_y - 1) * BLOCK_SIZE
        if (x, y) not in snake and (x, y) not in occupied:
            is_gold = random.random() < GOLD_FOOD_CHANCE
            return (x, y), is_gold


def place_obstacles(snake, food, count: int):
    """Generuje pevné překážky, které hra nepotřebuje k přežití."""
    obstacles = set()
    max_x = WIDTH // BLOCK_SIZE
    max_y = HEIGHT // BLOCK_SIZE
    while len(obstacles) < count:
        x = random.randint(0, max_x - 1) * BLOCK_SIZE
        y = random.randint(0, max_y - 1) * BLOCK_SIZE
        pos = (x, y)
        if pos in snake or pos == food or pos in obstacles:
            continue
        obstacles.add(pos)
    return list(obstacles)


def run_game(screen, clock, font, points_level: int) -> int:
    """Spustí jednu hru; vrátí skóre po smrti.

    points_level indicates how many extra points each food pickup gives.
    Level 0 = normal points (1 per pickup), level 1 = 2 points per pickup.

    Every DEBUFF_SCORE_INTERVAL points, the player must pick one of 3 unknown debuffs.
    """
    # počáteční pozice – vždy délka 1
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (0, -BLOCK_SIZE)
    (food, food_is_gold) = place_food(snake)
    shield_pos = None
    obstacles = place_obstacles(snake, food, NUM_OBSTACLES)

    state = {
        "speed_mult": 1.0,
        "points_mult": 1.0,
        "extra_obstacles": 0,
        "moving_obstacles": False,
        "reverse_controls": False,
        "random_turn": False,
        "fog": False,
        "score_penalty": 0,
        "teleport": False,
        "shield": False,
    }
    moving_obstacles = []  # list of dicts with {'pos': ..., 'dir': (...)}
    next_debuff_score = DEBUFF_SCORE_INTERVAL

    def occupied_positions():
        occ = set(snake)
        occ.update(obstacles)
        occ.update(mo["pos"] for mo in moving_obstacles)
        return occ

    def add_static_obstacles(count: int):
        nonlocal obstacles
        new = place_obstacles(snake, food, count)
        obstacles.extend(new)

    def add_moving_obstacles(count: int):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for _ in range(count):
            pos, _ = place_food(snake, occupied=list(occupied_positions()))
            moving_obstacles.append({"pos": pos, "dir": random.choice(dirs)})

    def place_shield():
        # create a one-time shield on the map (only coord, no gold flag)
        if random.random() < SHIELD_CHANCE:
            pos, _ = place_food(snake, occupied=list(occupied_positions()))
            return pos
        return None

    running = True
    gold_multiplier = 1
    need_debuff = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                reverse = state["reverse_controls"]
                if event.key == pygame.K_UP:
                    if reverse:
                        if direction != (0, -BLOCK_SIZE):
                            direction = (0, BLOCK_SIZE)
                    else:
                        if direction != (0, BLOCK_SIZE):
                            direction = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN:
                    if reverse:
                        if direction != (0, BLOCK_SIZE):
                            direction = (0, -BLOCK_SIZE)
                    else:
                        if direction != (0, -BLOCK_SIZE):
                            direction = (0, BLOCK_SIZE)
                elif event.key == pygame.K_LEFT:
                    if reverse:
                        if direction != (-BLOCK_SIZE, 0):
                            direction = (BLOCK_SIZE, 0)
                    else:
                        if direction != (BLOCK_SIZE, 0):
                            direction = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT:
                    if reverse:
                        if direction != (BLOCK_SIZE, 0):
                            direction = (-BLOCK_SIZE, 0)
                    else:
                        if direction != (-BLOCK_SIZE, 0):
                            direction = (BLOCK_SIZE, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # if a debuff is needed, show it now
        if need_debuff:
            name, fn = show_debuff_choice(screen, font)
            fn(state)
            need_debuff = False

            if state["extra_obstacles"] > 0:
                add_static_obstacles(state["extra_obstacles"])
                state["extra_obstacles"] = 0
            if state["moving_obstacles"] and not moving_obstacles:
                add_moving_obstacles(5)
            if state["random_turn"]:
                state["random_turn"] = False
            if state["fog"]:
                state["fog"] = False
            if state["teleport"]:
                snake[0], _ = place_food(snake, occupied=list(occupied_positions()))
                state["teleport"] = False

        # apply random-turn debuff (occasionally twist direction)
        if state["random_turn"] and random.random() < 0.1:
            possible_dirs = [(0, -BLOCK_SIZE), (0, BLOCK_SIZE), (-BLOCK_SIZE, 0), (BLOCK_SIZE, 0)]
            possible_dirs = [d for d in possible_dirs if d != (-direction[0], -direction[1])]
            direction = random.choice(possible_dirs)

        # move moving obstacles
        if state["moving_obstacles"]:
            for mo in moving_obstacles:
                x, y = mo["pos"]
                dx, dy = mo["dir"]
                new_pos = (x + dx * BLOCK_SIZE, y + dy * BLOCK_SIZE)

                if (
                    new_pos[0] < 0
                    or new_pos[0] >= WIDTH
                    or new_pos[1] < 0
                    or new_pos[1] >= HEIGHT
                    or new_pos in obstacles
                    or new_pos in [m["pos"] for m in moving_obstacles if m is not mo]
                ):
                    mo["dir"] = (-dx, -dy)
                    new_pos = (x - dx * BLOCK_SIZE, y - dy * BLOCK_SIZE)

                mo["pos"] = new_pos

                if new_pos == food:
                    food, food_is_gold = place_food(snake, occupied=list(occupied_positions()))

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, new_head)

        # shield pickup
        shield_collected = False
        if shield_pos is not None and new_head == shield_pos:
            state["shield"] = True
            shield_pos = None
            shield_collected = True
            show_message(screen, font, "Shield collected!", 1200)

        if (
            new_head[0] < 0
            or new_head[0] >= WIDTH
            or new_head[1] < 0
            or new_head[1] >= HEIGHT
        ):
            if state["shield"]:
                state["shield"] = False
            else:
                running = False
        if new_head in snake[1:]:
            if state["shield"]:
                state["shield"] = False
            else:
                running = False
        if new_head in obstacles or new_head in [m["pos"] for m in moving_obstacles]:
            if state["shield"]:
                state["shield"] = False
            else:
                running = False

        if new_head == food or shield_collected:
            # normal food consumption: grow by not popping tail
            if not shield_collected:
                (food, food_is_gold) = place_food(snake, occupied=list(occupied_positions()))

            # maybe spawn a shield power-up
            if shield_pos is None:
                shield_pos = place_shield()

            base_score = len(snake) - 1
            trigger_score = int(base_score * (1 + points_level))

            if food_is_gold and not shield_collected:
                gold_multiplier = GOLD_SCORE_MULT
            score = int(base_score * (1 + points_level) * state["points_mult"] * gold_multiplier)

            # if base/points-level score crosses the next threshold, schedule a debuff
            if trigger_score >= next_debuff_score:
                need_debuff = True
                next_debuff_score = (trigger_score // DEBUFF_SCORE_INTERVAL + 1) * DEBUFF_SCORE_INTERVAL
        else:
            snake.pop()

        base_score = len(snake) - 1
        trigger_score = int(base_score * (1 + points_level))
        score = int(base_score * (1 + points_level) * state["points_mult"] * gold_multiplier)
        score = max(0, score - state["score_penalty"])
        score_surf = font.render(f"Score: {score}", True, WHITE)

        # reset gold multiplier after applying it once
        gold_multiplier = 1

        if trigger_score >= 100:
            show_message(screen, font, "You reached 100! You win!", 2500)
            running = False

        # show gold food indicator
        if food_is_gold:
            gold_msg = font.render("Golden food!", True, GOLD)
            screen.blit(gold_msg, (10, 40))

        # show shield indicator
        if state["shield"]:
            shield_msg = font.render("Shield active", True, CYAN)
            screen.blit(shield_msg, (10, 70))

        # show fog indicator
        if state["fog"]:
            fog_msg = font.render("Foggy vision", True, WHITE)
            screen.blit(fog_msg, (10, 100))
            fog_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fog_overlay.fill((0, 0, 0, 100))
            screen.blit(fog_overlay, (0, 0))

        if score >= 100:
            show_message(screen, font, "You reached 100! You win!", 2500)
            running = False

        screen.fill(BLACK)
        for block in snake:
            draw_block(screen, GREEN, block)
        for obs in obstacles:
            draw_block(screen, BLUE, obs)
        for mo in moving_obstacles:
            draw_block(screen, BLUE, mo["pos"])
        draw_block(screen, GOLD if food_is_gold else RED, food)
        if shield_pos is not None:
            draw_block(screen, CYAN, shield_pos)

        screen.blit(score_surf, (10, 10))

        pygame.display.flip()
        target_fps = max(1, int(FPS * state["speed_mult"]))
        clock.tick(target_fps)

    return score


def show_menu(screen, font, balance: int, clock, highscore: int) -> str:
    """Zobrazí menu; vrací 'play' nebo 'quit'"""
    points_level = load_points_level()
    coin_level = load_coin_level()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "play"
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "quit"
                elif event.key == pygame.K_r:
                    # reset balance and redisplay menu
                    balance = 0
                    save_balance(balance)
                    # also reset points and coin levels
                    points_level = 0
                    save_points_level(points_level)
                    coin_level = 0
                    save_coin_level(coin_level)
                    # show a brief confirmation
                    show_message(screen, font, "Balance/upgrades reset", 1000)
                elif event.key == pygame.K_u and points_level < UPGRADE_MAX_LEVEL:
                    # attempt to buy/upgrade points bonus
                    cost = UPGRADE_COST * (points_level + 1)
                    if balance >= cost:
                        balance -= cost
                        save_balance(balance)
                        points_level += 1
                        save_points_level(points_level)
                        show_message(
                            screen,
                            font,
                            f"Points level {points_level}",
                            1500,
                        )
                    else:
                        show_message(screen, font, "Not enough coins", 1500)
                elif event.key == pygame.K_c and coin_level < COIN_UPGRADE_MAX_LEVEL:
                    cost = COIN_UPGRADE_COST * (coin_level + 1)
                    if balance >= cost:
                        balance -= cost
                        save_balance(balance)
                        coin_level += 1
                        save_coin_level(coin_level)
                        show_message(
                            screen,
                            font,
                            f"Coin bonus level {coin_level}",
                            1500,
                        )
                    else:
                        show_message(screen, font, "Not enough coins", 1500)

        screen.fill(BLACK)
        title = font.render("Snake Game", True, WHITE)
        play = font.render("Press Enter to play", True, WHITE)
        quit_msg = font.render("Esc or Q to quit", True, WHITE)
        reset_msg = font.render("R to reset coins/upgrades", True, WHITE)
        bal = font.render(f"Coins: {balance}", True, WHITE)
        highscore_msg = font.render(f"Highscore: {highscore}", True, WHITE)
        points_msg = font.render(f"Points Lv {points_level}", True, WHITE)
        coin_msg = font.render(f"Coin Lv {coin_level}", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(play, (WIDTH // 2 - play.get_width() // 2, 200))
        screen.blit(quit_msg, (WIDTH // 2 - quit_msg.get_width() // 2, 250))
        screen.blit(reset_msg, (WIDTH // 2 - reset_msg.get_width() // 2, 300))
        screen.blit(bal, (10, 10))
        screen.blit(highscore_msg, (10, 40))
        screen.blit(points_msg, (10, 70))
        screen.blit(coin_msg, (10, 100))
        if points_level < UPGRADE_MAX_LEVEL:
            next_cost = UPGRADE_COST * (points_level + 1)
            buy_msg = font.render(
                f"U to upgrade points ({next_cost})", True, WHITE
            )
            screen.blit(buy_msg, (WIDTH // 2 - buy_msg.get_width() // 2, 350))
        else:
            owned = font.render("Points max level", True, WHITE)
            screen.blit(owned, (WIDTH // 2 - owned.get_width() // 2, 350))
        if coin_level < COIN_UPGRADE_MAX_LEVEL:
            cost = COIN_UPGRADE_COST * (coin_level + 1)
            buyc = font.render(
                f"C to upgrade coins ({cost})", True, WHITE
            )
            screen.blit(buyc, (WIDTH // 2 - buyc.get_width() // 2, 380))
        else:
            maxc = font.render("Coin bonus max", True, WHITE)
            screen.blit(maxc, (WIDTH // 2 - maxc.get_width() // 2, 380))
        pygame.display.flip()
        clock.tick(15)


def show_message(screen, font, text: str, ms: int) -> None:
    """Zobrazí text na střed obrazovky po ms milisekund"""
    end = pygame.time.get_ticks() + ms
    while pygame.time.get_ticks() < end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BLACK)
        msg = font.render(text, True, WHITE)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(50)


def calculate_money(score: int, coin_level: int) -> int:
    """Vrátí částku za skóre včetně bonusu z coin upgrade."""
    base = score * 10
    # každá úroveň přidává +100% základního zisku (level 1 = ×2)
    return base * (1 + coin_level)


def load_balance() -> int:
    """Načte zůstatek peněz ze souboru; vrací 0 pokud soubor neexistuje."""
    try:
        with open(BALANCE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_balance(amount: int) -> None:
    """Uloží zůstatek peněz do souboru."""
    with open(BALANCE_FILE, "w") as f:
        f.write(str(amount))


def load_highscore() -> int:
    """Načte nejlepší skóre z disku; vrací 0, pokud chybí."""
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_highscore(score: int) -> None:
    """Uloží nejlepší skóre."""
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


if __name__ == "__main__":
    main()
