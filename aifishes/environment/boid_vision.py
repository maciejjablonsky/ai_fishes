'''This module combines boid vision preprocessing'''

import pygame as pg
from pygame.gfxdraw import textured_polygon
import torch
import aifishes.config as cfg
from shapely.geometry import Point, LineString, Polygon
import numpy as np
# from aifishes.dqn_vision.machine import DEVICE 
import torchvision.transforms as T
from PIL import Image
import aifishes.config as cfg
from skimage.measure import block_reduce

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def resize(image:np.ndarray):
    '''Resizes boid view to fit neural network input size'''
    r = cfg.dqn_vision()['view_size']
    b_size = int(round(image.shape[0] / r))
    return block_reduce(image, block_size=(b_size, b_size), func=np.mean)

def rgb_to_normalized_gray(rgb):
    '''Normalizes and maps 3 rgb channels to 1 channel grayscale'''
    return np.dot(rgb[...,:3] /255, [0.2989, 0.5870, 0.1140])

screen_width, screen_height = cfg.environment()['dim']

def extract_boid_view(vision_area:np.ndarray, position:np.ndarray) -> torch.Tensor:
    '''Computes downsampled boid view image state'''
    vision_poly = boid_vision_poly(vision_area, position)
    return downsample_image(vision_poly)


def boid_vision_poly(vision_area:np.ndarray, position:np.ndarray) -> torch.Tensor:
    '''Cutting boid reaction area from game screen'''
    screen = pg.display.get_surface()

    for point in vision_area:
        if point[0] < 0:
            point[0] = 0
        elif point[0] >= screen_width:
            point[0] = screen_width
        if point[1] < 0:
            point[1] = 0
        elif point[1] >= screen_height:
            point[1] = screen_height
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

def downsample_image(view:np.ndarray):
    '''Scales boid view image dimensions to neural network input and scales color values to <0,1)'''
    # view = rgb_to_normalized_gray(view)
    # view = view.transpose((2,0,1))
    view = np.ascontiguousarray(view, dtype=np.float32)/255
    view = torch.from_numpy(view)
    return view.unsqueeze(0).to(DEVICE)
    