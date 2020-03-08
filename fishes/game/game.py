import json

from .timer import Time
from .view import view_from_json
from ..data.fish import fish_from_json
from ..data.physics.area import Rectangle
from ..data.physics.point import Point
import pygame as pg

def open_config(path="fishes/game/config.json"):
    try:
        with open(path, "r") as config_file:
            return json.load(config_file)
    except OSError:
        raise OSError("Cannot open {0}".format(path))

def game_from_json(path="fishes/game/config.json"):
    try:
        return Game(config=open_config())
    except OSError:
        raise OSError("Cannot open {0}".format(path))


class Game:
    def __init__(self, config=None):
        if not isinstance(config, dict):
            raise TypeError("JSON configuration file is needed to create game.")
        number_of_fishes = config['fishes']['number_of_fishes']
        self._borders = Rectangle(
            left_upper=Point(
                x=config['fishes']['regular_fish']['coords']['min_x'],
                y=config['fishes']['regular_fish']['coords']['min_y']),
            right_bottom=Point(
                x=config['fishes']['regular_fish']['coords']['max_x'],
                y=config['fishes']['regular_fish']['coords']['max_y']
            )
        )
        self._fishes = [fish_from_json(config, self._borders) for i in
                        range(number_of_fishes)]
        self._view = view_from_json(config['view'])
        self._time = Time()
        self._running = False

    def reset(self):
        config = open_config()
        self._borders = Rectangle(
            left_upper=Point(
                x=config['fishes']['regular_fish']['coords']['min_x'],
                y=config['fishes']['regular_fish']['coords']['min_y']),
            right_bottom=Point(
                x=config['fishes']['regular_fish']['coords']['max_x'],
                y=config['fishes']['regular_fish']['coords']['max_y']
            )
        )
        self._fishes = [fish_from_json(config, self._borders) for i in
                        range(config['fishes']['number_of_fishes'])]
        self._view = view_from_json(config['view'])
        self._time.stop()
        self.run()

    @property
    def running(self):
        return self._time.running

    def run(self):
        self._time.start()
        while self.running:
            self.handle_events()
            self._time.update()
            self.move_objects()
            self.view()

    def stop(self):
        self._time.stop()

    def move_objects(self):
        dtime = self._time.dtime
        for fish in self._fishes:
            fish.move(dtime)

    def view(self):
        # textures = {key: value['texture'] for key, value in self._view.textures.items()}
        textures = self._view.textures
        self._view.blit(textures['background']['texture'], (0, 0))
        for fish in self._fishes:
            self._view.blit(textures['regular_fish']['texture'],
                            (fish.coords.x, fish.coords.y),
                            fish.velocity.phi
                            )
        self._view.blit_fps(self._time.fps())
        self._view.view()

    def stop(self):
        self._time.stop()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.stop()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.stop()
                elif event.key == pg.K_SPACE:
                    self._time.toggle_pause()
                elif event.key == pg.K_r:
                    self.reset()

