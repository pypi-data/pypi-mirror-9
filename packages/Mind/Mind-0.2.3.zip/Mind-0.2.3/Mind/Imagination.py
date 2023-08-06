"""
Part of library for Main Menu.
"""

import pygame

<<<<<<< HEAD
ARROWS = [(pygame.K_UP, "up"), (pygame.K_DOWN, "down"), (pygame.K_LEFT, "left"), (pygame.K_RIGHT, "right")]
"""List of keys (arrows) for Menu changing index.
"""
HIT = [(pygame.K_RETURN, "hit"), (pygame.K_SPACE, "hit")]
"""List of keys for Menu selecting option.
"""


def useless(*useless_args):
    """Function that doesn't do anything.
    """
=======
ARROWS = [(pygame.K_UP, pygame.K_DOWN)]
"""List of keys (arrows) for Menu changing index."""
HIT = [pygame.K_RETURN, pygame.K_SPACE]
"""List of keys for Menu selecting option."""


def useless(*args):
    """Function that doesn't do anything."""
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
    pass


def ch_image(new_image):
    """Returns function which changes pusher image.
    """
    def function(obj, self):
        self.image = new_image
    return function


def ch_text(new_text, error=True):
    """Returns function which changes pusher text (only for text_pushers).
    """
    def function(obj, self):
        if type(self) == text_pusher:
            self.text = new_text
            self.update()
        else:
            if error:
                raise TypeError(str(type(self)) +
                " should be text_pusher!")
    return function


def ch_color(new_color, error=True):
    """Returns function which changes pusher color (only for text_pushers).
    """
    def function(obj, self):
        if type(self) == text_pusher:
            self.color = new_color
            self.update()
        else:
            if error:
                raise TypeError(str(type(self)) +
                " should be text_pusher!")
    return function


def ch_font(new_font, error=True):
    """Returns function which changes pusher font (only for text_pushers).
    """
    def function(obj, self):
        if type(self) == text_pusher:
            self.font = new_font
            self.update()
        else:
            if error:
                raise TypeError(str(type(self)) +
                " should be text_pusher!")
    return function


def link(place):
    """Returns function which leads game to onother place.
    """
    def function(obj, self):
<<<<<<< HEAD
        obj.game.change(place)
    return function


def Quit(obj, self):
    """Quits game.
    """
    obj.game.kill()


=======
        obj.game.current = place
    return function


>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
def joied(List):
    """Returns function which executes all function in a given list.
    """
    def function(self, obj):
        for f in List:
            f(self, obj)
    return function


def equal(image1, image2):
    """Test if two images are equal.*
    """
    if image1.get_size() != image2.get_size():
        return False
    X, Y = image1.get_size()
    for y in range(Y):
        for x in range(X):
            if image1.get_at((x, y)) != image1.get_at((x, y)):
                return False
    return True


class PLACE:
    """Bacis class for states of main menu.
    """
    def __init__(self, active=False):
        self.active = active

    def __bool__(self):
        return self.active

    def activate(self):
        """Activates place.
        """
        self.active = True

    def deactivate(self):
        """Deactivates place.
        """
        self.active = False


class Game:
    """Bacis game class main menu.
    """
    def __init__(self, main_place):
        self.current = main_place
<<<<<<< HEAD
        self.current.activate()
        self.menues = []
        self.running = True
=======
        self.menues = []
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

    def add_menu(self, menu):
        """Adds menu to game.
        """
        self.menues.append(menu)

<<<<<<< HEAD
    def blit(self):
        """Blits game current menu.
        """
        if self.running:
            for menu in self.menues:
                if self.current in menu.places:
                    menu.blit()
=======
    def blit(self, event_get):
        """Blits game current menu.
        """
        for menu in self.menues:
            if self.current in menu.places:
                menu.blit(event_get)
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

    def change(self, new):
        """Change game current menu.
        """
<<<<<<< HEAD
        self.current.deactivate()
        self.current = new
        self.current.activate()

    def run(self):
        """Returns is game still running.
        """
        return self.running

    def kill(self):
        """Ends game running.
        """
        self.running = False


class Hyper_game:
    """Game for easy places controlling.
    """
=======
        self.current = new


class Hyper_game:
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
    def __init__(self):
        self.places = []
        self.menues = []
        self.index = 0

    def add_menu(self, menu):
        """Adds menu to game.
        """
        self.menues.append(menu)
        self.places.append(PLACE())

<<<<<<< HEAD
    def blit(self):
        """Blits game current menu.
        """
        self.menues[self.index].blit()
=======
    def blit(self, event_get):
        """Blits game current menu.
        """
        self.menues[self.index].blit(event_get)
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

    def set_menu(self, menu):
        """Sets game current menu.
        """
        for pos, Menu in self.menues:
            if Menu == menu:
                self.index = pos


