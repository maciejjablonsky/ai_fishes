import numpy as np
import aifishes.config as cfg
from aifishes.agent import Agent, random_position, random_velocity
import pygame as pg

PREDATOR_COLOR = pg.Color('orangered1')
PREDATOR_SPRITE = None


def predator_sprite():
    global PREDATOR_SPRITE
    if PREDATOR_SPRITE is None:
        dim = np.array(cfg.predator_dim())
        surf = pg.Surface(dim, pg.SRCALPHA)
        shape = np.array([[0, 0], [dim[0], 0.5 * dim[1]],[0, dim[1]]], dtype=np.float32)
        pg.gfxdraw.aapolygon(surf, shape, PREDATOR_COLOR)
        pg.gfxdraw.filled_polygon(surf, shape, PREDATOR_COLOR)
        PREDATOR_SPRITE = surf
    return PREDATOR_SPRITE


class Predator(Agent):
    def __init__(self):
        super().__init__(predator_sprite(), random_position(), random_velocity(cfg.predator_vel_start_magnitude()))

    def limit_velocity(self):
        limit = cfg.predator_vel_max_magnitude()
        return super().limit_velocity(limit=limit)

    