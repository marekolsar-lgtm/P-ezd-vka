import pygame, sys

pygame.init()
screen = pygame.display.set_mode((400, 400))
font = pygame.font.Font(None, 50)

score = 0
cube = pygame.Rect(150, 150, 100, 100) # x, y, šířka, výška

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and cube.collidepoint(event.pos):
                score += 1

    screen.fill((30, 30, 30)) # Tmavé pozadí
    pygame.draw.rect(screen, (0, 200, 255), cube) # Modrá kostka
    
    score_text = font.render(f"Skóre: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()