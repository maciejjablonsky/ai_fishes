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
        fish_config = config['fishes']['regular_fish']
        self.dimensions = (
            config['view']['textures']['regular_fish']['width'],
            config['view']['textures']['regular_fish']['height']
        )
        if fish_config['coords']['random']:
            x = randint(fish_config['coords']['min_x'],
                        int(round(fish_config['coords']['max_x'] - self.dimensions[0])))
            y = randint(fish_config['coords']['min_y'],
                        int(round(fish_config['coords']['max_y'] - self.dimensions[1])))
        else:
            x = fish_config['coords']['x']
            y = fish_config['coords']['y']

        self.coords = Point(x, y)
        self.velocity = Velocity()
        self.velocity.set_polar(
            fish_config['motion']['translational']['module_value'],
            radians(randint(0,359)))
        self.borders: Rectangle = borders


    def reposition(self, dtime=0):
        return self.velocity.reposition(dtime)

    def move(self, dtime=0):
        reposition = self.reposition(dtime)
        next_position = self.coords + reposition
        if not (self.borders.contains(next_position) and self.borders.contains(next_position + self.dimensions)):
            next_position = self.dodge_borders(next_position)
        self.coords = next_position

    def dodge_borders(self, next_position):
        width, height = self.dimensions
        if next_position.x < 0:
            self.velocity = self.velocity.reflect_x()
            next_position = next_position.reflect_x()
        elif next_position.x + width > self.borders.right_bottom.x:
            self.velocity = self.velocity.reflect_x()
            next_position = next_position.reflect_x((next_position.x + self.coords.x)/2)
        if next_position.y < 0:
            self.velocity = self.velocity.reflect_y()
            next_position = next_position.reflect_y()
        elif next_position.y + height > self.borders.right_bottom.y:
            self.velocity = self.velocity.reflect_y()
            next_position = next_position.reflect_y((next_position.y + self.coords.y)/2)
        return next_position
