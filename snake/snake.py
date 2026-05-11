import pygame
import time
import random

# Inicializace pygame
pygame.init()

# Definice barev
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Rozměry okna
dis_width = 600
dis_height = 400

dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Klasický Had (Snake)')

clock = pygame.time.Clock()

# Velikost jednoho bloku hada a rychlost hry
snake_block = 10
snake_speed = 15

# Fonty pro texty
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def Your_score(score):
    """Funkce pro zobrazení aktuálního skóre"""
    value = score_font.render("Skóre: " + str(score), True, yellow)
    dis.blit(value, [0, 0])

def our_snake(snake_block, snake_list):
    """Vykreslení celého hada"""
    for x in snake_list:
        pygame.draw.rect(dis, green, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    """Zobrazení zpráv pro hráče uprostřed obrazovky"""
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 6, dis_height / 3])

def gameLoop():
    """Hlavní herní smyčka"""
    game_over = False
    game_close = False

    # Počáteční pozice hada (uprostřed)
    x1 = dis_width / 2
    y1 = dis_height / 2

    # Směr pohybu
    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    # Náhodné vygenerování prvního jídla
    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    while not game_over:

        # Obrazovka prohry
        while game_close == True:
            dis.fill(blue)
            message("Prohrál jsi! Zmáčkni C pro novou hru nebo Q pro konec", red)
            Your_score(Length_of_snake - 1)
            pygame.display.update()

            # Čekání na vstup od uživatele
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # Ovládání (vstupy z klávesnice)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        # Kontrola, zda had nenarazil do stěny okna
        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True
        
        # Posun hlavy hada
        x1 += x1_change
        y1 += y1_change
        
        dis.fill(blue)
        
        # Vykreslení jídla
        pygame.draw.rect(dis, red, [foodx, foody, snake_block, snake_block])
        
        # Sledování těla hada
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        
        # Udržování správné délky hada (odmazávání ocasu, když nejíme)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Kontrola, zda had nenarazil sám do sebe
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        Your_score(Length_of_snake - 1)

        pygame.display.update()

        # Pokud had narazí na jídlo
        if x1 == foodx and y1 == foody:
            # Vygenerování nového jídla na náhodné pozici
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            # Zvětšení hada
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Spuštění hry
gameLoop()
