import json
from unittest import TestCase

from fishes.data.fish import Fish
from fishes.data.physics.area import Rectangle
from fishes.data.physics.point import Point
from fishes.data.physics.velocity import Velocity


class TestFish(TestCase):
    def setUp(self):
        with open("fishes/game/config.json", 'r') as config_file:
            json_file = json.load(config_file)
            self.borders = Rectangle(Point(0, 0), Point(50, 50))
            self.fish = Fish(json_file, self.borders)
            self.fish.dimensions = (8, 8)

    def test_dodge_border__top(self):
        self.fish.coords = Point(25, 2)
        self.fish.velocity = Velocity(2, -4)
        next_position = Point(27, -2)
        next_position = self.fish.dodge_borders(next_position)
        self.assertEqual((27, 2), next_position)
        self.assertEqual((2, 4), self.fish.velocity)

    def test_dodge_borders__right(self):
        self.fish.coords = Point(41, 25)
        self.fish.velocity = Velocity(4, 2)
        next_position = Point(45, 27)
        next_position = self.fish.dodge_borders(next_position)
        self.assertEqual((41, 27), next_position)
        self.assertEqual((-4, 2), self.fish.velocity)

    def test_dodge_borders__bottom(self):
        self.fish.coords = Point(40, 42)
        self.fish.velocity = Velocity(2, 2)
        next_position = Point(42, 44)
        next_position = self.fish.dodge_borders(next_position)
        self.assertEqual((42, 42), next_position)
        self.assertEqual((2, -2), self.fish.velocity)

    def test_dodge_border__left(self):
        self.fish.coords = Point(2, 25)
        self.fish.velocity = Velocity(-5, 3)
        next_position = Point(-3, 28)
        next_position = self.fish.dodge_borders(next_position)
        self.assertEqual((3, 28), next_position)
        self.assertEqual((5, 3), self.fish.velocity)
