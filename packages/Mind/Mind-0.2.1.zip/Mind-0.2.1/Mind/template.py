import pygame
from Mind import Orientation

pygame.init()

pygame.display.set_caption("test, arrows for moving")
screen = pygame.display.set_mode((400, 400))

Map = Orientation.moving_map("first_level", 500, 500, screen)
Map.set_position(*Map.get_camera_pos())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                Map.move(0, -10)
            if event.key == pygame.K_RIGHT:
                Map.move(10, 0)
            if event.key == pygame.K_DOWN:
                Map.move(0, 10)
            if event.key == pygame.K_LEFT:
                Map.move(-10, 0)
    Map.set_position(*Map.get_camera_pos())
    screen.fill((255, 255, 255))

    Map.blit()

    pygame.display.flip()

pygame.quit()
