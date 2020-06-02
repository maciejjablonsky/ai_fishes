'''Module containing main engine of deep qlearning network'''
import torch
import torch.optim as optim
import torch.nn.functional as F
from aifishes.dqn_vision.dqn import DQN
import aifishes.config as cfg
import random
import math

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from aifishes.dqn_vision.replay_memory import ReplayMemory, Transition
from aifishes.environment.agent import Agent, X_AXIS_VEC, scale


class DQNMachine:
    def __init__(self, game):
        r = cfg.dqn_vision()['view_size']
        self.game = game
        self.environment = None
        self.n_actions = cfg.dqn_vision()['directions'] # left, right, upper, down
        self.target = DQN(r, r, self.n_actions)
        self.policy = DQN(r, r, self.n_actions)
        self.BATCH_SIZE = 128
        self.GAMMA = 0.999
        self.EPS_START = 0.9
        self.EPS_END = 0.05
        self.EPS_DECAY = 200
        self.TARGET_UPDATE = 10
        self.target.load_state_dict(self.policy.state_dict())
        self.target.eval()
        self.optimizer = optim.RMSprop(self.policy.parameters())
        self.memory = ReplayMemory(10000)
        self.steps_done = 0

    def select_action(self, state):
        sample = random.random()
        eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * \
            math.exp(-1. * self.steps_done / self.EPS_DECAY)
        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                return self.policy(state).max(1)[1].view(1, 1)
        else:
            return torch.tensor([[random.randrange(self.n_actions)]], device=DEVICE, dtype=torch.long) 

    def optimize_model(self):
        if len(self.memory) < self.BATCH_SIZE:
            return
        transitions = self.memory.sample(self.BATCH_SIZE)
        # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
        # detailed explanation). This converts batch-array of Transitions
        # to Transition of batch-arrays.
        batch = Transition(*zip(*transitions))

        # Compute a mask of non-final states and concatenate the batch elements
        # (a final state would've been the one after which simulation ended)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), device=DEVICE, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                                    if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken. These are the actions which would've been taken
        # for each batch state according to policy_net
        state_action_values = self.policy(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        # Expected values of actions for non_final_next_states are computed based
        # on the "older" target_net; selecting their best reward with max(1)[0].
        # This is merged based on the mask, such that we'll have either the expected
        # state value or 0 in case the state was final.
        next_state_values = torch.zeros(self.BATCH_SIZE, device=DEVICE)
        next_state_values[non_final_mask] = self.target(non_final_next_states).max(1)[0].detach()
        # Compute the expected Q values
        expected_state_action_values = (next_state_values * GAMMA) + reward_batch

        # Compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

        # Optimize the model
        optimizer.zero_grad()
        loss.backward()
        for param in self.policy.parameters():
            param.grad.data.clamp_(-1, 1)
        optimizer.step()

    def next_step(self, state:dict):
        for agent in state['all_fishes']:
            if agent.learning:
                self.train(agent)
            else:
                self.predict(agent)
        self.steps_done += 1
        return {
            'fishes_acc': []
        }
    
    def predict(self, agent:Agent):
        state = agent.current_view - agent.last_view
        action = self.discretize_acc_angle_to_action(agent)
        # self.select_action(state)

    def train(self, agent:Agent):
        state = agent.current_view - agent.last_view
        action = self.discretize_acc_angle_to_action(agent)
        # self.memory.push(state, )

    def discretize_acc_angle_to_action(self, agent:Agent):
        angle = agent.velocity.angle_to(X_AXIS_VEC)
        action = int(round(scale(angle, [-180, 180], [0, self.n_actions - 1])))
        return action
