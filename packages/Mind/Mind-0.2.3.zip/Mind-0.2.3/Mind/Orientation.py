"""
Part of library for maps and points in map.
"""

imported_tiled = True
try:
    import tiledtmxloader
except ImportError:
    imported_tiled = False
<<<<<<< HEAD
import math
=======
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538


class MapError(Exception):
    """Exception for points outside the map.*
    """
<<<<<<< HEAD
=======

>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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
<<<<<<< HEAD
=======

>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []

    def __repr__(self):
        if self.objects:
<<<<<<< HEAD
            self.fin = 'Map ' + str(self.width) + "x" + str(self.height) + ":\n"
=======
            self.fin = ''
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
            self.count = 1
            for obj in self.objects:
                self.fin += str(self.count) + '. ' + str(obj) + '\n'
                self.count += 1
            return self.fin[:-1]
        else:
<<<<<<< HEAD
            return "Empty Map " + str(self.width) + "x" + str(self.height) + ":"
=======
            return 'Empty map'
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

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
<<<<<<< HEAD
    blits = False

    def __init__(self, x, y, Map, description='Unknown', quiet=False):
=======

    def __init__(self, x, y, Map, description='Unknown'):
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.x = x
        self.y = y
        self.Map = Map
        self.description = description
<<<<<<< HEAD
        if not quiet:
            self.Map.add_obj(self)
        self.name = self.description
=======
        self.Map.add_obj(self)
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

    def __tmx_init__(x, y, width, height, Map, name):
        if name:
            return point(x, y, Map, name)
        else:
            return point(x, y, Map)

<<<<<<< HEAD
    def __tmx_a_init__(x, y, width, height, Map, name, **prop):
        return ext_obj(point.__tmx_init__(x, y, width, height, Map, name), **prop)

    def __str__(self):
        return self.description + ' @ ' + str(self.x) + ', ' + str(self.y)

    __repr__ = __str__

    def distance(self, other):
        """Calculates distance between this and given point.
        """
        self.other = other
        return math.sqrt(abs(self.x - other.x) ** 2 + abs(self.y - other.y) ** 2)

    def get_xy(self):
        """Returns point's x and y.
        """
        return (self.x, self.y)


class line:
    """Basic line class.
    """
    blits = False

    def __init__(self, points, Map, description='Unknown', quiet=False, from_line_seg=False):
        self.points = points
        if from_line_seg:
            self.segment = from_line_seg
        else:
            self.segment = line_seg(self.points, Map, quiet=True, from_line=self)
        self.Map = Map
        self.description = description
        if not quiet:
            self.Map.add_obj(self)
        self.dif = self.x_dif, self.y_dif = self.segment.dif
        self.name = self.description
        self.cof = self.segment.cof

    def __str__(self):
        return self.description + ' line (' + str(self.points[0]) + ', ' + str(self.points[1]) + ')'

    __repr__ = __str__

    def __contains__(self, other):
        self.other = other
        if type(self.other) == point:
            if self.other in self.points:
                return True
            self.l = line((self.points[0], self.other), Map, quiet=True)
            if self.l.cof == self.cof:
                return True
        if type(self.other) == group_of_points:
            for P in self.other.points:
                if not P in self:
                    return False
            return True
        return False

    def get_angle(self):
        """Returns line anlge.
        """
        return self.segment.get_angle()
            


class line_seg:
    """Bacis line segment class.
    """
    blits = False

    def __init__(self, points, Map, description='Unknown', quiet=False, from_line=False):
        self.points = points
        self.Map = Map
        self.description = description
        if not quiet:
            self.Map.add_obj(self)
        self.name = self.description
        self.dif = self.x_dif, self.y_dif = (abs(self.points[0].x -
        self.points[1].x), abs(self.points[0].y - self.points[1].y))
        if self.y_dif == 0:
            self.cof = "horizontal"
        else:
            self.cof = self.x_dif / self.y_dif
        if from_line:
            self.line = from_line
        else:
            self.line = line(self.points, self.Map, quiet=True, from_line_seg=self)

    def __len__(self):
        return int(self.points[0].distance(self.points[1]))

    def __str__(self):
        return self.description + ' line segment (' + str(self.points[0]) + ', ' + str(self.points[1]) + ')'

    __repr__ = __str__

    def __contains__(self, P):
        self.P = P
        if self.P in self.points:
            return True
        self.l = line((self.points[0], self.P), Map, quiet=True)
        if self.l.cof == self.cof:
            if self.cof == "horizontal":
                if self.points[0].y > self.points[1].y:
                    if self.points[0].y > self.P.y > self.points[1].y:
                        return True
                else:
                    if self.points[0].y < self.P.y < self.points[1].y:
                        return True
            else:
                if (self.points[0].y > self.P.y > self.points[1].y or
                self.points[0].y < self.P.y < self.points[1].y) and\
                (self.points[0].x > self.P.x > self.points[1].x or
                self.points[0].x < self.P.x < self.points[1].x):
                    return True
        return False

    def get_angle(self):
        """Returns line rotation (0 vertical, 90 horizontal) in range 0 - 180.
        """
        if self.cof == "horizontal":
            return 90.0
        return math.degrees(math.atan(self.x_dif/self.y_dif))


