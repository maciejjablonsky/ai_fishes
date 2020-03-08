from unittest import TestCase
from fishes.game.timer import Time
import time


def is_between(low, value, high):
    return low <= value <= high


class TestTime(TestCase):
    def setUp(self):
        self.time = Time()

    def test_dtime(self):
        sleep_time = 1 #
        self.time.start()
        time.sleep(sleep_time)
        self.time.update()
        self.time.stop()
        dtime = self.time.dtime
        epsilon = 0.003
        self.assertGreaterEqual(dtime, sleep_time - epsilon)
        self.assertLessEqual(dtime, sleep_time + epsilon)

