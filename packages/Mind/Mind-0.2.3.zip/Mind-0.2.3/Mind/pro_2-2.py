from Mind import Imagination
import pygame

screen = pygame.display.set_mode((800, 500))
running = True

pygame.init()

font = pygame.font.SysFont(None, 50)

Main_menu = Imagination.Main_menu(Imagination.PLACE(True), 150)
keyboard = Main_menu.get_keyboard()
keyboard.extend([(pygame.K_ESCAPE, "quit")])

Main_menu.add_option(Imagination.text_option(font, "Start", (255, 0, 0), Main_menu, pos_do=Imagination.ch_color((0, 0, 0))), True)
Main_menu.add_option(Imagination.text_option(font, "Options", (0, 255, 0), Main_menu, pos_do=Imagination.ch_color((0, 0, 0))))
Main_menu.add_option(Imagination.text_option(font, "Quit", (0, 0, 255), Main_menu, pos_do=Imagination.ch_color((0, 0, 0))))
Main_menu.set_options()

while running:
    if keyboard.keys["quit"]:
        running = False

    screen.fill((255, 255, 255))

    Main_menu.blit()

    pygame.display.flip()

pygame.quit()
