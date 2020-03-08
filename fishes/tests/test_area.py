from unittest import TestCase

from fishes.data.physics.area import Rectangle
from fishes.data.physics.point import Point


class TestRectangle(TestCase):
    def setUp(self):
        self.rectangle = Rectangle(Point(0, 0), Point(10, 10))

    def test_contains(self):
        self.assertTrue(self.rectangle.contains(Point(5, 5)))
        self.assertTrue(self.rectangle.contains(Point(10, 10)))
        self.assertFalse(self.rectangle.contains(Point(10, 15)))
