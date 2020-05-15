import numpy as np
import aifishes.config as cfg
import typing
import pygame as pg
import scipy as scp
from shapely.geometry import Polygon


def random_position():
    borders = cfg.borders()
    return pg.Vector2(
        scale(np.random.rand(), [0, 1], [0, borders[0]]),
        scale(np.random.rand(), [0, 1], [0, borders[1]])
    )


def random_velocity(magnitude):
    angle = scale(np.random.rand(), [0, 1], [0, 360])
    vec = pg.Vector2()
    vec.from_polar((magnitude, angle))
    return vec


def scale(value, old, new):
    return (value / (old[1] - old[0])) * (new[1] - new[0]) + new[0]


X_AXIS_VEC = pg.Vector2(1, 0)
Y_AXIS_VEC = pg.Vector2(0, 1)
DEBUG_POSITION_COLOR = pg.Color('green')


class Agent:
    def __init__(self, sprite: pg.Surface, position: pg.Vector2, velocity: pg.Vector2):
        self.original_sprite = sprite
        self.showable_sprite = None
        self.hitbox = None
        self.position = position
        self.velocity = velocity
        self.acceleration = pg.Vector2(0, 0)
        self.alive = True

    def update_position(self, dtime):
        self.position += self.velocity * dtime

    def limit_velocity(self, limit=float('inf')):
        if self.velocity.length() > limit:
            self.velocity = limit * self.velocity.normalize()

    def update_velocity(self, dtime):
        self.velocity += self.acceleration * dtime

    def apply_force(self, acceleration: pg.Vector2):
        self.acceleration = acceleration

    def get_x(self):
        """Name must be 'get_x' for smartquadtree integration"""
        return self.position[0]

    def get_y(self):
        """Name must be 'get_y' for smartquadtree integration"""
        return self.position[1]

    def get_hitbox(self):
        # TODO implement hitbox
        raise NotImplementedError

    def update(self, dtime):
        self.update_velocity(dtime)
        self.limit_velocity()
        self.update_position(dtime)
        self.update_showable()

    def update_showable(self):
        angle = self.velocity.angle_to(X_AXIS_VEC)
        self.showable_sprite = pg.transform.rotate(self.original_sprite, angle)

    def get_showable(self):
        return self.showable_sprite

    def reaction_area(self):
        raise NotImplementedError()

    def get_hitbox(self):
        velocity_angle = X_AXIS_VEC.angle_to(self.velocity)
        return np.array([point.rotate(velocity_angle) + self.position for point in self.hitbox], dtype=np.float32)

    def collide(self, obj):
        obj_hitbox = Polygon(obj.get_hitbox())
        self_hitbox = Polygon(self.get_hitbox())
        return self_hitbox.intersects(obj_hitbox)

    def find_collisions(self, surroundings):
        collisions = []
        for obj in surroundings:
            if self.collide(obj):
                collisions.append(obj)
        return collisions

    def die(self):
        self.alive = False