def q_points(x1, y1, x2, y2, Map):
    """Returns points for line and line_seg.
    """
    p1 = point(x1, y1, Map, quiet=True)
    p2 = point(x2, y2, Map, quiet=True)
    return (p1, p2)


class ray:
    """Basic ray class.
    """
    blits = False

    def __init__(self, start_p, some_p, Map, description='Unknown', quiet=False):
        self.start_p = start_p
        self.some_p = some_p
        self.line = line((self.start_p, self.some_p), Map, quiet=True, from_line_seg=True)
        self.line_seg = self.line.segment
        self.Map = Map
        if not quiet:
            self.Map.add_obj(self)
        self.description = description
        self.name = self.description
        self.dif = self.x_dif, self.y_dif = (abs(self.start_p.x -
        self.some_p.x), abs(self.start_p.y - self.some_p.y))
        if self.y_dif == 0:
            self.cof = "horizontal"
        else:
            self.cof = self.x_dif / self.y_dif

    def __contains__(self, other):
        self.other = other
        if self.other == self.start_p:
            return True
        self.l = line((self.start_p, self.other), Map, quiet=True)
        if self.l.cof == self.cof:
            if self.cof == "horizontal":
                if self.start_p.y > self.some_p.y:
                    if self.start_p.y > self.P.y:
                        return True
                else:
                    if self.start_p.y < self.P.y:
                        return True
            else:
                if ((self.start_p.y > self.other.y and self.start_p > self.some_p)  or
                (self.start_p.y < self.other.y and self.start_p.y < self.some_p.y)) and\
                ((self.start_p.x > self.other.x and self.start_p > self.some_p) or
                (self.start_p.x < self.P.x and self.start_p > self.some_p)):
                    return True
        return False



class direction:
    """Bacis direction class.
    """
    blits = False

    def __init__(self, point, angle, Map, description='Unknown', quiet=False):
        self.angle = angle
        self.rd = math.radians(self.angle)
        self.point = point
        self.description = description
        self.Map = Map
        if not quiet:
            self.Map.add_obj(self)

    def __str__(self):
        return self.description + " direction @" + str(self.point.x) + ", " + str(self.point.y) + "; angle: " + str(self.angle)

    __repr__ = __str__

    def get_pos(self, distance):
        """Gets point of direction with given distance.
        """
        self.distance = distance
        if self.angle == 0:
            return point(self.point.x, self.point.y - self.distance, self.Map, quiet=True)
        else:
            self.x = math.sin(self.rd) * self.distance
            self.y = math.cos(self.rd) * self.distance
            return point(self.point.x + self.x, self.point.y - self.y, self.Map, quiet=True)

    def move(self, distance):
        """'Moves' directions point.
        """
        self.point.x, self.point.y = self.get_pos(distance).get_xy()

    def set_angle(self, angle):
        """Sets new angle.
        """
        self.angle = angle
        self.rd = math.radians(self.angle)

    def get_angle(self):
        """Returns direction angle.
        """
        return self.angle

    def ch_angle(self, change):
        """Changes angle for given value.
        """
        self.angle += change
        self.rd = math.radians(self.angle)

=======
    def __str__(self):
        return self.description + ' @ ' + str(self.x) + ', ' + str(self.y)

>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

class group_of_points:
    """Class for group of points.
    """
<<<<<<< HEAD
    blits = False

    def __init__(self, Map, description='Unknown', *points, quiet=False):
=======

    def __init__(self, Map, description='Unknown', *points):
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.Map = Map
        self.description = description
        self.points = points
        self.counter = 0
<<<<<<< HEAD
        if not quiet:
            self.Map.add_obj(self)
        self.name = self.description
=======
        for x in range(len(self.Map.objects)):
            if self.Map.objects[x - self.counter] in self.points:
                del self.Map.objects[x - self.counter]
                self.counter += 1
        self.Map.add_obj(self)
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

    def __str__(self):
        self.fin = self.description + ' group ['
        for Point in self.points:
            self.fin += str(Point) + '; '
        self.fin = self.fin[:-2] + ']'
        return self.fin

<<<<<<< HEAD
    __repr__ = __str__

=======
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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
<<<<<<< HEAD
    blits = False

    def __init__(self, x, y, width, height, Map, description='Unknown', quiet=False):
=======

    def __init__(self, x, y, width, height, Map, description='Unknown'):
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.Map = Map
<<<<<<< HEAD
        if not quiet:
            self.Map.add_obj(self)
        self.description = description
        self.name = self.description

    def __str__(self):
        return self.description + ' rect ' + str(self.width) + 'X' + \
        str(self.height) + ' @ ' + str(self.x) + ', ' + str(self.y)

    __repr__ = __str__

