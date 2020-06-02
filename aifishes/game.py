import pygame as pg
import pygame.gfxdraw
from aifishes.environment.agent import Agent
from aifishes.environment.environment import Environment
from aifishes.environment.fish import Fish
from aifishes.environment.predator import Predator
from aifishes.time import Time
import aifishes.config as cfg
import aifishes.qlearning as ql
import numpy as np
import math
from aifishes.flocking_behavior import flocking_behavior
from aifishes.dqn_vision.machine import DQNMachine

COLORS = pg.colordict.THECOLORS

SCREEN_COLOR = COLORS['royalblue1']
SHOW_FPS = True
DEBUG = False


class Game:
    def __init__(self):
        pg.init()
        self.DRAW = cfg.game()['draw']
        self.environment = None
        if self.DRAW:
            self.screen = pg.display.set_mode(cfg.borders())
        self.time = Time()
        pg.font.init()
        self.font = pg.font.Font(None, 30)
        self.running = False
        self.dqn_machine = DQNMachine(self)

    def setup(self):
        cfg.load_config()
        self.environment = Environment()
        self.dqn_machine.environment = self.environment
        
        for agent,_ in zip(self.environment.fishes, range(cfg.dqn_vision()['learning_agents'])):
            agent.learning = True
        self.environment.update_observations()
        self.environment.update_observations()

        self.screen.fill(SCREEN_COLOR)
        self.draw()
        self.time = Time()
        self.running = True
        # self.frame = 0

    def update(self):
        state = self.environment.get_state()
        actions = self.dqn_machine.next_step(state)
        if actions is None:
            return

        actions['dtime'] = self.time.get_dtime()
        self.environment.frame(actions)

    def draw(self):
        for agent in self.environment.fishes + self.environment.predators:
            sprite = agent.get_showable()
            self.screen.blit(sprite, agent.position -
                             pg.Vector2(sprite.get_size()) / 2)
            if DEBUG:
                agent.debug_print(self.screen)
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
            # if self.DRAW:
                # self.screen.fill(SCREEN_COLOR)
            self.update()
            if self.DRAW:
                self.draw()
            self.time.tick()

    def end(self):
        self.running = False

    def events(self):
        global DEBUG
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.setup()
                if event.key == pg.K_d:
                    DEBUG = not DEBUG
                if event.key == pg.K_h:
                    import aifishes.environment.predator as pred
                    pred.DEBUG_HUNT = not pred.DEBUG_HUNT
                if event.key == pg.K_1:
                    ql.QDEBUG = not ql.QDEBUG
                if event.key == pg.K_t:
                    self.qlearning.clear_qtable()
                if event.key == pg.K_s:
                    self.qlearning.save_qtable()
                if event.key == pg.K_COMMA:
                    self.qlearning.increase_debug_layer()
                if event.key == pg.K_PERIOD:
                    self.qlearning.decrease_debug_layer()
                if event.key == pg.K_SLASH:
                    self.qlearning.change_agent_debug()
