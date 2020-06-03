import torch.nn as nn
import torch.nn.functional as F
import aifishes.config as cfg
from torch.tensor import Tensor
import torch

def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.xavier_uniform(m.weight)
        m.bias.data.fill_(0.01)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class DQN(nn.Sequential):

    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.input_linear = nn.Linear(input_dim, 2*input_dim)
        self.middle_linear = nn.Linear(2*input_dim, input_dim)
        self.output_linear = nn.Linear(input_dim, output_dim)
        
        # self.apply(init_weights)


    def forward(self, x):
        # print(x)
        # x = Tensor(x, device=DEVICE)
        x = F.relu(self.input_linear(x))
        x = F.relu(self.middle_linear(x))
        x = self.output_linear(x)
        return x

    