<<<<<<< HEAD
class Keyboard:
    """Bacis keyboard class.
    """
    def __init__(self, definer):
        self.definer = definer
        self.new_definer = {}
        self.keys = {}
        for event, ac in self.definer:
            self.new_definer[event] = ac
            self.keys[ac] = 0
        self.definer = self.new_definer

    def __getitem__(self, index):
        return self.keys[index]

    def extend(self, extension):
        """Extends keyboard definer.
        """
        self.ext = extension
        for event, ac in self.ext:
            self.new_definer[event] = ac
            self.keys[ac] = 0

    def update(self):
        """Updates keyboard.*
        """
        for K in self.keys:
            if self.keys[K] == 1:
                self.keys[K] = 2
            elif self.keys[K] == 3:
                self.keys[K] = 0

        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key in self.definer:
                    if type(self.definer[event.key]) == list:
                        for x in self.definer[event.key]:
                            if event.type == pygame.KEYDOWN:
                                self.keys[x] = 1
                            elif event.type == pygame.KEYUP:
                                self.keys[x] = 3
                    else:
                        if event.type == pygame.KEYDOWN:
                            self.keys[self.definer[event.key]] = 1
                        elif event.type == pygame.KEYUP:
                            self.keys[self.definer[event.key]] = 3


class Main_menu:
    """Basic menu class.
    """
    def __init__(self, places, distance, *options, off=(0, 0),  # lint:ok
        off_type='pixel', keyboard=Keyboard(ARROWS+HIT)):
=======
class Main_menu:
    """Basic menu class."""
    def __init__(self, places, distance, *options, off=(0, 0),  # lint:ok
        off_type='pixel', keyboard=ARROWS, hit=HIT):
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.places = places
        if type(self.places) != list:
            self.places = [self.places]
        self.distance = distance
        self.screen = pygame.display.get_surface()
        self.screen_w, self.screen_h = self.screen.get_size()
        self.options = list(options)
        self.off = off
        self.off_type = off_type
        self.keyboard = keyboard
<<<<<<< HEAD
=======
        if self.keyboard:
            self.up = [i[0] for i in self.keyboard]
            self.down = [i[1] for i in self.keyboard]
        self.hit = hit
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.center = (self.screen.get_size()[0] / 2, self.screen.
        get_size()[1] / 2)
        if self.off_type == 'pixel':
            self.center = (self.center[0] + self.off[0], self.center[1] +
            self.off[1])
<<<<<<< HEAD
        if self.off_type in ('percent', '%'):
=======
        if self.off_type in ['percent', '%']:
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
            self.center = (self.center[0] + self.screen_w * self.off[0] /
            100, self.center[1] + self.screen_h * self.off[1] / 100)

    def __repr__(self):
        fin = "Menu object:\n"
        fin += "at " + str(self.center) + "(center),\n"
        fin += "with " + str(len(self.options)) + " option" + "s" * (not
        len(self.options) == 1) + ",\n"
        try:
            fin += "index at option " + str(self.index)
        except:
            fin += "no index currently"
        return fin

    def add_option(self, option, seted_option=False):
<<<<<<< HEAD
        """Adds new option to menu.
        """
=======
        """Adds new option to menu."""
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.options.append(option)
        if seted_option:
            self.current = option

    def set_options(self):
<<<<<<< HEAD
        """Should be executed on the end of options adding.
        """
=======
        """Should be executed on the end of options adding."""
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.first_y = self.center[1] - (len(self.options) - 1) / 2 *\
        self.distance
        for pos, opt in enumerate(self.options):
            opt.set_position(self.center[0], self.first_y + pos *
            self.distance)
            if opt == self.current:
                self.index = pos
        self.current.bold()

    def set_game(self, game):
        """Sets menu to given game.
        """
        self.game = game
        self.game.add_menu(self)

<<<<<<< HEAD
    def blit(self):
        """Blits menu.
        """
        self.keyboard.update()
        if self.keyboard["up"] == 1:
            self.current.un_bold()
            self.index -= 1
            self.index %= len(self.options)
            self.current = self.options[self.index]
            self.current.bold()
        elif self.keyboard["down"] == 1:
            self.current.un_bold()
            self.index += 1
            self.index %= len(self.options)
            self.current = self.options[self.index]
            self.current.bold()
        if self.keyboard["hit"] == 1:
            self.current.hit()

        for opt in self.options:
            opt.blit()

    def get_keyboard(self):
        """Returns game menu keyboard.
        """
        return self.keyboard

    def reset(self, *rest):
        """Turns on all options in Main Menu
        """

