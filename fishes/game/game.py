import json
from ..data.fish import fish_from_json
from .view import view_from_json
from .timer import Time
from .interaction_controller import EventsController
from ..data.physics.area import Rectangle
from ..data.physics.point import Point


def game_from_json(path="fishes/resources/config.json"):
    try:
        with open(path, "r") as config_file:
            config_json = json.load(config_file)
            return Game(config=config_json)
    except OSError:
        raise OSError("Cannot open {0}".format(path))


class Game:
    def __init__(self, config=None):
        if not isinstance(config, dict):
            raise TypeError("JSON configuration file is needed to create game.")
        number_of_fishes = config['fishes']['number_of_fishes']
        self._borders = Rectangle(
            left_upper=Point(x=0, y=0),
            right_bottom=Point(
                x=config['view']['dimensions']['width'],
                y=config['view']['dimensions']['height']
            )
        )
        self._fishes = [fish_from_json(config['fishes']['regular_fish'], self._borders) for i in range(number_of_fishes)]
        self._view = view_from_json(config)
        self._time = Time()
        self._running = False
        self._controller = EventsController()

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
            # TODO delete this stop after implementing view()
            self.stop()

    def stop(self):
        self._time.stop()

    def handle_events(self):
        pass

    def move_objects(self):
        dtime = self._time.dtime
        for fish in self._fishes:
            fish.move(dtime)

    def view(self):
        pass
