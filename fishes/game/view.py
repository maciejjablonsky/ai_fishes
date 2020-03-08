from math import degrees

from pygame import display, image, transform, font, color


def view_from_json(config):
    return View(config=config)


class View:
    def __init__(self, config=None):
        if config is None:
            raise TypeError("View can be only configured with config.json.")
        self.window = display.init()
        self.window_dimensions = (config['window']['width'], config['window']['height'])
        self.window = display.set_mode(size=self.window_dimensions)

        display.set_caption(config['name'])
        self.textures = config['textures']
        for key, value in self.textures.items():
            value['texture'] = transform.scale(
                image.load(value['path']),
                (round(value['width']), round(value['height'])))

        self.screen = display.get_surface()
        self.screen.blit(self.textures['background']['texture'], (0, 0))
        font.init()
        self.font = font.Font(None, 30)
        display.flip()

    def blit(self, texture, point, angle=0):
        # pygame counts angle counterclockwise so angle is negative

        if 90 <= abs(degrees(angle)) <= 180:
            texture = transform.flip(texture, False, True)
        rotated = transform.rotate(texture, degrees(-angle))
        self.screen.blit(rotated, point)

    def blit_fps(self, fps):
        fps_view = self.font.render("FPS: {0:.2f}".format(fps), True, color.Color('red'))
        self.screen.blit(fps_view, (10, 10))

    def view(self):
        display.flip()
