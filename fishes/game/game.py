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
                x=config['view']['window']['width'],
                y=config['view']['window']['height']
            )
        )
        self._fishes = [fish_from_json(config, self._borders) for i in
                        range(number_of_fishes)]
        self._view = view_from_json(config['view'])
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

    def stop(self):
        self._time.stop()

    def handle_events(self):
        pass

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
