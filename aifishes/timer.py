from pygame import time
from pygame.time import Clock


class Time():
    def __init__(self):
        self.clock = Clock()
        self._previous_time: float = 0
        self._next_time: float = 0
        self._last_delta_time: float = 0
        self._global = 0
        self._running = False
        self._paused = False
        self._paused_time = 0

    def reset(self):
        self._next_time = 0
        self._previous_time = 0

    def start(self):
        self._running = True
        self._previous_time = time.get_ticks()

    def stop(self):
        self._running = False

    def toggle_pause(self):
        self._paused = not self._paused

    @property
    def dtime(self):
        if not self._paused:
            return self._last_delta_time
        else:
            return 0

    @property
    def running(self):
        return self._running

    def update(self):
        self._next_time = self.get_ticks()
        self._last_delta_time = (self._next_time - self._previous_time) / 1000
        if self._paused:
            self._paused_time += self._last_delta_time
        self._previous_time = self._next_time
        self._global += self._last_delta_time
        self.clock.tick()

    def get_ticks(self):
        return time.get_ticks() - self._paused_time


    def fps(self):
        return self.clock.get_fps()