=======
        self.Map.add_obj(self)
        self.description = description

    def __repr__(self):
        return self.description + ' rect ' + str(self.width) + 'X' + \
        str(self.height) + ' @ ' + str(self.x) + ', ' + str(self.y)

>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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

<<<<<<< HEAD
    def collide(self, other):
        """Tests colliding with given rect.
        """
        self.fin = [0, 0, 0, 0]
        if self.y + self.height > other.y and self.y < other.y + other.height:
            if other.x + other.width > self.x + self.width > other.x:
                self.fin[0] = self.x + self.width - other.x
            if self.x + self.width > other.x + other.width > self.x:
                self.fin[2] = other.x + other.width - self.x
        if self.x + self.width > other.x and self.x < other.x + other.width:
            if other.y + other.height > self.y + self.height > other.y:
                self.fin[1] = self.y + self.height - other.y
            if self.y + self.height > other.y + other.height > self.y:
                self.fin[3] = other.y + other.height - self.y
        return self.fin

    def touch(self, other):
        """Tests touching with other rect.
        """
        self.fin = [False, False, False, False]
        if self.y + self.height > other.y and self.y < other.y + other.height:
            if self.x + self.width == other.x:
                self.fin[0] = True
            if other.x + other.width == self.x:
                self.fin[2] = True
        if self.x + self.width > other.x and self.x < other.x + other.width:
            if self.y + self.height == other.y:
                self.fin[1] =  True
            if other.y + other.height == self.y:
                self.fin[3] = True
        return self.fin


class ext_obj:
    """Extended object class.
    """
    blits = False

    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        self.prop1 = args
        self.prop2 = kwargs
        self.obj.Map.add_obj(self)

    def __str__(self):
        self.fin = str(self.obj)
        if self.prop1:
            self.fin += '; ['
            for prop in self.prop1:
                self.fin += str(prop)
                self.fin += ', '
            self.fin = self.fin[:-2]
            self.fin += ']'
        if self.prop2:
            self.fin += '; {'
            for prop in self.prop2:
                self.fin += str(prop)
                self.fin += ': '
                self.fin += str(self.prop2[prop])
                self.fin += ', '
            self.fin = self.fin[:-2]
            self.fin += '}'
        return self.fin

    __repr__ = __str__

=======
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
if imported_tiled:

    class tiled_map:
        """Class for map in tiled.
        """

<<<<<<< HEAD
        def __init__(self, name, r_decoder={"p": point}, a_decoder={"P": point}):
            self.name = name
            self.r_decoder = r_decoder
            self.a_decoder = a_decoder
=======
        def __init__(self, name, decoder={"p": point}):
            self.name = name
            self.decoder = decoder
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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
<<<<<<< HEAD
                        if obj.type in self.r_decoder:
                            self.objects.append(self.r_decoder[obj.type].__tmx_init__(obj.x, obj.y,
                            obj.width, obj.height, self.in_map, obj.name))
                        elif obj.type in self.a_decoder:
                            self.objects.append(self.r_decoder[obj.type].__tmx_a_init__(obj.x, obj.y,
                            obj.width, obj.height, self.in_map, obj.name, obj.type, obj.properties))
                        else:
                            if obj.name:
                                self.objects.append(ext_obj(rect(obj.x, obj.y,
                                obj.width, obj.height, self.in_map, obj.name, quiet=True), type=obj.type, **obj.properties))
                            else:
                                self.objects.append(ext_obj(rect(obj.x, obj.y,
                                obj.width, obj.height, self.in_map, quiet=True), type=obj.type, **obj.properties))
=======
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
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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

<<<<<<< HEAD
            for obj in self.objects:
                if obj.blits:
                    obj.blit()

        def clone_obj(self, key, key_type="name"):
            self.final = []
            for obj in self.objects:
                if obj.name == key:
                    self.final.append(obj)
            if len(self.final) > 1:
                return self.final
            elif len(self.final) == 1:
                return self.final[0]
            else:
                return None

=======
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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
<<<<<<< HEAD
        blits = True

=======
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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
<<<<<<< HEAD
            self.Map.screen.blit(self.picture, self.get_blit())

        def get_blit(self):
            """Returns position on which picture would be blitted
            """
            return (self.x - self.Map.x + self.Map.screen_w / 2, self.y -
            self.Map.y + self.Map.screen_h / 2)
=======
            self.Map.screen.blit(self.picture, (self.x - self.Map.x +
            self.Map.screen_w / 2, self.y - self.Map.y + self.Map.screen_h
            / 2))
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538

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

<<<<<<< HEAD
        def __init__(self, name, x, y, screen, edge=True, decoder={"p": point}):
            super().__init__(name, decoder)
=======
        def __init__(self, name, x, y, screen, edge=True):
            super().__init__(name)
>>>>>>> 74a9ded4a2bfac97fa7f274ab3d2c2b42ef46538
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
