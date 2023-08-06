"""
Part of library for Main Menu.
"""

import pygame

ARROWS = [(pygame.K_UP, "up"), (pygame.K_DOWN, "down"), (pygame.K_LEFT,
"left"), (pygame.K_RIGHT, "right")]
"""List of keys (arrows) for Menu changing index.
"""
HIT = [(pygame.K_RETURN, "hit"), (pygame.K_SPACE, "hit")]
"""List of keys for Menu selecting option.
"""


def useless(*useless_args):
    """Function that doesn't do anything.
    """
    pass


def ch_image(new_image):
    """Returns function which changes pusher image.

    :param new_image: new image for option
    :type new_image: pygame.Surface
    :return: function
    """
    def function(obj, self):
        self.image = new_image
    return function


def ch_pos(off):
    """Returns function which changes pusher position.

    :param off: *x* and *y* change
    :type off: tuple of numbers
    :return: function
    """
    def function(obj, self):
        if obj.off_type == "pixel":
            self.x1 += off[0]
            self.y1 += off[1]
        else:
            self.x1 += obj.screen_w * off[0] / 100
            self.y1 += obj.screen_h * off[1] / 100
    return function


def ch_text(new_text, error=True):
    """Returns function which changes pusher text (only for text_pushers).

    :param str new_text: new text for pusher
    :param bool error: if ``True`` raises error if pusher isn't text_pusher
    :returns: function
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

    :param new_color: new color for pusher
    :type new_color: color-like tuple
    :param bool error: if ``True`` raises error if pusher isn't text_pusher
    :returns: function
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

    :param new_font: font for puhser to be changed
    :type new_font: pygame.font.Font
    :param bool error: if ``True`` raises error if pusher isn't text_pusher
    :returns: function
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


def reset(im=True, pos=True):
    """Returns function which resets pusher.

    :param bool im: if ``True`` resets image
    :param bool pos: if ``True`` resets position
    :returns: function
    """
    def function(obj, self):
        self.reset(im, pos)
    return function


def link(place):
    """Returns function which leads game to onother place.

    :param place: place for game current place
    :type place: :py:class:`PLACE`
    :returns: function
    """
    def function(obj, self):
        obj.game.change(place)
    return function


def Quit(obj, self):
    """Quits game.
    """
    obj.game.kill()


def joined(List):
    """Returns function which executes all function in a given list.

    :param list List: list of all functions which will be executed
    :returns: function
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

    :param bool active: place activity
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

    :param main_place: first place for game
    :type place: :py:class:`PLACE`
    """
    def __init__(self, main_place):
        self.current = main_place
        self.current.activate()
        self.menues = []
        self.running = True
        self.options = {}

    def add_menu(self, menu):
        """Adds menu to game.*
        """
        self.menues.append(menu)
        menu.define(**self.options)

    def blit(self):
        """Blits game current menu.
        """
        if self.running:
            for menu in self.menues:
                if self.current in menu.places:
                    menu.blit()

    def change(self, new):
        """Change game current place.

        :param new: new place which will be blitted
        :type new: :py:class:`PLACE`
        """
        self.current.deactivate()
        self.current = new
        self.current.activate()

    def define(self, **options):
        """Defines options parameters for all menues.

        :param options: option parameters for all menues (see :py:class:`Main_menu` and :py:class:`option`)
        """
        self.options = options
        for menu in self.menues:
            menu.define(**options)

    def declare(self, type=None, **options):
        """Defines menues parameters.

        :param type: type of all menues in game (None for will be defined later).
        :type type: type
        :param options: menu parameters (see :py:class:`Main_menu`)
        """
        self.type = type
        self.Options = options

    def get_from(self, prior=False, **rest):
        """Returns menu from game combining previously defined and rest arguments.

        :param bool prior: if ``True`` rest options are prefered otherwise previously defined are prefered.
        :param rest: menu parameters which aren't defined by :py:meth:`Game.declare`
        :returns: menu or any other type defined by *type* argument
        """
        self.opt = rest
        for x in self.Options:
            if not prior or not x in self.opt:
                self.opt[x] = self.Options[x]
        if "type" in self.opt:
            if prior or not self.type:
                t = self.opt["type"]
                del self.opt["type"]
                return t(**self.opt)
            else:
                del self.opt["type"]
        return self.type(**self.opt)

    def set_from(self, prior=False, **rest):
        """Like :py:meth:`get_from` but this function automatically sets menu for game menu.

        :param bool prior: if ``True`` rest options are prefered otherwise previously defined are prefered.
        :param rest: menu parameters which aren't defined by :py:meth:`Game.declare`
        :returns: menu or any other type defined by *type* argument
        """
        M = self.get_from(prior, **rest)
        M.set_game(self)
        return M

    def run(self):
        """Returns is game still running.

        :returns: ``True`` if game is running otherwise ``False``
        """
        return self.running

    def kill(self):
        """Ends game running.
        """
        self.running = False


class Hyper_game(Game):
    """Game for easy places controlling.
    """
    def __init__(self):
        self.places = []
        self.menues = []
        self.index = 0

    def add_menu(self, menu):
        """Adds menu to game.*
        """
        self.menues.append(menu)
        self.places.append(PLACE())

    def blit(self):
        """Blits game current menu.
        """
        self.menues[self.index].blit()

    def set_menu(self, menu):
        """Sets game current menu.

        :param menu: Menu which will be blitted
        :type menu: :py:class:`Main_menu`
        """
        for pos, Menu in self.menues:
            if Menu == menu:
                self.index = pos


class Keyboard:
    """Bacis keyboard class.

    :param definer: defines keyboard keys
    :type definer: list of tuples
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

        :param extension: defines new keyboard keys
        :type extension: list of tuples
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

    :param places: place/es on which will menu be blitted
    :type places: :py:class:`PLACE` or list of :py:class:`PLACE`
    :param int x_distance: x distance between each option
    :param int y_distance: y distance between each option
    :param options: menu options
    :type options: :py:class:`option`
    :param off: how *off* menu is (on relation to the center of screen)
    :type off: tuple of two ints
    :param str off_type: if 'pixel' *off* will be measured in pixels, if 'percent' (or '%') *off* will be measured in percent of screen
    :param keyboard: keyboard which will be used in menu
    :type keyboard: :py:class:`Keyboard`
    """
    def __init__(self, places, x_distance, y_distance, *options, off=(0, 0),  # lint:ok
        off_type='pixel', keyboard=Keyboard(ARROWS + HIT)):
        self.places = places
        if type(self.places) != list:
            self.places = [self.places]
        self.distance = x_distance, y_distance
        self.screen = pygame.display.get_surface()
        self.screen_w, self.screen_h = self.screen.get_size()
        self.options = list(options)
        self.off = off
        self.off_type = off_type
        self.keyboard = keyboard
        self.center = (self.screen.get_size()[0] / 2, self.screen.
        get_size()[1] / 2)
        if self.off_type == 'pixel':
            self.center = (self.center[0] + self.off[0], self.center[1] +
            self.off[1])
        if self.off_type in ('percent', '%'):
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
        """Adds new option to menu.

        :param option: option which will be added to menu
        :type option: :py:class:option
        :param bool seted_option: if ``True`` menu index will be on that option
        """
        self.options.append(option)
        if seted_option:
            self.current = option

    def set_options(self):
        """Should be executed on the end of options adding.
        """
        self.first_x = self.center[0] - (len(self.options) - 1) / 2 *\
        self.distance[0]
        self.first_y = self.center[1] - (len(self.options) - 1) / 2 *\
        self.distance[1]
        for pos, opt in enumerate(self.options):
            opt.set_position(self.first_x + pos * self.distance[0], self.first_y + pos *
            self.distance[1])
            if opt == self.current:
                self.index = pos
        self.current.bold()

    def define(self, type=None, **options):
        """Defines options parameters.

        :param type: type of option
        :type type: type
        :param options: arguments for options
        """
        self.type = type
        self.Options = options
        self.Options["menu"] = self

    def get_from(self, prior=False, **rest):
        """Returns option from menu combining previously defined and rest arguments.

        :param bool prior: if ``True`` rest options are prefered otherwise previously defined are prefered.
        :param rest: option parameters which aren't defined by :py:meth:`Main_menu.define`
        :returns: option or any other type defined by *type* argument
        """
        self.opt = rest
        for x in self.Options:
            if not prior or not x in self.opt:
                self.opt[x] = self.Options[x]
        if "type" in self.opt:
            if prior or not self.type:
                t = self.opt["type"]
                del self.opt["type"]
                return t(**self.opt)
            else:
                del self.opt["type"]
        return self.type(**self.opt)

    def set_from(self, seted_option=False, prior=False, **rest):
        """Sets option to menu.

        :param bool seted_option: if ``True`` menu index will be on that option
        :param bool prior: if ``True`` rest options are prefered otherwise previously defined are prefered.
        :param rest: option parameters which aren't defined by :py:meth:`Main_menu.define`
        """
        self.add_option(self.get_from(prior, **rest), seted_option)

    def set_game(self, game):
        """Sets menu to given game.

        :param game: game which will be added to menu
        :type game: :py:class:`Game`
        """
        self.game = game
        self.game.add_menu(self)

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

        :returns: menu keyboard
        :rtype: :py:class:`Keyboard`
        """
        return self.keyboard

    def reset(self, *rest):
        """Turns on all options in Main Menu.

        :param rest: unimportant parameter.
        """
        for opt in self.options:
            opt.proces = 2


