from .physics.point import Point
from .physics.velocity import Velocity
from random import randint
from math import radians
from .physics.area import Rectangle


def fish_from_json(fish_config, borders):
    return Fish(config=fish_config, borders=borders)


class Fish:
    def __init__(self, config=None, borders=None):
        if config is None:
            raise TypeError("Fish can be created only with config.json.")
        if config['coords']['random']:
            x = randint(config['coords']['min_x'],
                        config['coords']['max_x'])
            y = randint(config['coords']['min_y'],
                        config['coords']['max_y'])
        else:
            x = config['coords']['x']
            y = config['coords']['y']

        self.coords = Point(x, y)
        self.velocity = Velocity()
        self.velocity.set_polar(
            config['motion']['translational']['module_value'],
            radians(randint(0, 359)))
        self.borders: Rectangle = borders

    def reposition(self, dtime=0):
        return self.velocity.reposition(dtime)

    def move(self, dtime=0):
        reposition = self.reposition(dtime)
        next_position = self.coords + reposition
        if not self.borders.contains(next_position):
            next_position = self.dodge_borders(next_position)
        self.coords = next_position

    def dodge_borders(self, next_position):
        if next_position.x < 0:
            self.velocity = self.velocity.reflect_x()
            next_position = next_position.reflect_x()
        elif next_position.x > self.borders.right_bottom.x:
            self.velocity = self.velocity.reflect_x()
            next_position = next_position.reflect_x(self.borders.right_bottom.x)
        if next_position.y < 0:
            self.velocity = self.velocity.reflect_y()
            next_position = next_position.reflect_y()
        elif next_position.y > self.borders.right_bottom.y:
            self.velocity = self.velocity.reflect_y()
            next_position = next_position.reflect_y(self.borders.right_bottom.y)
        return next_position
