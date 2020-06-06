'''
This module contains original Reynolds 1987 flocking behavior.
Separation: steer to avoid local crowding
Cohesion: steer to average position of local flockmates
Alignment: steer towards average heading of local flockmates
'''
from aifishes.fish import Fish
from typing import List
from smartquadtree import Quadtree
from pygame import Vector2
from functools import reduce
from aifishes.config import flocking


def flocking_behavior(environment_data: dict) -> List[Fish]:
    """Acummulates rules of flocking behavior as list of acceleration vectors for each boid"""
    alignment_coefficient = flocking()['alignment']
    separation_coefficient = flocking()['separation']
    cohesion_coefficient = flocking()['cohesion']
    qtree = environment_data['fishes_tree']
    dtime = environment_data['dtime']

    def find_flockmates(boid: Fish) -> List[Fish]:
        '''Finds all boids within reaction area'''
        qtree.set_mask(boid.reaction_area())
        return [e[2] for e in qtree.elements() if e[2] is not boid]

    def find_safe_space_intruders(boid: Fish) -> List[Fish]:
        '''Finds all boids that are within safe space of boid'''
        qtree.set_mask(boid.safe_space())
        return [e[2] for e in qtree.elements() if e[2] is not boid]

    def separation(boid: Fish, flockmates: List[Fish]) -> Vector2:
        '''Computes acceleration to avoid local crowding with flockmates'''
        '''Formula is negative sum of differences between flockmates and boid'''
        if len(flockmates) >0:
            return -1 * reduce(lambda a, b: a + b, [mate.position - boid.position for mate in flockmates])
        else:
            return Vector2(0,0)

    def cohesion(boid: Fish, flockmates: List[Fish]) -> Vector2:
        '''Computes acceleration to keep boid close to other boids'''
        '''Formula is difference between average position of flockmates and boid position'''
        mates_positions = [mate.position for mate in flockmates]
        return (reduce(lambda a, b: a + b, mates_positions)/len(flockmates) - boid.position)

    def alignment(boid: Fish, flockmates: List[Fish]) -> Vector2:
        '''Computes acceleration to keep boid velocity in alignment with local flockmates'''
        mates_velocities = [mate.velocity for mate in flockmates]

        return (reduce(lambda a, b: a+b, mates_velocities) / len(flockmates) - boid.velocity)

    def compute_flocking(boid: Fish) -> Vector2:
        '''Accumulates all traits for one boid'''
        flockmates = find_flockmates(boid)
        if len(flockmates) > 0:
            return cohesion_coefficient * cohesion(boid, flockmates) + alignment_coefficient * alignment(boid, flockmates) + separation_coefficient * separation(boid, find_safe_space_intruders(boid))
        else:
            return Vector2(0, 0)

    return [compute_flocking(boid) for boid in environment_data['fishes']]
