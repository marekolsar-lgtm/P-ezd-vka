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

# shockwave upgrade constants
UPGRADE_COST = 100  # base cost for first level
UPGRADE_MAX_LEVEL = 6              # how many levels of shockwave we allow
UPGRADE_FILE = os.path.join(os.path.dirname(__file__), "upgrade.txt")  # stores integer level

# coin upgrade constants
COIN_UPGRADE_COST = 100  # base cost for first coin level
COIN_UPGRADE_MAX_LEVEL = 6
COIN_UPGRADE_FILE = os.path.join(os.path.dirname(__file__), "coin_upgrade.txt")

# cesta k souboru s penězi
BALANCE_FILE = os.path.join(os.path.dirname(__file__), "balance.txt")


def draw_block(surface, color, pos):
    rect = pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, color, rect)


def load_shock_level() -> int:
    """Return current shockwave level (0=no ability)."""
    try:
        with open(UPGRADE_FILE, "r") as f:
            lvl = int(f.read().strip())
            return max(0, min(UPGRADE_MAX_LEVEL, lvl))
    except (FileNotFoundError, ValueError):
        return 0






def save_shock_level(lvl: int) -> None:
    """Persist the shockwave level (clamped)."""
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
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    # font pro vykreslení textu
    font = pygame.font.SysFont(None, 36)

    # načíst zůstatek peněz a stav upgradů (persistuje přes spuštění)
    balance = load_balance()
    shock_level = load_shock_level()
    coin_level = load_coin_level()

    # hlavní smyčka menu
    while True:
        choice = show_menu(screen, font, balance, clock)
        # reload state in case menu changed things
        balance = load_balance()
        shock_level = load_shock_level()
        coin_level = load_coin_level()
        if choice == "play":
            before = balance
            final_score = run_game(screen, clock, font, shock_level)
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


def place_food(snake):
    """Vybere náhodnou pozici pro jídlo, která nekoliduje s hadem."""
    max_x = WIDTH // BLOCK_SIZE
    max_y = HEIGHT // BLOCK_SIZE
    while True:
        x = random.randint(0, max_x - 1) * BLOCK_SIZE
        y = random.randint(0, max_y - 1) * BLOCK_SIZE
        if (x, y) not in snake:
            return (x, y)


def run_game(screen, clock, font, shock_level: int) -> int:
    """Spustí jednu hru; vrátí skóre po smrti.

    shock_level indicates level of shockwave ability; if >0 the player can
    trigger the effect by pressing SPACE.  Higher levels increase radius.

    When the shockwave is activated it will collect any food within the
    radius as if the snake had eaten it; the snake grows and the score goes
    up accordingly.  This happens instantly and uses an internal
    ``extra_growth`` counter to make the next move longer.
    """
    # počáteční pozice – vždy délka 1
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (0, -BLOCK_SIZE)
    food = place_food(snake)
    running = True
    # cool‑down for the shockwave (simple timer) in milliseconds
    shock_cooldown = 0
    SHOCK_DURATION = 300  # how long the effect stays visible
    shock_time = 0

    # extra growth to apply on next move (used when a shockwave collects food)
    extra_growth = 0

    # radius depends on level (level 0 = no ability)
    base_radius_blocks = 2  # original radius when level==1 is 2 blocks
    radius_blocks = base_radius_blocks + max(0, shock_level - 1)
    shock_radius = radius_blocks * BLOCK_SIZE

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, BLOCK_SIZE):
                    direction = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -BLOCK_SIZE):
                    direction = (0, BLOCK_SIZE)
                elif event.key == pygame.K_LEFT and direction != (BLOCK_SIZE, 0):
                    direction = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-BLOCK_SIZE, 0):
                    direction = (BLOCK_SIZE, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif (
                    shock_level > 0
                    and event.key == pygame.K_SPACE
                    and shock_cooldown <= 0
                ):
                    # trigger shockwave
                    shock_time = pygame.time.get_ticks()
                    shock_cooldown = 2000  # 2 seconds before next use
                    # if food is within the level-dependent radius, collect it
                    dx = snake[0][0] - food[0]
                    dy = snake[0][1] - food[1]
                    if (dx * dx + dy * dy) <= shock_radius * shock_radius:
                        # schedule a growth for the next move and reposition food
                        extra_growth += 1
                        food = place_food(snake)
        # decrement cooldown each frame
        if shock_cooldown > 0:
            shock_cooldown -= clock.get_time()

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, new_head)

        if (
            new_head[0] < 0
            or new_head[0] >= WIDTH
            or new_head[1] < 0
            or new_head[1] >= HEIGHT
        ):
            running = False
        if new_head in snake[1:]:
            running = False

        if new_head == food:
            # normal food consumption: grow by not popping tail
            food = place_food(snake)
        else:
            if extra_growth > 0:
                # shockwave picked up a food earlier; apply growth
                extra_growth -= 1
            else:
                snake.pop()

        score = len(snake) - 1
        score_surf = font.render(f"Score: {score}", True, WHITE)

        screen.fill(BLACK)
        for block in snake:
            draw_block(screen, GREEN, block)
        draw_block(screen, RED, food)

        # draw shockwave effect if active
        if shock_time and pygame.time.get_ticks() - shock_time < SHOCK_DURATION:
            pygame.draw.circle(
                screen,
                WHITE,
                (snake[0][0] + BLOCK_SIZE // 2, snake[0][1] + BLOCK_SIZE // 2),
                shock_radius,
                2,
            )

        screen.blit(score_surf, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    return len(snake) - 1


def show_menu(screen, font, balance: int, clock) -> str:
    """Zobrazí menu; vrací 'play' nebo 'quit'"""
    shock_level = load_shock_level()
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
                    # also reset shockwave and coin levels
                    shock_level = 0
                    save_shock_level(shock_level)
                    coin_level = 0
                    save_coin_level(coin_level)
                    # show a brief confirmation
                    show_message(screen, font, "Balance/upgrades reset", 1000)
                elif event.key == pygame.K_u and shock_level < UPGRADE_MAX_LEVEL:
                    # attempt to buy/upgrade shockwave
                    cost = UPGRADE_COST * (shock_level + 1)
                    if balance >= cost:
                        balance -= cost
                        save_balance(balance)
                        shock_level += 1
                        save_shock_level(shock_level)
                        show_message(
                            screen,
                            font,
                            f"Shockwave level {shock_level}",
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
        shock_msg = font.render(f"Shock Lv {shock_level}", True, WHITE)
        coin_msg = font.render(f"Coin Lv {coin_level}", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(play, (WIDTH // 2 - play.get_width() // 2, 200))
        screen.blit(quit_msg, (WIDTH // 2 - quit_msg.get_width() // 2, 250))
        screen.blit(reset_msg, (WIDTH // 2 - reset_msg.get_width() // 2, 300))
        screen.blit(bal, (10, 10))
        screen.blit(shock_msg, (10, 40))
        screen.blit(coin_msg, (10, 70))
        if shock_level < UPGRADE_MAX_LEVEL:
            next_cost = UPGRADE_COST * (shock_level + 1)
            buy_msg = font.render(
                f"U to upgrade shockwave ({next_cost})", True, WHITE
            )
            screen.blit(buy_msg, (WIDTH // 2 - buy_msg.get_width() // 2, 350))
        else:
            owned = font.render("Shockwave max level", True, WHITE)
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


if __name__ == "__main__":
    main()
