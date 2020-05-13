import aifishes.config as cfg
import pygame
from aifishes.fish import Fish
from aifishes.timer import Time
from aifishes.predator import Predator

class Environment:
    def __init__(self):
        self.fishes = [Fish() for _ in range(cfg.fish_amount())]
        self.predators  = [Predator() for _ in range(cfg.predator_amount())]

    def get_agents(self):
        return (self.fishes, self.predators)

        
    def step(self, data: dict):
        dtime = data['dtime']
        for fish, acc in zip(self.fishes, data['fish_acc']):
            fish.apply_force(acc)
        for predator, acc in zip(self.predators, data['predator_acc']):
            predator.apply_force(acc)
        for agent in self.fishes + self.predator:
            agent.update(dtime)
        
        
            
