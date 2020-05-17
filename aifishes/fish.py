import numpy as np
import aifishes.config as cfg

from aifishes import agent
from aifishes.agent import Agent, random_position, random_velocity
import pygame as pg

FISH_COLOR = pg.Color('seashell2')
FISH_SPRITE = None


def fish_sprite():
    global FISH_SPRITE
    if FISH_SPRITE is None:
        dim = np.array(cfg.fish_dim())
        surf = pg.Surface(dim, pg.SRCALPHA)
        shape = np.array([[0, 0], [dim[0], 0.5 * dim[1]],[0, dim[1]]], dtype=np.float32)

        pg.gfxdraw.aapolygon(surf, shape, FISH_COLOR)
        pg.gfxdraw.filled_polygon(surf, shape, FISH_COLOR)
        FISH_SPRITE = surf
    return FISH_SPRITE

def fish_shape():
    w, h = cfg.fish()['dim']
    vec = pg.Vector2
    return [vec(-w/2, -h/2), vec(w/2, 0), vec(-w/2, h/2)]

class Fish(Agent):
    def __init__(self):
        super().__init__(fish_sprite(), random_position(), random_velocity(cfg.fish_vel_start_magnitude()))
        self.hitbox = fish_shape()

    def limit_velocity(self):
        limit = cfg.fish_vel_max_magnitude()
        return super().limit_velocity(limit=limit)

    def reaction_area(self):
        direction_angle = agent.X_AXIS_VEC.angle_to(self.velocity)     
        radius = cfg.fish()['reaction_radius']
        vis_angle = cfg.fish()['vision_angle']
        start = agent.scale(direction_angle - vis_angle/ 2, [0, 360], [0, 2*np.pi])
        end = agent.scale(direction_angle + vis_angle / 2, [0, 360], [0, 2*np.pi])
        t = np.linspace(start, end, dtype=np.float32)
        x = np.append(0, radius * np.cos(t))
        y = np.append(0, radius * np.sin(t))
        area = np.c_[x, y]
        return area + self.position

    def debug_print(self, screen:pg.Surface):
        pg.draw.circle(screen, agent.DEBUG_POSITION_COLOR, np.array(self.position, dtype=np.int32), 5)
        sprite_dim = pg.Vector2(self.showable_sprite.get_size())
        pg.draw.rect(screen, (0, 255, 0), pg.Rect(self.position - sprite_dim/2, sprite_dim), 2)
        pg.draw.polygon(screen, (0, 0, 0), self.reaction_area(), 2)

