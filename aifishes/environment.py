import aifishes.config as cfg
import pygame as pg
from aifishes.fish import Fish
from aifishes.predator import Predator
from smartquadtree import Quadtree
from aifishes.agent import Agent
import numpy as np

QTREE_THRESHOLD = 4

def gen_border(*kwargs):
    w, h = cfg.environment()['dim']
    tolerance = cfg.environment()['border_tolerance']
    if 'top' in kwargs:
        return np.array([[-tolerance, -tolerance], [w + tolerance, -tolerance], [w + tolerance, tolerance], [-tolerance, tolerance]])
    elif 'right' in kwargs:
        return np.array([[w - tolerance, -tolerance], [w + tolerance, - tolerance], [w + tolerance, h + tolerance],[w - tolerance, h + tolerance]])
    elif 'bottom' in kwargs:
        return np.array([[-tolerance, -tolerance + h], [w + tolerance, -tolerance + h], [w + tolerance, tolerance + h], [-tolerance, tolerance + h]])
    elif 'left':
        return np.array([[-tolerance, -tolerance], [tolerance, -tolerance], [tolerance, h + tolerance],[-tolerance, h + tolerance]])
    else:
        raise NotImplemented()

class Environment:
    def __init__(self):
        self.fishes = [Fish() for _ in range(cfg.fish_amount())]
        self.all_fishes = self.fishes
        self.predators = [Predator() for _ in range(cfg.predator_amount())]
        self.all_predators = self.predators
        self.fish_qtree = None
        self.predator_qtree = None
        self.last_states = {}
        self.update_qtree()
        self.deaths = 0

    def get_state(self):
        return {
            'fishes': self.fishes,
            'predators': self.predators,
            'fishes_tree':self.fish_qtree,
            'predators_tree':self.predator_qtree,
        }

    def frame(self, data: dict):
        dtime = data['dtime']
        for fish, acc in zip(self.fishes, data['fish_acc']):
            fish.apply_force(acc)
            fish.detect_target(self.find_neighbours(fish, Predator))
        for predator, acc in zip(self.predators, data['predator_acc']):
            predator.apply_force(acc)
            predator.detect_target(self.find_neighbours(predator, Fish))
        self.kill_all_emigrants()
        self.last_states['all_fishes'] = self.fishes
        self.last_states['all_predators'] = self.predators
        self.delete_dead_fishes()
        self.predators = [predator for predator in self.predators if predator.alive]
        for agent in self.fishes + self.predators:
            agent.update(dtime)       
        self.update_qtree()
        print('\rAvg: %5f, Max: %5f, Alive: %d' %(self.average_lifetime(), self.max_lifetime(), len(self.fishes)), end='\0')


    def kill_all_emigrants(self):
        tolerance = cfg.environment()['border_tolerance']
        emigrants = []
        self.fish_qtree.set_mask(gen_border('top'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.fish_qtree.elements()]]
        self.fish_qtree.set_mask(gen_border('right'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.fish_qtree.elements()]]
        self.fish_qtree.set_mask(gen_border('bottom'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.fish_qtree.elements()]]
        self.fish_qtree.set_mask(gen_border('left'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.fish_qtree.elements()]]
        self.predator_qtree.set_mask(gen_border('top'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        self.predator_qtree.set_mask(gen_border('right'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        self.predator_qtree.set_mask(gen_border('bottom'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        self.predator_qtree.set_mask(gen_border('left'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        [emigrant.die() for emigrant in emigrants]
        
    def average_lifetime(self):
        return sum([fish.frame for fish in self.all_fishes])/len(self.all_fishes)

    def max_lifetime(self):
        return max([fish.frame for fish in self.all_fishes])

    def update_qtree(self):
        """ qtree takes center x, y and then width and heigth, so region is described as (x - w, y - h, x + w, y + h)"""
        w, h = cfg.borders()
        self.fish_qtree = Quadtree(w/2, h/2, w/2, h/2, QTREE_THRESHOLD)
        [self.fish_qtree.insert((agent.get_x(), agent.get_y(), agent))
         for agent in self.fishes]
        self.predator_qtree = Quadtree(w/2, h/2, w/2, h/2, QTREE_THRESHOLD)
        [self.predator_qtree.insert((agent.get_x(), agent.get_y(), agent))
         for agent in self.predators]

    def find_neighbours(self, agent: Agent, searched_class = None):
        if searched_class is None:
            searched_class = agent.__class__
        reaction_area = agent.reaction_area()
        if searched_class == Fish:
            self.fish_qtree.set_mask(reaction_area)
            neighbours = self.fish_qtree.elements()
        else:
            self.predator_qtree.set_mask(reaction_area)
            neighbours = self.predator_qtree.elements()
        neighbours = [element[2] for element in neighbours]
        return neighbours

    def delete_dead_fishes(self):
        number_of_fishes = len(self.fishes)
        self.fishes = [fish for fish in self.fishes if fish.alive]
        self.deaths += number_of_fishes - len(self.fishes)

    def debug_print(self):
        screen = pg.display.get_surface()
        pg.gfxdraw.filled_polygon(screen, gen_border('top'), pg.Color('black'))
        pg.gfxdraw.filled_polygon(screen, gen_border('right'), pg.Color('black'))
        pg.gfxdraw.filled_polygon(screen, gen_border('bottom'), pg.Color('black'))
        pg.gfxdraw.filled_polygon(screen, gen_border('left'), pg.Color('black'))

