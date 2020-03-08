from pygame.time import Clock
from pygame import time


class Time():
    def __init__(self):
        self.clock = Clock()
        self._previous_time : float= 0
        self._next_time : float = 0
        self._last_delta_time : float = 0
        self._global = 0
        self._running = False

    def reset(self):
        self._next_time = 0
        self._previous_time = 0

    def start(self):
        self._running = True
        self._previous_time = time.get_ticks()

    def stop(self):
        self._running = False

    @property
    def dtime(self):
        return self._last_delta_time

    @property
    def running(self):
        return self._running

    def update(self):

        self._next_time = time.get_ticks()
        self._last_delta_time = (self._next_time - self._previous_time) / 1000
        self._previous_time = self._next_time
        self._global += self._last_delta_time
        self.clock.tick()

    def fps(self):
        return self.clock.get_fps()
