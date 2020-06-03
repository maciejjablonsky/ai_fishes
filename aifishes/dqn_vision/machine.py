'''Module containing main engine of deep qlearning network'''
from aifishes.environment.agent import Agent, X_AXIS_VEC, scale
from aifishes.dqn_vision.replay_memory import ReplayMemory, Transition
import torch
import torch.optim as optim
import torch.nn.functional as F
from aifishes.dqn_vision.dqn import DQN
import aifishes.config as cfg
import random
import math
import pygame as pg 
from torch.tensor import Tensor
from typing import List
from datetime import datetime

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DQNMachine:
    def __init__(self, game):
        r = cfg.dqn_vision()['view_size']
        self.game = game
        self.environment = None
        # left, right, upper, down
        self.n_actions = cfg.dqn_vision()['output_length']
        self.target = DQN(cfg.dqn_vision()['input_length'], self.n_actions)
        self.policy = DQN(cfg.dqn_vision()['input_length'], self.n_actions)
        self.BATCH_SIZE = 64
        self.GAMMA = 0.999
        self.EPS_START = 0.9
        self.EPS_END = 0.05
        self.EPS_DECAY = 200
        self.TARGET_UPDATE = 10
        self.target.load_state_dict(self.policy.state_dict())
        self.target.eval()
        self.optimizer = optim.RMSprop(self.policy.parameters())
        self.memory = ReplayMemory(1000000)
        self.steps_done = 0
        self.epochs = 0
        self.epochs_limit = cfg.dqn_vision()['epochs']
        self.epoch_duration = 0
        self.epoch_duration_limit = cfg.dqn_vision()['epoch_duration']
        self.learning = cfg.dqn_vision()['learning']

    def select_action(self, state):
        sample = random.random()
        eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * \
            math.exp(-1. * self.steps_done / self.EPS_DECAY)
        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                return self.policy(state).max(1)[1].view(1,1)
        else:
            return torch.tensor([[random.randrange(self.n_actions)]], device=DEVICE, dtype=torch.long)

    def optimize_model(self):
        if len(self.memory) < self.BATCH_SIZE:
            return
        transitions = self.memory.sample(self.BATCH_SIZE)
        batch = Transition(*zip(*transitions))
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch.next_state)), device=DEVICE, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                           if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        
        state_action_values = self.policy(state_batch).gather(1, action_batch)

        next_state_values = torch.zeros(self.BATCH_SIZE, device=DEVICE)
        next_state_values[non_final_mask] = self.target(
            non_final_next_states).max(1)[0].detach()

        expected_state_action_values = (
            next_state_values * self.GAMMA) + reward_batch

        # Compute Huber loss
        loss = F.smooth_l1_loss(state_action_values,
                                expected_state_action_values.unsqueeze(1))

        # Optimize the model
        # print(loss, end='\0')
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

    def load_state(self, policy_path, target_path):
        self.policy.load_state_dict(torch.load(policy_path))
        self.target.load_state_dict(torch.load(target_path))

    def next_step(self, states: List[dict]):
        predictions = []
        for state in states:
            current, last = state.values()
            if current is None:
                continue
            if current['learning'] and self.learning:
                self.train(current, last)
            prediction = self.predict(current)
            # print(prediction)
            predictions.append(prediction)
        if self.manage_epochs():
            return {
                'fishes_acc': predictions
            }
        return None

    def manage_epochs(self):
        '''Returns true if game continues, False when reset or end happend'''
        self.epoch_duration += 1
        if self.should_stop():
            if self.epochs % self.TARGET_UPDATE == 0:
                self.target.load_state_dict(self.policy.state_dict())
            print('\nEpoch %d | Average time: %f | Max time: %f' % (
                self.epochs, self.environment.average_lifetime(), self.environment.max_lifetime()))
            with open('time_stats.csv', 'a') as time_stats:
                time_stats.write('%d,%f,%f\n' %(self.epochs, self.environment.average_lifetime(), self.environment.max_lifetime()))
            self.epoch_duration = 0
            self.save_stats()
            self.epochs += 1
            if self.epochs < self.epochs_limit:
                self.game.setup()
            else:
                self.game.end()
            return False
        return True

    def should_stop(self):
        return self.learning and (len(self.environment.fishes) == 0 \
            or self.epoch_duration >= self.epoch_duration_limit \
                or len(self.environment.predators) != cfg.predator()['amount'])

    def save_stats(self):
        date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        epoch = self.epochs
        torch.save(self.policy.state_dict(), 'saves/policy_model_epoch_%d_%s.model' % (epoch, date))
        torch.save(self.target.state_dict(), 'saves/target_model_epoch_%d_%s.model' % (epoch, date))

    def predict(self, state):
        action = self.select_action(torch.tensor([state['observation']])).item()
        if action == self.n_actions - 1:
            acc = pg.Vector2(0,0)
        else:
            angle = self.action_to_angle(action)
            acc = pg.Vector2()
            acc.from_polar((state['acc_magnitude'], angle))
        return acc

    def train(self, current, last):
        reward = current['reward']
        action = self.specify_action(current['acceleration'])
        self.memory.push(torch.tensor([last['observation']], device=DEVICE), 
            torch.tensor([[action]], device=DEVICE), 
            torch.tensor([current['observation']], device=DEVICE), 
            torch.tensor([[reward]], device=DEVICE))
        self.optimize_model()

    def discretize_acc_angle_to_action(self, acceleration:pg.Vector2):
        angle = acceleration.angle_to(X_AXIS_VEC)
        action = int(round(scale(angle, [-180, 180], [0, self.n_actions - 2])))
        return action

    def action_to_angle(self, action):
        return scale(action, [0, self.n_actions - 2], [-180, 180])

    def specify_action(self, acceleration:pg.Vector2):
        action = self.n_actions - 1 # last action is no acceleration
        if acceleration.length() > 1e-4:
            action = self.discretize_acc_angle_to_action(acceleration)
        return action
