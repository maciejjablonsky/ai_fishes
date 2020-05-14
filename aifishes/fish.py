import numpy as np
import aifishes.config as cfg

from aifishes.agent import Agent, random_position, random_velocity
import pygame as pg

FISH_COLOR=pg.Color('chartreuse')

def create_fish_surface():
        dim = cfg.fish_dim()
        surf = pg.Surface(dim, pg.SRCALPHA)
        shape = np.array([[0, 0], [dim[0], 0.5 * dim[1]],[0, dim[1]]], dtype=np.float32)
        pg.gfxdraw.aapolygon(surf, shape, FISH_COLOR)
        pg.gfxdraw.filled_polygon(surf, shape, FISH_COLOR)
        return surf


fish_surface = create_fish_surface()

class Fish(Agent):
    def __init__(self):
        super().__init__(fish_surface,  random_position(), random_velocity())

    