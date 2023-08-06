import Imagination
import pygame

screen = pygame.display.set_mode((800, 500))
running = True

pygame.init()

font = pygame.font.SysFont(None, 50)
MAIN_MENU = Imagination.PLACE(True)
OPTION_MENU = Imagination.PLACE()
game = Imagination.Game(MAIN_MENU)
Menu = Imagination.Main_menu(MAIN_MENU, 150)
Menu.add_option(Imagination.text_option(font, "Start", (255, 0, 0), Menu,
pos_do=Imagination.ch_color((0, 0, 0)), anti_pos_do=Imagination.ch_color((
255, 0, 0))))
Menu.add_option(Imagination.text_option(font, "Options", (0, 255, 0), Menu, do2=Imagination.link(OPTION_MENU), time=200,
pos_do=Imagination.ch_color((0, 0, 0)), anti_pos_do=Imagination.ch_color((
0, 255, 0))))
Menu.add_option(Imagination.text_option(font, "Quit", (0, 0, 255), Menu,
pos_do=Imagination.ch_color((0, 0, 0)), anti_pos_do=Imagination.ch_color((
0, 0, 255))), True)
Menu.set_options()
Menu.set_game(game)
Options = Imagination.Main_menu(OPTION_MENU, 200)
Options.add_option(Imagination.text_option(font, "Sound", (0, 0, 255), Menu), True)
Options.set_options()
Options.set_game(game)

while running:
    event_get = pygame.event.get()
    for event in event_get:
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    game.blit(event_get)

    pygame.display.flip()

pygame.quit()
