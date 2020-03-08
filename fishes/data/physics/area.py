from fishes.data.physics.point import Point


def is_between(low, value, high):
    return low <= value <= high


class Rectangle:
    def __init__(self, left_upper=Point(0, 0), right_bottom=Point(0, 0)):
        self.left_upper = left_upper
        self.right_bottom = right_bottom

    def contains(self, point):
        if isinstance(point, Point):
            return is_between(self.left_upper.x, point.x, self.right_bottom.x) and is_between(self.left_upper.y,
                                                                                              point.y,
                                                                                              self.right_bottom.y)
        else:
            raise TypeError("Can't specify if instance of {0} is in Area.".format(str(type(point))))
