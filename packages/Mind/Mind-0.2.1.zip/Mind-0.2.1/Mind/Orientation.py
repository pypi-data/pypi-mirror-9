"""
Part of library for maps and points in map.
"""

imported_tiled = True
try:
    import tiledtmxloader
except ImportError:
    imported_tiled = False


class MapError(Exception):
    """Exception for points outside the map.*
    """

    def __init__(self, x, y, max_x, max_y):
        self.x = x
        self.y = y
        self.max_x = max_x
        self.max_y = max_y

    def __str__(self):
        self.fin = ''
        if self.x > self.max_x:
            self.fin += 'x should be reduced by ' + str(self.x -
            self.max_x)
            if self.y > self.max_y:
                self.fin += ', '
        if self.y > self.max_y:
            self.fin += 'y should be reduced by ' + str(self.y -
            self.max_y)
        return self.fin


class MAP:
    """Bacis map class.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []

    def __repr__(self):
        if self.objects:
            self.fin = ''
            self.count = 1
            for obj in self.objects:
                self.fin += str(self.count) + '. ' + str(obj) + '\n'
                self.count += 1
            return self.fin[:-1]
        else:
            return 'Empty map'

    def __contains__(self, item):
        self.item = item
        return self.item in self.objects

    def __bool__(self):
        return bool(self.objects)

    def add_obj(self, obj):
        """Function that adds object(point, rect...) to map.
        """
        self.obj = obj
        if type(self.obj) == point:
            if self.obj.x > self.width or self.obj.y > self.height:
                raise MapError(obj.x, obj.y, self.width, self.height)
        self.objects.append(self.obj)

    def at(self, x, y):
        """Return generator of all items in map on x, y coordinates.
        """
        self.x = x
        self.y = y
        for obj in self.objects:
            if type(obj) == point:
                if obj.x == self.x and obj.y == self.y:
                    yield obj
            elif type(obj) == group_of_points:
                self.T = False
                for POINT in obj.at(self.x, self.y):
                    yield POINT
                    self.T = True
                if self.T:
                    yield obj
            elif type(obj) == rect:
                if obj.at(self.x, self.y):
                    yield obj


class point:
    """Basic point class.
    """

    def __init__(self, x, y, Map, description='Unknown'):
        self.x = x
        self.y = y
        self.Map = Map
        self.description = description
        self.Map.add_obj(self)

    def __tmx_init__(x, y, width, height, Map, name):
        if name:
            return point(x, y, Map, name)
        else:
            return point(x, y, Map)

    def __str__(self):
        return self.description + ' @ ' + str(self.x) + ', ' + str(self.y)


class group_of_points:
    """Class for group of points.
    """

    def __init__(self, Map, description='Unknown', *points):
        self.Map = Map
        self.description = description
        self.points = points
        self.counter = 0
        for x in range(len(self.Map.objects)):
            if self.Map.objects[x - self.counter] in self.points:
                del self.Map.objects[x - self.counter]
                self.counter += 1
        self.Map.add_obj(self)

    def __str__(self):
        self.fin = self.description + ' group ['
        for Point in self.points:
            self.fin += str(Point) + '; '
        self.fin = self.fin[:-2] + ']'
        return self.fin

    def at(self, x, y):
        """Return generator of all items in group on x, y coordinates.
        """
        self.x = x
        self.y = y
        for Point in self.points:
            if Point.x == self.x and Point.y == self.y:
                yield Point


class rect:
    """Bacis map rect class.
    """

    def __init__(self, x, y, width, height, Map, description='Unknown'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.Map = Map
        self.Map.add_obj(self)
        self.description = description

    def __repr__(self):
        return self.description + ' rect ' + str(self.width) + 'X' + \
        str(self.height) + ' @ ' + str(self.x) + ', ' + str(self.y)

    def __contains__(self, item):
        self.item = item
        if type(self.item) == point:
            if self.at(self.item.x, self.item.y):
                return True
        elif type(self.item) == group_of_points:
            for p in self.item.points:
                if not p in self:
                    return False
            return True
        elif type(self.item) == rect:
            if self.x <= self.item.x and self.y <= self.item.y and self.x \
            + self.width >= self.item.x + self.item.width and self.y + \
            self.height >= self.item.y + self.item.height:
                return True
            return False
        else:
            raise TypeError("'in <rect>' doesn't support " +
            repr(self.item))

    def at(self, x, y):
        """Test if point is in rect.*
        """
        return self.x + self.width >= x >= self.x and self.y + \
        self.height >= y >= self.y

if imported_tiled:

    class tiled_map:
        """Class for map in tiled.
        """

        def __init__(self, name, decoder={"p": point}):
            self.name = name
            self.decoder = decoder
            self.out_map = tiledtmxloader.tmxreader.TileMapParser().\
            parse_decode(self.name + '.tmx')
            self.out_objects = tiledtmxloader.helperspygame.\
            ResourceLoaderPygame()
            self.out_objects.load(self.out_map)
            self.renderer = tiledtmxloader.helperspygame.RendererPygame()
            self.layers = tiledtmxloader.helperspygame.\
            get_layers_from_map(self.out_objects)
            self.in_map = MAP(self.out_map.pixel_width,
            self.out_map.pixel_height)
            self.objects = []
            for layer in self.layers:
                if layer.is_object_group:
                    for obj in layer.objects:
                        if obj.type in decoder:
                            self.objects.append(self.decoder[obj.type].__tmx_init__(obj.x, obj.y,
                            obj.width, obj.height, self.in_map, obj.name))
                        else:
                            if obj.name:
                                self.objects.append(rect(obj.x, obj.y,
                                obj.width, obj.height, self.in_map, obj.name))
                            else:
                                self.objects.append(rect(obj.x, obj.y,
                                obj.width, obj.height, self.in_map))
            self.edge_width = self.in_map.width
            self.edge_height = self.in_map.height
            self.edge_x, self.edge_y = 0, 0

        def __repr__(self):
            return repr(self.in_map)

        def set_screen(self, screen):
            """Sets screen (pygame) on which will map be blited.
            """
            self.screen = screen
            self.screen_w, self.screen_h = self.screen.get_size()
            self.renderer.set_camera_position_and_size(0, 0, self.screen_w,
            self.screen_h)

        def set_camera_pos(self, x, y, edge=True):
            """Sets camera position (centre), if edge is True it won't be
            outside the map.
            """
            self.x = x
            self.y = y
            self.edge = edge
            if self.edge:
                self.x = max([self.edge_x + self.screen_w / 2, min([self.x,
                self.edge_width - self.screen_w / 2])])
                self.y = max([self.edge_y + self.screen_h / 2, min([self.y,
                self.edge_height - self.screen_h / 2])])
            self.renderer.set_camera_position(self.x, self.y)
            return (self.x, self.y)

        def get_camera_pos(self):
            """Returns camera position.
            """
            return (self.x, self.y)

        def blit(self):
            """Blits map (on seted screen).
            """
            for layer in self.layers:
                if not layer.is_object_group:
                    self.renderer.render_layer(self.screen, layer)

        def set_edge(self, width, height):
            """Sets edge of map.
            """
            self.edge_width = width
            self.edge_height = height

        def offset(self, x, y):
            """Sets how off map is.
            """
            self.edge_x = x
            self.edge_y = y

    class map_obj:
        """Basic Map object.
        """
        def __init__(self, x, y, Map, picture, name='Unknown'):
            self.x = x
            self.y = y
            self.Map = Map
            self.picture = picture
            self.name = name

        def __tmx_init__(x, y, width, height, Map, name):
            return map_obj(x, y, Map, None, name)

        def blit(self):
            """Blits object picture on Map screen.*
            """
            self.Map.screen.blit(self.picture, (self.x - self.Map.x +
            self.Map.screen_w / 2, self.y - self.Map.y + self.Map.screen_h
            / 2))

        def set_position(self, x, y):
            """Sets position of object.
            """
            self.x = x
            self.y = y

        def move(self, x, y):
            """Moves objetct.
            """
            self.x += x
            self.y += y

    class moving_map(tiled_map):
        """Map in which moving is very easy.
        """

        def __init__(self, name, x, y, screen, edge=True):
            super().__init__(name)
            self.set_screen(screen)
            self.X = x
            self.Y = y
            self.edge = edge
            self.set_camera_pos(self.X, self.Y, self.edge)

        def set_position(self, x, y):
            """Sets position of map 'center object'.
            """
            self.X = x
            self.Y = y
            self.set_camera_pos(self.X, self.Y, self.edge)

        def get_position(self):
            """Returns 'center object' position.
            """
            return (self.X, self.Y)

        def move(self, x, y):
            """Moves 'center object'.
            """
            self.X += x
            self.Y += y
            self.set_camera_pos(self.X, self.Y, self.edge)
