import pygame as pg
import numpy as np
from aifishes.agent import X_AXIS_VEC

class QLearing():
    def __init__(self, resolution, dim):
        self.resolution = resolution
        self.number_of_directions = 8
        self.dim = dim
        self.alfa = 0.96
        # 0 UP, 1 RIGHT, 2 DOWN, 3 LEFT
        self.qtable = np.zeros([resolution[0], resolution[1], self.number_of_directions])


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
        if alive:
            reward = 0
        else:
            reward = -200

        x = self.discretized(position[0], self.dim[0], self.resolution[0])
        y = self.discretized(position[1], self.dim[1], self.resolution[1])
        action = self.action_reader(velocity)
        self.qtable[x, y, action] += self.alfa * reward
        return

    def action_reader(self, vector: pg.Vector2):
        angle = X_AXIS_VEC.angle_to(vector)
        if angle < 0:
            angle = angle + 360
        return int((angle / 360) * self.number_of_directions) % self.number_of_directions

    def action_selection(self, position):
        x = self.discretized(position[0], self.dim[0], self.resolution[0])
        y = self.discretized(position[1], self.dim[1], self.resolution[1])
        actions = self.qtable[x, y, :]
        return self.create_acceleraion(actions)


    def discretized(selfs, point, range_of_point, resolution):
        return int((point / range_of_point) * resolution)

    def create_acceleraion(self,actions):
        a = pg.Vector2(0,0)
        acceleration = pg.Vector2(0,0)
        for i,action in enumerate(actions):
            a.from_polar((action, i *(360/ self.number_of_directions)))
            acceleration += a;

        #acceleration = pg.Vector2(0, -actions[0])
        #acceleration += pg.Vector2(actions[1],0)
        #acceleration += pg.Vector2(0,actions[2])
        #acceleration += pg.Vector2(-actions[3],0)
        return acceleration
