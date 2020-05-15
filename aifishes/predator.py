import numpy as np
import aifishes.config as cfg
from aifishes import agent
from aifishes.agent import Agent, random_position, random_velocity
from aifishes.fish import Fish
import pygame as pg

PREDATOR_COLOR = pg.Color('orangered1')
PREDATOR_SPRITE = None

DEBUG_HUNT = False

def predator_sprite():
    global PREDATOR_SPRITE
    if PREDATOR_SPRITE is None:
        w, h = tuple(cfg.predator_dim())
        surf = pg.Surface((w, h), pg.SRCALPHA)
        shape = np.array([[0, 0], [w, h/2],[0, h]], dtype=np.float32)
        pg.gfxdraw.aapolygon(surf, shape, PREDATOR_COLOR)
        pg.gfxdraw.filled_polygon(surf, shape, PREDATOR_COLOR)
        PREDATOR_SPRITE = surf
    return PREDATOR_SPRITE


class Predator(Agent):
    def __init__(self):
        super().__init__(predator_sprite(), random_position(), random_velocity(cfg.predator_vel_start_magnitude()))

    def limit_velocity(self):
        limit = cfg.predator_vel_max_magnitude()
        return super().limit_velocity(limit=limit)

    def reaction_area(self):
        direction_angle = agent.X_AXIS_VEC.angle_to(self.velocity)     
        radius = cfg.predator()['reaction_radius']
        vision_angle = cfg.predator()['vision_angle']
        start = agent.scale(direction_angle - vision_angle/ 2, [0, 360], [0, 2*np.pi])
        end = agent.scale(direction_angle + vision_angle / 2, [0, 360], [0, 2*np.pi])
        t = np.linspace(start, end, dtype=np.float32)
        x = np.append(0, radius * np.cos(t))
        y = np.append(0, radius * np.sin(t))
        area = np.c_[x, y]
        return area + self.position

    def debug_print(self, screen:pg.Surface):
        pg.draw.circle(screen, agent.DEBUG_POSITION_COLOR, np.array(self.position, dtype=np.int32), 10)
        sprite_dim = pg.Vector2(self.showable_sprite.get_size())
        pg.draw.rect(screen, (0, 255, 0), pg.Rect(self.position - sprite_dim/2, sprite_dim), 2)
        pg.draw.polygon(screen, (0, 0, 0), self.reaction_area(), 2)

    def debug_hunt(self, surroundings):
        screen = pg.display.get_surface()
        for each in surroundings:
            pg.draw.circle(screen, (255, 0, 0), np.array(each.position, dtype=np.int32), 10)

    def choose_closest(self, surroundings):
        min_distance = float('inf')
        closest = None
        if len(surroundings) > 0:
            for neighbour in surroundings:
                distance = self.position.distance_to(neighbour.position)
                if distance < min_distance and neighbour is not isinstance(neighbour, Predator) and neighbour is not self:
                    min_distance = distance
                    closest = neighbour
        return closest

    def hunt(self, surroundings):
        if DEBUG_HUNT: self.debug_hunt(surroundings)
        closest = self.choose_closest(surroundings)
        if closest is not None:
            self.velocity  = self.velocity.lerp(self.velocity.magnitude() * (closest.position - self.position),  0.9)
        
        #TODO surroundings are only agents who are in reaction area but is that the case?
        # dinner = self.find_collisions(surroundings) #crappy but funny
        # for dish in dinner:
        #     if isinstance(dish,Fish):
        #         dish.ate()

