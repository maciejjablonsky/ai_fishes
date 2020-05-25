import numpy as np
import aifishes.config as cfg
from aifishes import agent
from aifishes.agent import Agent, random_position, random_velocity
from aifishes.fish import Fish
import pygame as pg

PREDATOR_COLOR = pg.Color('darkblue')
PREDATOR_SPRITE = None

DEBUG_HUNT = False


def predator_sprite():
    global PREDATOR_SPRITE
    if PREDATOR_SPRITE is None:
        w, h = tuple(cfg.predator_dim())
        surf = pg.Surface((w, h), pg.SRCALPHA)
        shape = np.array([[0, 0], [w, h/2], [0, h]], dtype=np.float32)
        pg.gfxdraw.aapolygon(surf, shape, PREDATOR_COLOR)
        pg.gfxdraw.filled_polygon(surf, shape, PREDATOR_COLOR)
        pg.draw.line(surf, pg.Color('Gray'), [w/9, h/2], [w/3, h/2], 2)
        PREDATOR_SPRITE = surf
    return PREDATOR_SPRITE

def predator_shape():
    w, h = cfg.predator()['dim']
    vec = pg.Vector2
    return [vec(-w/2, -h/2), vec(w/2, 0), vec(-w/2, h/2)]

class Predator(Agent):
    def __init__(self):
        super().__init__(predator_sprite(), random_position(),
                         random_velocity(cfg.predator_vel_start_magnitude()))
        self.hitbox = predator_shape()

    def limit_velocity(self):
        limit = cfg.predator_vel_max_magnitude()
        return super().limit_velocity(limit=limit)

    def reaction_area(self):
        direction_angle = agent.X_AXIS_VEC.angle_to(self.velocity)
        radius = cfg.predator()['reaction_radius']
        vision_angle = cfg.predator()['vision_angle']
        start = agent.scale(direction_angle - vision_angle /
                            2, [0, 360], [0, 2*np.pi])
        end = agent.scale(direction_angle + vision_angle /
                          2, [0, 360], [0, 2*np.pi])
        t = np.linspace(start, end, num=20, dtype=np.float32)
        x = np.append(0, radius * np.cos(t))
        y = np.append(0, radius * np.sin(t))
        area = np.c_[x, y]
        return area + self.position

    def debug_print(self, screen: pg.Surface):
        pg.draw.circle(screen, pg.Color('green'), np.array(
            self.position, dtype=np.int32), 2)
        sprite_dim = pg.Vector2(self.showable_sprite.get_size())
        # pg.draw.rect(screen, (0, 255, 0), pg.Rect(
            # self.position - sprite_dim/2, sprite_dim), 2)
        pg.draw.polygon(screen, (0, 0, 0), self.reaction_area(), 2)
        if self.closest_target is not None:
            pg.draw.line(screen, pg.Color('red'), self.position, self.closest_target.position, 2)

        # axis_len = 200
        # X axis
        # pg.draw.line(screen, pg.Color('white'), np.array(self.position, dtype=np.int32), np.array(
        #     self.position + axis_len * agent.X_AXIS_VEC, dtype=np.int32), 2)
        # # Y axis
        # pg.draw.line(screen, pg.Color('white'), np.array(self.position, dtype=np.int32), np.array(
        #     self.position + axis_len * agent.Y_AXIS_VEC, dtype=np.int32), 2)

        # pg.draw.line(screen, pg.Color('cyan'), self.position, self.position + axis_len * self.velocity.normalize(), 2)
    def debug_hunt(self, surroundings):
        screen = pg.display.get_surface()
        for each in surroundings:
            pg.draw.circle(screen, (255, 0, 0), np.array(
                each.position, dtype=np.int32), 10)

    def detect_target(self, surroundings):
        super().detect_target(surroundings)
        self.dinner(surroundings)

    def hunt(self, surroundings):
        if DEBUG_HUNT:
            self.debug_hunt(surroundings)
        closest = self.choose_closest(surroundings)
        if closest is not None:
            self.velocity = self.velocity.lerp(self.velocity.magnitude() * (closest.position - self.position),  0.005)
        
        #TODO surroundings are only agents who are in reaction area but is that the case?
        self.dinner(surroundings)

    def dinner(self, surroundings):
        dinner = self.find_collisions(surroundings) #crappy but funny
        for dish in dinner:
            if isinstance(dish, Fish):
                dish.die()