=======
    def blit(self, event_get):
        """Blits menu.
        """
        self.event_get = event_get
        for event in event_get:
            if event.type == pygame.KEYDOWN:
                if self.keyboard:
                    if event.key in self.up:
                        self.current.un_bold()
                        self.index -= 1
                        if self.index < 0:
                            self.index = len(self.options) - 1
                        self.current = self.options[self.index]
                        self.current.bold()
                    if event.key in self.down:
                        self.current.un_bold()
                        self.index += 1
                        if self.index > len(self.options) - 1:
                            self.index = 0
                        self.current = self.options[self.index]
                        self.current.bold()
                if event.key in self.hit:
                    self.current.hit()
        for opt in self.options:
            opt.blit()

>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

class option:
    """Bacis menu option class.
    """
    def __init__(self, image, menu, do1=useless, do2=useless, time=0,
        pos_do=useless,
        anti_pos_do=useless, infinity=0, proces=2):
        self.image = image
        self.x2, self.y2 = self.image.get_size()
        self.menu = menu
        self.do1 = do1
        self.do2 = do2
        self.time = time
        self.pos_do = pos_do
        self.anti_pos_do = anti_pos_do
        self.infinity = infinity
        self.proces = proces

    def __repr__(self):
        return "option object @" + str(self.x1) + ", " + str(self.y1)

    def set_position(self, x, y):
        """Sets option's position.*
        """
        self.x1 = x - self.x2 / 2
        self.y1 = y - self.y2 / 2
        self.pusher = pusher(self.x1, self.y1, self.image, self.menu,
        self.do1, self.do2, self.time, self.pos_do, self.anti_pos_do,
        self.infinity, self.proces)

    def blit(self):
        """Blits option.*
        """
        self.pusher.blit()

    def hit(self):
        """Executed when menu index is on option and when space is pressed.*
        """
        self.pusher.hit()

    def bold(self):
        """Executed when menu index comes on option.*
        """
        self.pusher.bold()

    def un_bold(self):
        """Executed when menu index comes out of option.*
        """
        self.pusher.un_bold()


class pusher:
    """Bacis independed option class (mostly used in option class).*
    """
    def __init__(self, x1, y1, image, obj, do1=None, do2=None, time=0,
        pos_do=None, anti_pos_do=None, infinity=0, proces=2):
        self.x1, self.y1 = x1, y1
        self.image = image
        self.x2, self.y2 = self.image.get_size()
        self.obj = obj
        self.do1 = do1
        self.do2 = do2
        self.time = time
        self.proces = proces
        self.pos_do = pos_do
        self.anti_pos_do = anti_pos_do
        self.infinity = infinity

    def blit(self):
        """Blits pusher.*
        """
        if self.proces > 0:
            self.obj.screen.blit(self.image, (self.x1, self.y1))
        if self.proces == 1:
            if pygame.time.get_ticks() - self.t > self.time:
                self.do2(self.obj, self)
                if self.infinity < 1:
                    self.proces = 0
                else:
                    self.recall()

    def hit(self):
        """Executed when menu index is on option and when space is pressed.*
        """
        if self.proces == 2:
            self.t = pygame.time.get_ticks()
            if self.infinity < 2:
                self.proces = 1
            self.do1(self.obj, self)

    def bold(self):
        """Executed when menu index comes on option.*
        """
        self.pos_do(self.obj, self)

    def un_bold(self):
        """Executed when menu index comes out of option.*
        """
        self.anti_pos_do(self.obj, self)


class text_option(option):
    """Textual menu option class(subclass of option).
    """
    def __init__(self, font, text, color, menu, do1=useless, do2=useless,
        time=0, pos_do=useless,
        anti_pos_do=useless, infinity=0, proces=2):
        self.font = font
        self.text = text
        self.color = color
        super().__init__(self.font.render(self.text, True, self.color),
        menu, do1, do2, time, pos_do, anti_pos_do, infinity, proces)

    def set_position(self, x, y):
        """Sets option's position.*
        """
        self.center = (x, y)
        super().set_position(x, y)
        self.pusher = text_pusher(self.x1, self.y1, self.font, self.text,
        self.color, self.menu, self.do1, self.do2, self.time, self.pos_do,
        self.anti_pos_do, self.infinity, self.proces)

    def blit(self):
        """Blits option.*
        """
        super().blit()
        if not equal(self.image, self.pusher.image):
            self.image = self.pusher.image
            self.x2, self.y2 = self.image.get_size()
            self.set_position(*self.center)


class text_pusher(pusher):
    """Textual independed option class (mostly used in text_option class,
<<<<<<< HEAD
    subclass of pusher).*
    """
=======
    subclass of pusher).*"""
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
    def __init__(self, x1, y1, font, text, color, obj, do1, do2, time,
        pos_do, anti_pos_do, infinity, proces):
        self.font = font
        self.text = text
        self.color = color
        super().__init__(x1, y1, self.font.render(self.text, True,
        self.color), obj, do1, do2, time, pos_do, anti_pos_do, infinity,
        proces)

    def update(self):
<<<<<<< HEAD
        """Updates pusher.*
        """
=======
        """Updates pusher.*"""
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.image = self.font.render(self.text, True, self.color)
