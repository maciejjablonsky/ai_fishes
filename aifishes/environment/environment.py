import aifishes.config as cfg
import pygame as pg
from aifishes.environment.fish import Fish
from aifishes.environment.predator import Predator
from smartquadtree import Quadtree
from aifishes.environment.agent import Agent
import numpy as np
from shapely.geometry import Polygon, Point
from typing import List
from functools import reduce
from torch.tensor import Tensor

QTREE_THRESHOLD = 4


def gen_border(*args, **kwargs):
    w, h = cfg.environment()['dim']
    tolerance = kwargs['tolerance']
    if 'top' in args:
        return np.array([[-tolerance, -tolerance], [w + tolerance, -tolerance], [w + tolerance, tolerance], [-tolerance, tolerance]])
    elif 'right' in args:
        return np.array([[w - tolerance, -tolerance], [w + tolerance, - tolerance], [w + tolerance, h + tolerance], [w - tolerance, h + tolerance]])
    elif 'bottom' in args:
        return np.array([[-tolerance, -tolerance + h], [w + tolerance, -tolerance + h], [w + tolerance, tolerance + h], [-tolerance, tolerance + h]])
    elif 'left':
        return np.array([[-tolerance, -tolerance], [tolerance, -tolerance], [tolerance, h + tolerance], [-tolerance, h + tolerance]])
    else:
        raise NotImplemented()


BORDERS_NAMES = ['top', 'right', 'bottom', 'left']
TURNING_BORDERS: List[Polygon] = [Polygon(gen_border(border, tolerance=cfg.environment()[
                                          'turning_tolerance'])) for border in BORDERS_NAMES]
SCREEN_WIDTH, SCREEN_HEIGHT = cfg.environment()['dim']

