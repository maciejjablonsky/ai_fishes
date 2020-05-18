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
        self.predators = [Predator() for _ in range(cfg.predator_amount())]
        self.qtree = None
        self.last_states = {}
        self.update_qtree()
        self.deaths = 0

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
        self.kill_all_emigrants()
        self.last_states['all_fishes'] = self.fishes
        self.delete_dead_fishes()
        self.predators = [predator for predator in self.predators if predator.alive]
        for agent in self.fishes + self.predators:
            agent.update(dtime)       
        self.update_qtree()


    def kill_all_emigrants(self):
        tolerance = cfg.environment()['border_tolerance']
        emigrants = []
        self.qtree.set_mask(gen_border('top'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.qtree.elements()]]
        self.qtree.set_mask(gen_border('right'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.qtree.elements()]]
        self.qtree.set_mask(gen_border('bottom'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.qtree.elements()]]
        self.qtree.set_mask(gen_border('left'))
        [emigrants.append(emigrant) for emigrant in [element[2] for element in self.qtree.elements()]]
        [emigrant.die() for emigrant in emigrants]
        

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

