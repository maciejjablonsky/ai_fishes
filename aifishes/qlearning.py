import pygame as pg
import numpy as np
import aifishes.config as cfg
from aifishes.agent import X_AXIS_VEC

class QLearing():
    def __init__(self):
        self.dim = cfg.environment()['dim']
        self.resolution = cfg.qlearing()['resolution']
        self.alfa = cfg.qlearing()['alfa']
        self.number_of_directions = cfg.qlearing()['number_of_directions']
        self.qtable = np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions])

    def next_step(self, last_states):
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

    def update_qtable(self,position ,velocity, alive):
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


    def discretized(selfs, point, range_of_point, resolution):
        return int((point / range_of_point) * resolution)

    def create_acceleraion(self,actions):
        temp = pg.Vector2(0, 0)
        acceleration = pg.Vector2(0,0)
        for i, action in enumerate(actions):
            temp.from_polar((action, i *(360/ self.number_of_directions)))
            acceleration += temp

        return acceleration
