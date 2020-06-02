import numpy as np
import aifishes.config as cfg
import typing
import pygame as pg
from shapely.geometry import Polygon
from aifishes.environment.boid_vision import extract_boid_view
import math

def random_position():
    borders = cfg.borders()
    tolerance = cfg.environment()['border_tolerance']
    return pg.Vector2(
        scale(np.random.rand(), [0, 1], [tolerance, borders[0] - tolerance]),
        scale(np.random.rand(), [0, 1], [tolerance, borders[1] - tolerance])
    )


def random_velocity(magnitude):
    angle = scale(np.random.rand(), [0, 1], [0, 360])
    vec = pg.Vector2()
    vec.from_polar((magnitude, angle))
    return vec


def scale(value, old, new):
    return ((value - old[0]) / (old[1] - old[0])) * (new[1] - new[0]) + new[0]


X_AXIS_VEC = pg.Vector2(1, 0)
Y_AXIS_VEC = pg.Vector2(0, 1)
DEBUG_POSITION_COLOR = pg.Color('green')
SCREEN_WIDTH, SCREEN_HEIGHT = cfg.environment()['dim']


class Agent:
    def __init__(self, sprite: pg.Surface, position: pg.Vector2, velocity: pg.Vector2):
        self.original_sprite = sprite
        self.showable_sprite = None
        self.hitbox = None
        self.position = position
        self.velocity = velocity
        self.acceleration = pg.Vector2(0, 0)
        self.alive = True
        self.closest_target = None
        self.last_view = None
        self.current_view = None
        self.frame = 0
        self.learning = False
        self.reward = 0
        self.update_showable()

    def update_position(self, dtime):
        self.position += self.velocity * dtime

    def limit_velocity(self, min_limit=float('-inf'), max_limit=float('+inf')):
        magnitude = self.velocity.magnitude()
        if magnitude > max_limit:
            self.velocity = max_limit * self.velocity.normalize()
        if magnitude < min_limit:
            self.velocity = min_limit * self.velocity.normalize()

    def init_view(self):
        self.last_view = self.current_view = extract_boid_view(self.reaction_area(), self.position)

    def update_view(self):
        self.last_view = self.current_view
        self.current_view = extract_boid_view(
            self.reaction_area(), self.position)

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

    def update(self, dtime):
        self.update_velocity(dtime)
        self.limit_velocity()
        self.update_position(dtime)
        self.update_showable()
        self.frame += 1
        self.reward = 1

    def detect_target(self, surroundings):
        self.closest_target = self.choose_closest(surroundings)

    def choose_closest(self, surroundings):
        if len(surroundings) == 0:
            return None
        def distance(agent): 
           return math.sqrt((self.position.x - agent.position.x) **2 + (self.position.y - agent.position.y)**2)
        surroundings.sort(key=distance)        
        return surroundings[0]

    def update_showable(self):
        angle = self.velocity.angle_to(X_AXIS_VEC)
        self.showable_sprite = pg.transform.rotate(self.original_sprite, angle)

    def get_showable(self):
        return self.showable_sprite

    def safe_space(self):
        raise NotImplementedError()

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
        self.reward = -1000

    def steer_to_center(self):
        to_center = pg.Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2) - self.position
        # to_center.scale_to_length(self.velocity.length())
        self.velocity = self.velocity.lerp(to_center, 0.2) 