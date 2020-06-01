'''This module combines boid vision preprocessing'''

import pygame as pg
from pygame.gfxdraw import textured_polygon
import torch
import aifishes.config as cfg
from shapely.geometry import Point, LineString, Polygon

screen_width, screen_height = cfg.environment()['dim']


def boid_reaction_area_surface(boid, frame: int) -> torch.Tensor:
    '''Cutting boid reaction area from game screen'''
    screen = pg.display.get_surface()
    vision_area = boid.reaction_area()

    for point in vision_area:
        if point[0] < 0:
            point[0] = 0
        elif point[0] >= screen_width:
            point[0] = screen_width
        if point[1] < 0:
            point[1] = 0
        elif point[1] >= screen_height:
            point[1] = screen_height
    position = boid.position
    radius = cfg.fish()['reaction_radius']

    left = int(max(0, round(position.x - radius)))
    up = int(max(0, round(position.y - radius)))
    right = int(min(screen.get_width() - 1, round(position.x + radius)))
    bottom = int(min(screen.get_height() - 1, round(position.y + radius)))
    bounding_box = pg.Rect(left, up, right - left, bottom - up)
    vision_surface = pg.Surface((radius * 2, radius * 2))
    clipped = vision_surface.copy()
    dest = (max(0, radius - position.x), max(0, radius - position.y))
    vision_surface.blit(screen,dest=dest, area=bounding_box)
    textured_polygon(clipped, vision_area - position + pg.Vector2(radius, radius), vision_surface, 0, 0)
    return pg.surfarray.pixels3d(clipped)
