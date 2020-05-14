import numpy as np
import aifishes.config as cfg

from aifishes.agent import Agent, random_position, random_velocity
import pygame as pg

FISH_COLOR = pg.Color('chartreuse')
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


class Fish(Agent):
    def __init__(self):
        super().__init__(fish_sprite(), random_position(), random_velocity(cfg.fish_vel_start_magnitude()))

    def limit_velocity(self):
        limit = cfg.fish_vel_max_magnitude()
        return super().limit_velocity(limit=limit)
