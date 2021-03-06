import numpy as np
import aifishes.config as cfg

from aifishes.environment import agent
from aifishes.environment.agent import Agent, random_position, random_velocity
import pygame as pg
import math

FISH_COLOR = pg.Color('seashell2')
FISH_SPRITE = None


def fish_sprite():
    global FISH_SPRITE
    if FISH_SPRITE is None:
        w, h = np.array(cfg.fish()['dim'])
        surf = pg.Surface((w, h), pg.SRCALPHA)
        level_of_disability = 0.13
        left_x = np.array([0, 0.25, 0.5, 0], dtype=np.float32) * w
        left_y = np.array([0, 1 / 4 - level_of_disability, 7 / 8 - level_of_disability, 1], dtype=np.float32) * h
        middle_x = np.array([0.25, 0.5, 0.75, 0.5], dtype=np.float32) * w
        middle_y = np.array([1 / 4 - level_of_disability, 3 / 8 - level_of_disability, 3 / 4 - level_of_disability, 7 / 8 - level_of_disability], dtype=np.float32) * h
        right_x = np.array([0.5, 1, 0.75], dtype=np.float32) * w
        right_y = np.array([3 / 8 - level_of_disability, 0.5, 3 / 4 - level_of_disability], dtype=np.float32) * h
        pg.draw.line(surf, pg.Color('Black'), [0, 0], [2, 2])
        left = np.c_[left_x, left_y]
        middle = np.c_[middle_x, middle_y]
        right = np.c_[right_x, right_y]
        pg.gfxdraw.filled_polygon(surf, left, pg.Color('darkorange1'))
        pg.gfxdraw.filled_polygon(surf, middle, pg.Color('seashell2'))
        pg.gfxdraw.filled_polygon(surf, right, pg.Color('darkorange1'))
        if w >= 30 and h >= 10:
            pg.draw.aaline(surf, pg.Color('black'), [middle_x[0], middle_y[0]], [middle_x[3], middle_y[3]], int(w/30))
            pg.draw.aaline(surf, pg.Color('black'), [middle_x[1], middle_y[1]], [middle_x[2], middle_y[2]], int(w/30))
            eye = np.array([int(0.8 * w), int(0.48 * h)])
            pg.draw.circle(surf, pg.Color('black'), eye, int(w/30), int(w/30))
        # left = np.array([0,0],[0.25*w, 7*w])
        # shape = np.array([[0, 0], [dim[0], 0.5 * dim[1]],[0, dim[1]]], dtype=np.float32)

        # pg.gfxdraw.aapolygon(surf, shape, FISH_COLOR)
        # pg.gfxdraw.filled_polygon(surf, shape, FISH_COLOR)
        FISH_SPRITE = surf
    return FISH_SPRITE


def fish_shape():
    w, h = cfg.fish()['dim']
    vec = pg.Vector2
    return [vec(-w / 2, -h / 2), vec(w / 2, 0), vec(-w / 2, h / 2)]


class Fish(Agent):
    def __init__(self):
        super().__init__(fish_sprite(), random_position(), random_velocity(cfg.fish_vel_start_magnitude()), cfg.fish()['reaction_radius'])
        self.hitbox = fish_shape()

    def create_reaction_area(self):
        vision_angle = cfg.fish()['vision_angle']
        n = 8
        return super().create_reaction_area(vision_angle, n)

    def limit_velocity(self):
        min_limit = cfg.fish()['velocity']['min']
        max_limit = cfg.fish()['velocity']['max']
        return super().limit_velocity(min_limit=min_limit, max_limit=max_limit)

    def safe_space(self):
        direction_angle = agent.X_AXIS_VEC.angle_to(self.velocity)
        r = cfg.fish()['safe_distance']
        vis_angle = cfg.fish()['vision_angle']
        start = agent.scale(direction_angle - vis_angle / 2, [0, 360], [0, 2 * np.pi])
        end = agent.scale(direction_angle + vis_angle / 2, [0, 360], [0, 2 * np.pi])
        t = np.linspace(start, end, num=20, dtype=np.float32)
        x = np.append(0, r * np.cos(t))
        y = np.append(0, r * np.sin(t))
        area = np.c_[x, y]
        return area + self.position



    def debug_print(self, screen: pg.Surface):
        pg.draw.circle(screen, agent.DEBUG_POSITION_COLOR, np.array(self.position, dtype=np.int32), 5)
        sprite_dim = pg.Vector2(self.showable_sprite.get_size())
        pg.draw.rect(screen, (0, 255, 0), pg.Rect(self.position - sprite_dim / 2, sprite_dim), 2)
        pg.draw.polygon(screen, (0, 0, 0), self.reaction_area(), 2)
        if self.closest_target is not None:
            pg.draw.line(screen, pg.Color('gold1'), self.position, self.closest_target.position, 2)