class Environment:
    def __init__(self):
        self.fishes = [Fish() for _ in range(cfg.fish_amount())]
        self.all_fishes = self.fishes
        self.predators = [Predator() for _ in range(cfg.predator_amount())]
        self.all_predators = self.predators
        self.fish_qtree = None
        self.predator_qtree = None
        self.last_frame = {
            'all_fishes': self.fishes,
            'all_predators': self.predators
        }
        self.update_qtree()
        self.deaths = 0

    def get_state(self):
        return [{'current':f.current_observation, 'last':f.last_observation} for f in self.last_frame['all_fishes']]

    

    def frame(self, actions: dict):
        dtime = actions['dtime']
        for fish, acc in zip(self.fishes, actions['fishes_acc']):
            fish.set_acceleration(acc)
        for predator in self.predators:
            predator.set_acceleration(pg.Vector2(0,0))
            if self.is_agent_withing_turning_area(predator):
                predator.steer_to_center()
            else:
                predator.action(self.find_neighbours(predator, Fish))
        self.separate_predators()
        self.kill_all_emigrants()
        self.last_frame['all_fishes'] = self.fishes
        self.last_frame['all_predators'] = self.predators
        self.delete_dead_fishes()
        self.predators = [
            predator for predator in self.predators if predator.alive]
        for agent in self.fishes + self.predators:
            agent.update(dtime)

        self.update_qtree()
        self.update_observations()
        
        print('\rAvg: %5f, Max: %5f, Alive: %d' %(self.average_lifetime(), self.max_lifetime(), len(self.fishes)), end='\0')

    def update_observations(self):
        for fish in self.last_frame['all_fishes']:
            fish.update_observation(self.create_observations(fish))

    def kill_all_emigrants(self):
        tolerance=cfg.environment()['border_tolerance']
        emigrants=[]
        self.fish_qtree.set_mask(gen_border('top', tolerance=tolerance))
        [emigrants.append(emigrant) for emigrant in [element[2]
                          for element in self.fish_qtree.elements()]]
        self.fish_qtree.set_mask(gen_border('right', tolerance=tolerance))
        [emigrants.append(emigrant) for emigrant in [element[2]
                          for element in self.fish_qtree.elements()]]
        self.fish_qtree.set_mask(gen_border('bottom', tolerance=tolerance))
        [emigrants.append(emigrant) for emigrant in [element[2]
                          for element in self.fish_qtree.elements()]]
        self.fish_qtree.set_mask(gen_border('left', tolerance=tolerance))
        [emigrants.append(emigrant) for emigrant in [element[2]
                          for element in self.fish_qtree.elements()]]
        # self.predator_qtree.set_mask(gen_border('top', tolerance=tolerance))
        # [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        # self.predator_qtree.set_mask(gen_border('right', tolerance=tolerance))
        # [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        # self.predator_qtree.set_mask(gen_border('bottom', tolerance=tolerance))
        # [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        # self.predator_qtree.set_mask(gen_border('left', tolerance=tolerance))
        # [emigrants.append(emigrant) for emigrant in [element[2] for element in self.predator_qtree.elements()]]
        [emigrant.die() for emigrant in emigrants]

    def create_observations(self, fish:Fish):
        if not fish.alive:
            return None

        obs = [fish.velocity.x, fish.velocity.y, fish.acceleration.x, fish.acceleration.y]

        '''top, right, bottom, left'''
        wall_distances = [fish.position.y, SCREEN_WIDTH - fish.position.x, SCREEN_HEIGHT - fish.position.y, fish.position.x]
        obs.extend(wall_distances)
        mates = self.find_neighbours(fish)
        enemies = self.find_neighbours(fish, Predator)
        mate_vec = pg.Vector2(0,0)
        enemy_vec = pg.Vector2(0,0)
        
        if len(mates) > 0:
            mate_vec = reduce(lambda a,b: a+ b, [mate.position - fish.position for mate in mates])/len(mates)
        if len(enemies) > 0:
            enemy_vec = reduce(lambda a,b: a + b, [enemy.position - fish.position for enemy in enemies])/len(enemies)

        obs.append(mate_vec.x)
        obs.append(mate_vec.y)
        obs.append(enemy_vec.x)
        obs.append(enemy_vec.y)
        # print(len(obs), obs)
        return {
            'observation': obs,
            'reward': fish.reward,
            'acceleration': fish.acceleration,
            'alive': fish.alive,
            'learning': fish.learning,
            'acc_magnitude':fish.max_acc_magnitude
        }
        
    def update_qtree(self):
        """ qtree takes center x, y and then width and heigth, so region is described as (x - w, y - h, x + w, y + h)"""
        w, h=cfg.borders()
        self.fish_qtree=Quadtree(w/2, h/2, w/2, h/2, QTREE_THRESHOLD)
        [self.fish_qtree.insert((agent.get_x(), agent.get_y(), agent))
         for agent in self.fishes]
        self.predator_qtree = Quadtree(w/2, h/2, w/2, h/2, QTREE_THRESHOLD)
        [self.predator_qtree.insert((agent.get_x(), agent.get_y(), agent))
         for agent in self.predators] 
       
    def find_neighbours(self, agent: Agent, searched_class=None):
        if searched_class is None:
            searched_class=agent.__class__
        reaction_area=agent.reaction_area()
        if searched_class == Fish:
            self.fish_qtree.set_mask(reaction_area)
            neighbours=self.fish_qtree.elements()
        else:
            self.predator_qtree.set_mask(reaction_area)
            neighbours=self.predator_qtree.elements()
        neighbours=[element[2] for element in neighbours if element[2] is not agent]
        return neighbours

    def delete_dead_fishes(self):
        number_of_fishes=len(self.fishes)
        self.fishes=[fish for fish in self.fishes if fish.alive]
        self.deaths += number_of_fishes - len(self.fishes)

    def debug_print(self):
        screen=pg.display.get_surface()
        pg.gfxdraw.filled_polygon(screen, gen_border('top'), pg.Color('black'))
        pg.gfxdraw.filled_polygon(
            screen, gen_border('right'), pg.Color('black'))
        pg.gfxdraw.filled_polygon(
            screen, gen_border('bottom'), pg.Color('black'))
        pg.gfxdraw.filled_polygon(
            screen, gen_border('left'), pg.Color('black'))

    def is_agent_withing_turning_area(self, agent: Agent):
        pos = Point(agent.position)
        return any([border.contains(pos) for border in TURNING_BORDERS])

    def average_lifetime(self):
        return sum([fish.frame for fish in self.all_fishes])/len(self.all_fishes)

    def max_lifetime(self):
        return max([fish.frame for fish in self.all_fishes])

    def separate_predators(self):
        for predator in self.predators:
            close = self.find_neighbours(predator)
            if len(close) > 0:
                acc = -1 *reduce(lambda a, b: a + b, [(mate.position - predator.position)* 5 for mate in close]) * 10
                predator.set_acceleration(acc)
            