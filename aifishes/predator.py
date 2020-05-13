import numpy as np 
import aifishes.config as cfg
from aifishes.agent import Agent, random_position, random_velocity

class Predator(Agent):
    def __init__(self):
        dim = cfg.predator_dim()
        shape = np.array([[0, 0], [dim[0], 0.5 * dim[1]],[0, dim[1]]], dtype=np.float32)
        super().__init__(shape, random_position(cfg.borders()), random_velocity())