def Vertical_menu(places, distance, *options, off=(0, 0),  # lint:ok
    off_type='pixel', keyboard=Keyboard(ARROWS + HIT)):
    """Returns menu which is vertical.

    :param places: place/es on which will menu be blitted
    :type places: :py:class:`PLACE` or list of :py:class:`PLACE`
    :param int distance: distance between each option
    :param options: menu options
    :type options: :py:class:`option`
    :param off: how *off* menu is (on relation to the center of screen)
    :type off: tuple of two ints
    :param str off_type: if 'pixel' *off* will be measured in pixels, if 'percent' (or '%') *off* will be measured in percent of screen
    :param keyboard: keyboard which will be used in menu
    :type keyboard: :py:class:`Keyboard`
    """
    return Main_menu(places, 0, distance, *options, off=off, off_type=off_type, keyboard=keyboard)


def Horizontal_menu(places, distance, *options, off=(0, 0),  # lint:ok
    off_type='pixel', keyboard=Keyboard(ARROWS + HIT)):
    """Returns menu which is horizontal.

    :param places: place/es on which will menu be blitted
    :type places: :py:class:`PLACE` or list of :py:class:`PLACE`
    :param int distance: distance between each option
    :param options: menu options
    :type options: :py:class:`option`
    :param off: how *off* menu is (on relation to the center of screen)
    :type off: tuple of two ints
    :param str off_type: if 'pixel' *off* will be measured in pixels, if 'percent' (or '%') *off* will be measured in percent of screen
    :param keyboard: keyboard which will be used in menu
    :type keyboard: :py:class:`Keyboard`
    """
    return Main_menu(places, distance, 0, *options, off=off, off_type=off_type, keyboard=keyboard)


