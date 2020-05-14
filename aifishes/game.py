import pygame as pg
import pygame.gfxdraw
from aifishes.environment import Environment
from aifishes.time import Time
import aifishes.config as cfg
import numpy as np
import math
COLORS = pg.colordict.THECOLORS

SCREEN_COLOR = COLORS['darkmagenta']
SHOW_FPS = True


class Game:
    def __init__(self):
        pg.init()
        self.env = None
        self.screen = pg.display.set_mode(size=cfg.borders())
        self.time = Time()
        pg.font.init()
        self.font = pg.font.Font(None, 30)
        self.running = False

    def setup(self):
        self.env = Environment()
        self.running = True

    def update(self):
        agents = self.env.get_state()
        data = {
            'dtime': self.time.get_dtime(),
            'fish_acc': [pg.Vector2(0, 0)] * len(agents['fishes']),
            'predator_acc': [pg.Vector2(0, 0)] * len(agents['predators'])
        }
        self.env.frame(data)

    def draw(self):
        self.screen.fill(SCREEN_COLOR)
        state = self.env.get_state()
        for agent in state['fishes'] + state['predators']:
            self.screen.blit(agent.get_showable(), agent.position)
        if SHOW_FPS:
            self.blit_fps(self.time.get_fps())
        pg.display.flip()

    def blit_fps(self, fps):
        fps_view = self.font.render(
            "FPS: {0:.2f}".format(fps), True, pg.Color('red'))
        self.screen.blit(fps_view, (10, 10))

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.time.tick()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.setup()
