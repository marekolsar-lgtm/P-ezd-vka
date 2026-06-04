import pygame, sys

# Inicializace knihovny Pygame (nutné před použitím jakýchkoliv jejích funkcí)
pygame.init()

# Vytvoření hlavního okna hry o velikosti 400x400 pixelů
screen = pygame.display.set_mode((400, 400))

# Vytvoření fontů pro texty ve hře
# Velký font pro zobrazení skóre, malý font pro text na tlačítku
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 30)

# Herní proměnné
score = 0               # Aktuální počet bodů
score_per_click = 1     # Kolik bodů hráč získá za jedno kliknutí
upgrade_cost = 10       # Aktuální cena pro další nákup upgradu

# Vytvoření obdélníků (tlačítek), na které půjde klikat
# Rect bere argumenty: x pozice, y pozice, šířka, výška
cube = pygame.Rect(150, 150, 100, 100)           # Hlavní klikací objekt (modrá kostka)
upgrade_button = pygame.Rect(10, 300, 380, 50)   # Tlačítko pro nákup upgradu

# Hlavní herní smyčka, která běží neustále dokola
while True:
    # Zpracování událostí (např. kliknutí myší, stisk klávesy)
    for event in pygame.event.get():
        # Pokud hráč klikne na křížek pro zavření okna
        if event.type == pygame.QUIT:
            pygame.quit() # Ukončení Pygame
            sys.exit()    # Ukončení celého Python programu
        
        # Pokud hráč stiskne tlačítko na myši
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 1 znamená levé tlačítko myši
            if event.button == 1:
                # Zjišťujeme, zda pozice myši při kliknutí koliduje s hlavní kostkou
                if cube.collidepoint(event.pos):
                    score += score_per_click # Přičteme body podle aktuální síly kliku
                
                # Zjišťujeme, zda hráč klikl na tlačítko upgradu
                elif upgrade_button.collidepoint(event.pos):
                    # Kontrola, zda má hráč dostatek bodů na nákup
                    if score >= upgrade_cost:
                        score -= upgrade_cost                   # Odečteme cenu
                        score_per_click += 1                    # Zvýšíme počet bodů za kliknutí
                        upgrade_cost = int(upgrade_cost * 1.5)  # Zvýšíme cenu o 50 % (int zajistí celé číslo)

    # 1. VYKRESLOVÁNÍ POZADÍ
    screen.fill((30, 30, 30)) # Tmavé pozadí (RGB hodnoty 0-255)
    
    # 2. VYKRESLOVÁNÍ OBJEKTŮ
    # Vykreslení modré klikací kostky
    pygame.draw.rect(screen, (0, 200, 255), cube) 
    
    # Vykreslení zeleného tlačítka pro upgrade
    pygame.draw.rect(screen, (50, 200, 50), upgrade_button)
    
    # 3. VYKRESLOVÁNÍ TEXTŮ
    # Příprava textu na tlačítko upgradu a jeho vykreslení
    upgrade_text = small_font.render(f"Upgrade (+1/klik) - Cena: {upgrade_cost}", True, (255, 255, 255))
    screen.blit(upgrade_text, (20, 315)) # Zobrazení na souřadnicích (x=20, y=315)
    
    # Příprava textu pro aktuální skóre a jeho vykreslení
    score_text = font.render(f"Skóre: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10)) # Zobrazení v levém horním rohu
    
    # 4. AKTUALIZACE OBRAZOVKY
    # Vykreslí vše, co jsme připravili do paměti v aktuálním snímku (frame)
    pygame.display.flip()