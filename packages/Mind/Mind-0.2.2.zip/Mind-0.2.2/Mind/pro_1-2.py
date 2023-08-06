from Mind import Orientation
import pygame

class player(Orientation.map_obj):
    def __init__(self, x, y, Map, *other):
        self.pos = self.x, self.y = (x, y)
        self.Map = Map
        self.image = pygame.image.load("player.png")

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('test, arrows for moving')
Map = Orientation.moving_map('first_level', 200, 200, screen, True, {"player": player})
Map.set_edge(Map.edge_width - 10, Map.edge_height - 10)
Map.offset(10, 10)
Map.move(0, 0)
p = Map.clone_obj("player")
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
    screen.fill((255, 255, 255))
    Map.blit()
    p.set_position(*Map.get_position())
    p.blit()
    pygame.display.flip()
pygame.quit()
