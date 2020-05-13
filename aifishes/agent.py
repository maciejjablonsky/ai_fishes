import numpy as np
import aifishes.config as cfg
import typing
import pygame


def random_position(borders: list):
    return np.array([
        scale(np.random.rand(), [0, 1], [0, borders[0]]),
        scale(np.random.rand(), [0, 1], [0, borders[1]])
    ])

def random_velocity():
    magnitude = cfg.velocity_start_magnitude()
    angle = scale(np.random.rand(), [0, 1], [0, 2*np.pi])
    return magnitude * np.array([np.cos(angle), np.sin(angle)])

def scale(value, old, new: np.Array):
    return (value / (old[1] - old[0])) * (new[1] - new[0]) + new[0]

class Agent:
    def __init__(self, shape :np.Array, position:np.Array, velocity: np.Array):
        self.shape = shape
        self.position = position
        self.velocity = velocity
        self.acceleration = np.zeros(dtype=np.float32, shape=(2))
        self.alive = True

    def update_position(self, dtime):
        self.position = self.position + self.velocity * dtime

    def update_velocity(self, dtime):
        next_velocity =  self.velocity + self.acceleration * dtime
        limit = cfg.velocity_max_magnitude()
        current_magnitude = np.linalg.norm(next_velocity)
        if current_magnitude > limit:
            unit = next_velocity / current_magnitude
            next_velocity = limit * unit
        self.velocity = next_velocity


    def apply_force(self, acceleration: np.Array):
        self.acceleration = acceleration

    def update(self, dtime):
        self.update_velocity(dtime)
        self.update_position(dtime)

    def show(self):
        shape_to_display = np.array([x + self.position for x in self.shape])
        pygame.draw.polygon()