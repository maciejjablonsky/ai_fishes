import aifishes.config as cfg
import pygame
from aifishes.fish import Fish
from aifishes.predator import Predator
import scipy as scp
from smartquadtree import Quadtree
from aifishes.agent import Agent

QTREE_THRESHOLD = 4

class Environment:
    def __init__(self):
        self.fishes = [Fish() for _ in range(cfg.fish_amount())]
        self.predators = [Predator() for _ in range(cfg.predator_amount())]
        self.qtree = None
        self.update_qtree()

    def get_state(self):
        return {
            'fishes': self.fishes,
            'predators': self.predators,
            'qtree': self.qtree
        }

    def frame(self, data: dict):
        dtime = data['dtime']
        for fish, acc in zip(self.fishes, data['fish_acc']):
            fish.apply_force(acc)
        for predator, acc in zip(self.predators, data['predator_acc']):
            predator.apply_force(acc)
            predator.hunt(self.find_neighbours(predator))
            self.find_neighbours(predator)
        for agent in self.fishes + self.predators:
            agent.update(dtime)
        self.update_qtree()

    def update_qtree(self):
        """ qtree takes center x, y and then width and heigth, so region is described as (x - w, y - h, x + w, y + h)"""
        w, h = cfg.borders()
        self.qtree = Quadtree(w/2, h/2, w/2, h/2, QTREE_THRESHOLD)
        [self.qtree.insert((agent.get_x(), agent.get_y(), agent))
         for agent in self.fishes + self.predators]

    def find_neighbours(self, agent: Agent):
        reaction_area = agent.reaction_area()
        self.qtree.set_mask(reaction_area)
        neighbours = self.qtree.elements()
        return [element[2] for element in neighbours]
        
