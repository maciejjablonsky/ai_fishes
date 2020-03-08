from math import sin, cos, sqrt, atan2



class Point:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def r(self):
        return sqrt(self._x * self._x + self._y * self._y)

    @property
    def phi(self):
        return atan2(self._y, self._x)

    @property
    def cartesian(self):
        return self.x, self.y

    def set_cartesian(self, x, y):
        self.x = x
        self.y = y

    @property
    def polar(self):
        return self.r, self.phi

    def set_polar(self, r, theta):
        self.x = r * cos(theta)
        self.y = r * sin(theta)

    def distance_to(self, point):
        return abs(self.r - point.r)

    def __add__(self, reposition):
        if type(reposition) is tuple:
            return Point(self.x + reposition[0], self.y + reposition[1])
        elif type(reposition) is Point:
            return Point(self.x + reposition.x, self.y + reposition.y)
        else:
            raise RuntimeError("Can't add {0:s} to Point instance.".format(str(type(reposition))))

    def __radd(self, reposition):
        return self.__add__(reposition)

    def __mul__(self, multiplier):
        return Point(self.x * multiplier, self.y * multiplier)

    def __eq__(self, other):
        if type(other) is tuple:
            return self.x == other[0] and self.y == other[1]
        elif type(self) is type(other):
            return self.x == other.x and self.y == other.y

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __sub__(self, other):
        if type(other) is Point:
            return self.__add__(-other)
        elif type(other) is tuple:
            return self.__add__(Point(-other[0], -other[1]))
        else:
            raise RuntimeError("Can't subtract {0:s} from Point instance.".format(str(type(other))))

    def __rsub__(self, other):
        if type(other) is Point:
            return self.__add__(-other)
        elif type(other) in [tuple, list]:
            return Point(other[0] - self.x, other[1] - self.y)

    def reflect_x(self, x=0):
        diff = x - self.x
        return Point(self.x + diff * 2, self.y)

    def reflect_y(self, y=0):
        diff = y - self.y
        return Point(self.x, self.y + diff * 2)

    def reflect(self, point=(0, 0)):
        if type(point) in [Point, tuple, list]:
            diff = point - self
            return self + diff * 2
        else:
            raise RuntimeError("Can't reflect Point from {0}.".format(str(type(point))))

    def __str__(self):
        return "{0}({1}, {2})".format(self.__class__.__name__, self.x, self.y)
