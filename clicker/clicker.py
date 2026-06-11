import pygame, sys, random

# Inicializace knihovny Pygame (nutné před použitím jakýchkoliv jejích funkcí)
pygame.init()

# Vytvoření hlavního okna hry o velikosti 400x600 pixelů
screen = pygame.display.set_mode((400, 600))

# Vytvoření fontů pro texty ve hře
# Velký font pro zobrazení skóre, malý font pro text na tlačítku
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 30)

# Herní proměnné
score = 0               # Aktuální počet bodů
score_per_click = 1     # Kolik bodů hráč získá za jedno kliknutí
upgrade_cost = 10       # Aktuální cena pro další nákup upgradu

autoclicker_cost = 50   # Cena pro autoklikr
autoclickers = 0        # Počet zakoupených autoklikrů

# Proměnné pro Level a XP
level = 1
xp = 0
xp_needed = 10
xp_per_click = 1
xp_upgrade_cost = 20

# Proměnné pro kritický zásah
crit_chance = 0          # Šance na kritický zásah (v procentech)
crit_upgrade_cost = 100  # Cena pro upgrade kritického zásahu

# Barva kostky
cube_color = (0, 200, 255)

# Vytvoření události pro autoklikr (každou sekundu)
AUTOCLICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(AUTOCLICK_EVENT, 1000)

# Vytvoření obdélníků (tlačítek), na které půjde klikat
# Rect bere argumenty: x pozice, y pozice, šířka, výška
cube = pygame.Rect(150, 150, 100, 100)           # Hlavní klikací objekt (modrá kostka)
upgrade_button = pygame.Rect(10, 300, 380, 50)   # Tlačítko pro nákup upgradu
autoclicker_button = pygame.Rect(10, 360, 380, 50) # Tlačítko pro autoklikr
xp_upgrade_button = pygame.Rect(10, 420, 380, 50)  # Tlačítko pro XP upgrade
crit_upgrade_button = pygame.Rect(10, 480, 380, 50) # Tlačítko pro kritický zásah

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
                    click_score = score_per_click
                    if crit_chance > 0 and random.randint(1, 100) <= crit_chance:
                        click_score *= 5 # 5x násobič za crit
                    
                    score += click_score # Přičteme body
                    xp += xp_per_click       # Přičteme XP
                    
                    if xp >= xp_needed:      # Level up logika
                        level += 1
                        xp -= xp_needed
                        xp_needed = int(xp_needed * 1.5)
                        score_per_click += 1 # Zvýšíme score per click při level upu
                        # Změníme barvu kostky na náhodnou
                        cube_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                
                # Zjišťujeme, zda hráč klikl na tlačítko upgradu
                elif upgrade_button.collidepoint(event.pos):
                    # Kontrola, zda má hráč dostatek bodů na nákup
                    if score >= upgrade_cost:
                        score -= upgrade_cost                   # Odečteme cenu
                        score_per_click += 1                    # Zvýšíme počet bodů za kliknutí
                        upgrade_cost = int(upgrade_cost * 1.5)  # Zvýšíme cenu o 50 % (int zajistí celé číslo)
                
                # Zjišťujeme, zda hráč klikl na autoklikr
                elif autoclicker_button.collidepoint(event.pos):
                    if score >= autoclicker_cost:
                        score -= autoclicker_cost
                        autoclickers += 1
                        autoclicker_cost = int(autoclicker_cost * 1.5)
                
                # Zjišťujeme, zda hráč klikl na XP upgrade
                elif xp_upgrade_button.collidepoint(event.pos):
                    if score >= xp_upgrade_cost:
                        score -= xp_upgrade_cost
                        xp_per_click += 1
                        xp_upgrade_cost = int(xp_upgrade_cost * 1.5)
                
                # Zjišťujeme, zda hráč klikl na kritický zásah
                elif crit_upgrade_button.collidepoint(event.pos):
                    if score >= crit_upgrade_cost:
                        score -= crit_upgrade_cost
                        crit_chance += 5 # Zvýšíme šanci o 5 %
                        crit_upgrade_cost = int(crit_upgrade_cost * 1.6)
        
        # Pokud nastane událost autoklikru (každou sekundu)
        elif event.type == AUTOCLICK_EVENT:
            score += autoclickers # Přidá body podle počtu autoklikrů

    # 1. VYKRESLOVÁNÍ POZADÍ
    screen.fill((30, 30, 30)) # Tmavé pozadí (RGB hodnoty 0-255)
    
    # 2. VYKRESLOVÁNÍ OBJEKTŮ
    # Vykreslení klikací kostky s její aktuální barvou
    pygame.draw.rect(screen, cube_color, cube) 
    
    # Vykreslení zeleného tlačítka pro upgrade
    pygame.draw.rect(screen, (50, 200, 50), upgrade_button)
    
    # Vykreslení oranžového tlačítka pro autoklikr
    pygame.draw.rect(screen, (200, 100, 50), autoclicker_button)
    
    # Vykreslení fialového tlačítka pro XP upgrade
    pygame.draw.rect(screen, (150, 50, 200), xp_upgrade_button)
    
    # Vykreslení červeného tlačítka pro kritický zásah
    pygame.draw.rect(screen, (220, 20, 60), crit_upgrade_button)
    
    # 3. VYKRESLOVÁNÍ TEXTŮ
    # Příprava textu na tlačítko upgradu a jeho vykreslení
    upgrade_text = small_font.render(f"Upgrade (+1/klik) - Cena: {upgrade_cost}", True, (255, 255, 255))
    screen.blit(upgrade_text, (20, 315)) # Zobrazení na souřadnicích (x=20, y=315)

    # Příprava textu pro autoklikr
    autoclicker_text = small_font.render(f"Autoklikr (+1/s) - Cena: {autoclicker_cost} ({autoclickers}x)", True, (255, 255, 255))
    screen.blit(autoclicker_text, (20, 375))
    
    # Příprava textu pro XP upgrade
    xp_upgrade_text = small_font.render(f"XP Upgrade (+1 XP/klik) - Cena: {xp_upgrade_cost}", True, (255, 255, 255))
    screen.blit(xp_upgrade_text, (20, 435))
    
    # Příprava textu pro kritický zásah
    crit_upgrade_text = small_font.render(f"Crit Chance (+5%) - Cena: {crit_upgrade_cost} ({crit_chance}%)", True, (255, 255, 255))
    screen.blit(crit_upgrade_text, (20, 495))
    
    # Příprava textu pro aktuální skóre a jeho vykreslení
    score_text = font.render(f"Skóre: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10)) # Zobrazení v levém horním rohu
    
    # Příprava textu pro Level a XP
    level_text = small_font.render(f"Level: {level} (XP: {xp}/{xp_needed})", True, (255, 255, 255))
    screen.blit(level_text, (10, 50)) # Zobrazení pod skóre
    
    # 4. AKTUALIZACE OBRAZOVKY
    # Vykreslí vše, co jsme připravili do paměti v aktuálním snímku (frame)
    pygame.display.flip()