class option:
    """Bacis menu option class.

    :param image: option image
    :type image: pygame.Surface
    :param menu: option menu
    :type menu: :py:class:`Main_menu`
    :param function do: what happens when option is activated
    :param function pos_do: what happens when index comes to option
    :param function anti_pos_do: what happens when index to another option
    """
    def __init__(self, image, menu, do=useless, pos_do=useless,
        anti_pos_do=useless):
        self.image = image
        self.x2, self.y2 = self.image.get_size()
        self.menu = menu
        self.do = do
        self.pos_do = pos_do
        self.anti_pos_do = anti_pos_do

    def __repr__(self):
        return "option object @" + str(self.x1) + ", " + str(self.y1)

    def set_position(self, x, y):
        """Sets option's position.*
        """
        self.x1 = x - self.x2 / 2
        self.y1 = y - self.y2 / 2
        self.pusher = pusher(self.x1, self.y1, self.image, self.menu,
        self.do, self.pos_do, self.anti_pos_do)

    def blit(self):
        """Blits option.*
        """
        self.pusher.blit()

    def hit(self):
        """
        Executed when menu index is on option and when space ispressed.*
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
    def __init__(self, x1, y1, image, obj, do=None, pos_do=None, anti_pos_do=None):
        self.x1, self.y1 = self.sx, self.sy = x1, y1
        self.image = self.simage = image
        self.x2, self.y2 = self.image.get_size()
        self.obj = obj
        self.do = do
        self.pos_do = pos_do
        self.anti_pos_do = anti_pos_do

    def blit(self):
        """Blits pusher.*
        """
        self.obj.screen.blit(self.image, (self.x1, self.y1))

    def hit(self):
        """
        Executed when menu index is on option and when space is pressed.*
        """
        self.do(self.obj, self)

    def bold(self):
        """Executed when menu index comes on option.*
        """
        self.pos_do(self.obj, self)

    def un_bold(self):
        """Executed when menu index comes out of option.*
        """
        self.anti_pos_do(self.obj, self)

    def reset(self, im, pos):
        """Resets pusher.
        """
        if im:
            self.image = self.simage
            self.x2, self.y2 = self.image.get_size()
        if pos:
            self.x1, self.y1 = self.sx, self.sy


class text_option(option):
    """Textual menu option class(subclass of option).

    :param font: option font
    :type font: pygame.font.Font
    :param color: option color
    :type color: color-like tuple
    :param str text: option text
    :param menu: option menu
    :type menu: :py:class:`Main_menu`
    :param function do: what happens when option is activated
    :param function pos_do: what happens when index comes to option
    :param function anti_pos_do: what happens when index to another option
    """
    def __init__(self, font, text, color, menu, do=useless, pos_do=useless,
        anti_pos_do=useless):
        self.font = font
        self.text = text
        self.color = color
        super().__init__(self.font.render(self.text, True, self.color),
        menu, do, pos_do, anti_pos_do)

    def set_position(self, x, y):
        """Sets option's position.*
        """
        self.center = (x, y)
        super().set_position(x, y)
        self.pusher = text_pusher(self.x1, self.y1, self.font, self.text,
        self.color, self.menu, self.do, self.pos_do, self.anti_pos_do)

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
    subclass of pusher).*
    """
    def __init__(self, x1, y1, font, text, color, obj, do,
        pos_do, anti_pos_do):
        self.font = font
        self.text = text
        self.color = color
        super().__init__(x1, y1, self.font.render(self.text, True,
        self.color), obj, do, pos_do, anti_pos_do)

    def update(self):
        """Updates pusher.*
        """
        self.image = self.font.render(self.text, True, self.color)
