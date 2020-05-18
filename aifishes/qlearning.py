import pygame as pg
import numpy as np
import aifishes.config as cfg
from aifishes.agent import X_AXIS_VEC

QDEBUG = False

class QLearning():
    def __init__(self, game):
        self.environment = None
        self.game = game
        self.dim = cfg.environment()['dim']
        self.resolution = cfg.qlearing()['resolution']
        self.alpha = cfg.qlearing()['alpha']
        self.epsilon = cfg.qlearing()['epsilon']
        self.gamma = cfg.qlearing()['gamma']
        self.LEARNING = cfg.qlearing()['learning']
        self.number_of_directions = cfg.qlearing()['number_of_directions']
        self.qtable = self.load_qtable()
        self.tick = 0
        self.epoch = 0
        self.max_epochs = cfg.qlearing()['max_epochs']
        self.max_ticks = cfg.qlearing()['max_ticks']
        # Debug
        self.grid = cfg.qlearing()['print_grid']
        self.arrows = cfg.qlearing()['print_vectors']
        if self.arrows:
            self.ARROW_SPRITE = self.arrow_sprite()

    def next_step(self):
        if not self.environment.last_states:
            return [pg.Vector2(0, 0)]
        if self.LEARNING:
            return self.learning_process()
        else:
            return self.read_from_qtable()

    def learning_process(self):
        self.debug_print()
        acceleration_table = []
        for agent in self.environment.last_states['all_fishes']:
            acceleration = self.get_acceleration(agent.position)
            self.update_qtable(agent)
            acceleration_table.append(acceleration)
        self.tick += 1
        if self.tick == self.max_ticks:
            self.next_epoch()
            return [pg.Vector2(0, 0)]
        if self.epoch == self.max_epochs:
            self.game.running = False
        return acceleration_table

    def next_epoch(self):
        self.tick = 0
        self.epoch += 1
        survival_percentage = ((cfg.fish()['amount'] - self.environment.deaths) / cfg.fish()['amount']) * 100
        self.game.setup()
        self.save_qtable()
        print("Epoch: %d, Survival percentage: %d%%" % (self.epoch, survival_percentage))

    def read_from_qtable(self):
        self.debug_print()
        acceleration_table = []
        for agent in self.environment.last_states['all_fishes']:
            acceleration = self.get_acceleration(agent.position)
            acceleration_table.append(acceleration)
        return acceleration_table

    def update_qtable(self, agent):
        reward = self.get_reward(agent)
        self.qtable *= self.epsilon
        x, y, action = self.get_state(agent)
        predicted_x, predicted_y = self.predict_next_state(x, y, agent.velocity)
        predicted_awards_array = self.qtable[predicted_x, predicted_y, :]
        predicted_award = (max(predicted_awards_array) + min(predicted_awards_array)) / 2
        self.qtable[x, y, action] += self.alpha * (reward + self.gamma * predicted_award - self.qtable[x, y, action])
        return

    def predict_next_state(self, x, y, velocity: pg.Vector2):
        vector_norm = velocity.normalize()
        predicted_x = int(round(x + vector_norm[0]))
        predicted_y = int(round(y + vector_norm[1]))
        predicted_x = max(min(predicted_x, self.resolution[0] - 1), 0)
        predicted_y = max(min(predicted_y, self.resolution[1] - 1), 0)
        return predicted_x, predicted_y

    def get_reward(self, agent):
        reward = 0
        if not agent.alive:
            reward = -200
        return reward

    def get_state(self, agent):
        x = self.discretized(agent.position[0], self.dim[0], self.resolution[0])
        y = self.discretized(agent.position[1], self.dim[1], self.resolution[1])
        action = self.action_reader(agent.velocity)
        return x, y, action

    def action_reader(self, vector: pg.Vector2):
        angle = X_AXIS_VEC.angle_to(vector)
        offset = 180 / self.number_of_directions
        if angle < 0:
            angle = angle + 360
        return int(((angle + offset) / 360) * self.number_of_directions) % self.number_of_directions

    def get_acceleration(self, position):
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

    def set_environment(self, environment):
        self.environment = environment

    def load_qtable(self):
        if self.LEARNING:
            return np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions])
        try:
            return np.load('qtable.npy')
        except IOError:
            return np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions])

    def save_qtable(self):
        np.save('qtable.npy', self.qtable)

    def clear_qtable(self):
        self.qtable = np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions])

    def debug_print(self):
        if QDEBUG:
            if self.grid:
                self.print_grid()
            if self.arrows:
                self.print_arrows()

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
                          [0.5 * dim[0], 0 + 2],
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
                if abs(vec.length()) > 3:
                    angle = vec.angle_to(X_AXIS_VEC)
                    self.showable_sprite = pg.transform.rotate(self.ARROW_SPRITE, angle)
                    screen.blit(self.showable_sprite, [space_x/4 + i * space_x, space_y/4 + j * space_y])
