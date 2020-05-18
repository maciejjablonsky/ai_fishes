import pygame as pg

class Time():
    def __init__(self):
        self.clock = pg.time.Clock()
        self.last_ticks = 0
        self.dtime = 0
        self.gtime = 0

    def tick(self):
        t = pg.time.get_ticks()
        self.dtime = (t - self.last_ticks) / 1000
        self.dtime = min(self.dtime, 0.05)
        self.gtime += self.dtime
        self.last_ticks = t
        self.clock.tick()
    
    def get_dtime(self):
        """Returns time since last frame in miliseconds"""
        return self.dtime

    def get_gtime(self):
        """Returns global time since setup() call"""
        return self.gtime
    
    def get_fps(self):
        return self.clock.get_fps()