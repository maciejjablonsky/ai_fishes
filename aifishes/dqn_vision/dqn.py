import torch.nn as nn
import torch.nn.functional as F
import aifishes.config as cfg
from torch.tensor import Tensor
class DQN(nn.Module):

    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.input_linear = nn.Linear(input_dim, 2*input_dim)
        self.middle_linear = nn.Linear(2*input_dim, 2*input_dim)
        self.output_linear = nn.Linear(2*input_dim, output_dim)


    def forward(self, x):
        # print(x)
        x = Tensor(x)
        x = F.relu(self.input_linear(x))
        x = F.relu(self.middle_linear(x))
        x = self.output_linear(x)
        return x