import pygame as pg
import numpy as np
import aifishes.config as cfg
from aifishes.agent import X_AXIS_VEC

QDEBUG = False

class QLearning():
    def __init__(self):
        self.dim = cfg.environment()['dim']
        self.resolution = cfg.qlearing()['resolution']
        self.alfa = cfg.qlearing()['alfa']
        self.number_of_directions = cfg.qlearing()['number_of_directions']
        self.qtable = np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions])
        # Debug
        self.grid = cfg.qlearing()['print_grid']
        self.arrows = cfg.qlearing()['print_vectors']
        if self.arrows:
            self.ARROW_SPRITE = self.arrow_sprite()

    def next_step(self, last_states):
        if QDEBUG:
            if self.grid:
                self.print_grid()
            if self.arrows:
                self.print_arrows()
        if last_states:
            acc_table = []
            for fish in last_states['all_fishes']:
                self.update_qtable(fish.position, fish.velocity, fish.alive)
            for fish in last_states['all_fishes']:
                new_action = self.action_selection(fish.position)
                acc_table.append(new_action)
            return acc_table
        else:
            return [pg.Vector2(0, 0)]

    def update_qtable(self, position, velocity, alive):
        reward = 0
        if not alive:
            reward = -200
        x = self.discretized(position[0], self.dim[0], self.resolution[0])
        y = self.discretized(position[1], self.dim[1], self.resolution[1])
        action = self.action_reader(velocity)
        self.qtable[x, y, action] += self.alfa * reward
        return

    def action_reader(self, vector: pg.Vector2):
        angle = X_AXIS_VEC.angle_to(vector)
        offset = 180 / self.number_of_directions
        if angle < 0:
            angle = angle + 360
        return int(((angle + offset) / 360) * self.number_of_directions) % self.number_of_directions

    def action_selection(self, position):
        x = self.discretized(position[0], self.dim[0], self.resolution[0])
        y = self.discretized(position[1], self.dim[1], self.resolution[1])
        actions = self.qtable[x, y, :]
        return self.create_acceleraion(actions)

    def discretized(self, point, range_of_point, resolution):
        return int((point / range_of_point) * resolution)

    def create_acceleraion(self,actions):
        temp = pg.Vector2(0, 0)
        acceleration = pg.Vector2(0,0)
        for i, action in enumerate(actions):
            temp.from_polar((action, i *(360/ self.number_of_directions)))
            acceleration += temp

        return acceleration

    def print_grid(self):
        screen = pg.display.get_surface()
        space_x = self.dim[0] / self.resolution[0]
        space_y = self.dim[1] / self.resolution[1]
        for i in range (self.resolution[0]):
            pg.draw.line(screen, pg.Color('Black'), [i * space_x, 0], [i * space_x, self.dim[1]], 2)
        for i in range (self.resolution[1]):
            pg.draw.line(screen, pg.Color('Black'), [0, i * space_y], [self.dim[0], i * space_y], 2)


    def arrow_sprite(self):

        dim = np.array([self.dim[0] / self.resolution[0] / 2, self.dim[1] / self.resolution[1] / 2])
        surf = pg.Surface(dim, pg.SRCALPHA)
        shape = np.array([[0, 0.5 * dim[1] - 1],
                          [0.5 * dim[0], 0.5 * dim[1] - 1],
                          [0.5 * dim[0], 0 + 3],
                          [dim[0], 0.5 * dim[1]],
                          [0.5 * dim[0], dim[1] - 3],
                          [0.5 * dim[0], 0.5 * dim[1] + 1],
                          [0, 0.5 * dim[1] + 1]], dtype=np.float32)

        pg.gfxdraw.aapolygon(surf, shape, pg.Color('Black'))
        pg.gfxdraw.filled_polygon(surf, shape, pg.Color('Black'))
        return surf

    def print_arrows(self):
        screen = pg.display.get_surface()
        space_x = self.dim[0] / self.resolution[0]
        space_y = self.dim[1] / self.resolution[1]
        for i in range(self.resolution[0]):
            for j in range(self.resolution[1]):
                actions = self.qtable[i, j, :]
                vec = self.create_acceleraion(actions)
                if abs(vec.length()) > 5:
                    angle = vec.angle_to(X_AXIS_VEC)
                    self.showable_sprite = pg.transform.rotate(self.ARROW_SPRITE, angle)
                    screen.blit(self.showable_sprite, [space_x/4 + i * space_x, space_y/4 + j * space_y])
