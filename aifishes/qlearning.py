import pygame as pg
import numpy as np
import aifishes.config as cfg
from aifishes.environment.agent import X_AXIS_VEC
from aifishes.environment.fish import Fish
from datetime import datetime

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
        self.NEW_QTABLE = cfg.qlearing()['new_qtable']
        self.number_of_directions = cfg.qlearing()['number_of_directions']
        self.qtable = self.load_qtable()
        self.frames = 0
        self.epoch = 0
        self.max_epochs = cfg.qlearing()['max_epochs']
        self.max_frames = cfg.qlearing()['max_ticks']
        # Debug
        self.grid = cfg.qlearing()['print_grid']
        self.arrows = cfg.qlearing()['print_vectors']
        self.QDEBUG_LAYER = 0
        self.AGENT_INDEX_DEBUG = 0
        if self.arrows:
            self.ARROW_FISH_SPRITE, self.ARROW_PREDATOR_SPRITE = self.arrow_sprite()
        self.stat_filename = None
        self.setup_stat_file()

    def next_step(self, agent_class):
        agent_class_index = self.get_class(agent_class)
        if not self.environment.last_states:
            return [pg.Vector2(0, 0)]
        if self.LEARNING:
            return self.learning_process(agent_class_index)
        else:
            return self.read_from_qtable(agent_class_index)

    def learning_process(self, agent_class_index):
        self.debug_print()
        acceleration_table = []
        for agent in self.get_agents(agent_class_index):
            acceleration = self.get_acceleration(agent, agent_class_index)
            self.update_qtable(agent)
            acceleration_table.append(acceleration)
        self.frames += 1
        if self.should_stop():
            self.next_epoch()
            return [pg.Vector2(0, 0)]
        if self.epoch == self.max_epochs:
            self.game.running = False
        return acceleration_table

    def next_epoch(self):
        self.frames = 0
        self.epoch += 1
        self.save_stats()
        self.game.setup()
        self.save_qtable()

    def save_stats(self):
        survival_percentage = 0
        max_lifetime, avg_lifetime =0,0
        if cfg.fish()['amount'] > 0:
            survival_percentage = ((cfg.fish()['amount'] - self.environment.deaths) / cfg.fish()['amount']) * 100
            max_lifetime = self.environment.max_lifetime()
            avg_lifetime = self.environment.average_lifetime()
        with open(self.stat_filename, 'a') as stats:
            stats.write(f'{self.epoch},{avg_lifetime},{max_lifetime}\n')
        print(f"\nepoch: {self.epoch} | avg: {avg_lifetime} | max: {max_lifetime} | survival [%]: {survival_percentage}")

    def read_from_qtable(self, agent_class_index):
        self.debug_print()
        acceleration_table = []
        for agent in self.get_agents(agent_class_index):
            acceleration = self.get_acceleration(agent, agent_class_index)
            acceleration_table.append(acceleration)
        return acceleration_table

    def update_qtable(self, agent):
        self.qtable *= self.epsilon
        x, y, danger_angle, agent_class, action = self.get_state(agent)
        reward = self.get_reward(agent, x, y, agent_class, action)
        predicted_x, predicted_y = self.predict_next_state(x, y, agent.velocity)
        predicted_awards_array = self.qtable[predicted_x, predicted_y, 0, agent_class, :]
        predicted_award = (max(predicted_awards_array) + min(predicted_awards_array)) / 2
        try:
            self.qtable[x, y, danger_angle, agent_class, action] += self.alpha * (reward + self.gamma * predicted_award - self.qtable[x, y, danger_angle, agent_class, action])
        except IndexError:
            # print(f'Error: Failed to update qtable at [{x}, {y}]')
            pass
        return

    def predict_next_state(self, x, y, velocity: pg.Vector2):
        vector_norm = velocity.normalize()
        predicted_x = int(round(x + vector_norm[0]))
        predicted_y = int(round(y + vector_norm[1]))
        predicted_x = max(min(predicted_x, self.resolution[0] - 1), 0)
        predicted_y = max(min(predicted_y, self.resolution[1] - 1), 0)
        return predicted_x, predicted_y

    def get_reward(self, agent, x, y, agent_class, action):
        reward = 0
        if not agent.alive:
            reward -= 1000
        if agent.closest_target is not None:
            target_vec = (agent.position - agent.closest_target.position).normalize()
            velocity_vec = agent.velocity.normalize()
            if agent_class == 0:
                reward += round((pg.Vector2(target_vec + velocity_vec).length() - 1 ) * 200)
            else:
                reward -= round((pg.Vector2(target_vec + velocity_vec).length() - 1) * 400)
                if agent.closest_target.alive == 0:
                    reward += 500


        return reward

    def get_state(self, agent):
        x = self.discretized(agent.position[0], self.dim[0], self.resolution[0])
        y = self.discretized(agent.position[1], self.dim[1], self.resolution[1])
        danger_angle = self.get_angle_to_predator(agent, agent.closest_target)
        agent_class = self.get_class(agent)
        action = self.action_reader(agent.velocity)
        return x, y, danger_angle, agent_class, action

    def get_angle_to_predator(self, agent, predator):
        if predator is None:
            return 0
        direction_vec = (predator.position - agent.position).normalize()
        return self.action_reader(direction_vec) + 1

    def action_reader(self, vector: pg.Vector2):
        angle = X_AXIS_VEC.angle_to(vector)
        offset = 180 / self.number_of_directions
        if angle < 0:
            angle = angle + 360
        return int(((angle + offset) / 360) * self.number_of_directions) % self.number_of_directions

    def get_acceleration(self, agent, agent_class_index):
        x, y, danger_angle,agent_class_index, action = self.get_state(agent)

        try:
            actions = self.qtable[x, y, danger_angle, agent_class_index, :]
        except IndexError:
            return pg.Vector2(0,0)
        return self.create_acceleraion(actions)

    def discretized(self, point, range_of_point, resolution):
        return int((point / range_of_point) * resolution)

    def create_acceleraion(self, actions):
        temp = pg.Vector2(0, 0)
        acceleration = pg.Vector2(0,0)
        for i, action in enumerate(actions):
            temp.from_polar((action, i *(360/ self.number_of_directions)))
            acceleration += temp
        return acceleration

    def get_class(self, agent):
        if agent == Fish:
            return 0
        else:
            if isinstance(agent, Fish):
                return 0
            else:
                return 1

    def get_agents(self, agent_class_index):
        if agent_class_index == 0:
            return self.environment.last_states['all_fishes']
        else:
            return self.environment.last_states['all_predators']

    def set_environment(self, environment):
        self.environment = environment

    def load_qtable(self):
        if self.NEW_QTABLE:
            return np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions + 1, 2, self.number_of_directions])
        try:
            return np.load('qtable.npy')
        except IOError:
            return np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions + 1, 2, self.number_of_directions])

    def save_qtable(self):
        np.save('qtable.npy', self.qtable)

    def clear_qtable(self):
        self.qtable = np.zeros([self.resolution[0], self.resolution[1], self.number_of_directions + 1, 2, self.number_of_directions])

    def increase_debug_layer(self):
        self.QDEBUG_LAYER = (self.QDEBUG_LAYER + 1) % (self.number_of_directions + 1)

    def decrease_debug_layer(self):
        self.QDEBUG_LAYER = (self.QDEBUG_LAYER - 1) % (self.number_of_directions + 1)

    def change_agent_debug(self):
        self.AGENT_INDEX_DEBUG = (self.AGENT_INDEX_DEBUG + 1) % 2

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
        for i in range(self.resolution[0]):
            pg.draw.line(screen, pg.Color('Black'), [i * space_x, 0], [i * space_x, self.dim[1]], 2)
        for i in range(self.resolution[1]):
            pg.draw.line(screen, pg.Color('Black'), [0, i * space_y], [self.dim[0], i * space_y], 2)


    def arrow_sprite(self):
        dim = np.array([self.dim[0] / self.resolution[0] / 2, self.dim[1] / self.resolution[1] / 2])
        surfB = pg.Surface(dim, pg.SRCALPHA)
        surfN = pg.Surface(dim, pg.SRCALPHA)
        shape = np.array([[0, 0.5 * dim[1] - 1],
                          [0.5 * dim[0], 0.5 * dim[1] - 1],
                          [0.5 * dim[0], 0 + 2],
                          [dim[0], 0.5 * dim[1]],
                          [0.5 * dim[0], dim[1] - 3],
                          [0.5 * dim[0], 0.5 * dim[1] + 1],
                          [0, 0.5 * dim[1] + 1]], dtype=np.float32)

        pg.gfxdraw.aapolygon(surfB, shape, pg.Color('tomato4'))
        pg.gfxdraw.filled_polygon(surfB, shape, pg.Color('tomato4'))
        pg.gfxdraw.aapolygon(surfN, shape, pg.Color('Blue4'))
        pg.gfxdraw.filled_polygon(surfN, shape, pg.Color('Blue4'))
        return surfB, surfN

    def print_arrows(self):
        screen = pg.display.get_surface()
        space_x = self.dim[0] / self.resolution[0]
        space_y = self.dim[1] / self.resolution[1]
        for i in range(self.resolution[0]):
            for j in range(self.resolution[1]):
                actions = self.qtable[i, j, self.QDEBUG_LAYER, self.AGENT_INDEX_DEBUG, :]
                vec = self.create_acceleraion(actions)
                if abs(vec.length()) > 3:
                    angle = vec.angle_to(X_AXIS_VEC)
                    if self.AGENT_INDEX_DEBUG == 0:
                        showable_sprite = pg.transform.rotate(self.ARROW_FISH_SPRITE, angle)
                    else:
                        showable_sprite = pg.transform.rotate(self.ARROW_PREDATOR_SPRITE, angle)
                    screen.blit(showable_sprite, [space_x/4 + i * space_x, space_y/4 + j * space_y])


    def should_stop(self):
            return self.LEARNING and (len(self.environment.fishes) == 0 \
                or self.frames >= self.max_frames \
                    or len(self.environment.predators) != cfg.predator()['amount'])

    def setup_stat_file(self):
        date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self.stat_filename = 'stats_%s.csv' % date
        with open(self.stat_filename, 'w') as stats:
            stats.write('epochs,average,maximum\n')