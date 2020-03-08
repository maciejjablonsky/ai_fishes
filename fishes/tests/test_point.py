from math import degrees, radians, sqrt, sin, cos
from unittest import TestCase

from fishes.data.physics.point import Point


class TestPoint(TestCase):
    def setUp(self):
        self.point = Point(2, 2)

    def test_set_cartesian(self):
        self.point.set_cartesian(5, 5)
        self.assertEqual(self.point.cartesian, (5, 5))
        self.assertEqual(self.point.polar, (sqrt(50), radians(45)))

    def test_set_polar(self):
        self.point.set_polar(2, radians(30))
        self.assertEqual(self.point.polar, (2, radians(30)))
        self.assertEqual(self.point.cartesian, (2 * cos(radians(30)), 2 * sin(radians(30))))

    def test_distance_to(self):
        another_point = Point(7, 7)
        self.assertEqual(self.point.distance_to(another_point), sqrt(50))

    def test_mul(self):
        self.assertEqual(self.point * 2, (4, 4))
        self.assertEqual(self.point * -2, (-4, -4))
        self.assertEqual(self.point * 0, (0, 0))

    def test_add(self):
        another_point = Point(7, 7)
        self.assertEqual(self.point + (2, 2), (4, 4))
        self.assertEqual(self.point + another_point, (9, 9))

    def test_sub(self):
        self.assertEqual(self.point, (2, 2))
        self.assertEqual(self.point - (2, 2), (0, 0))
        self.assertEqual(self.point - Point(2, 2), (0, 0))
        self.assertEqual(self.point - Point(2, 2), Point(0, 0))
        self.assertEqual(self.point - (2, 0), (0, 2))
        self.assertEqual(self.point - (3, 3), (-1, -1))
        self.assertEqual((1, 1) - self.point, (-1, -1))

    def test_reflect_x(self):
        self.assertEqual(self.point.reflect_x(), (-2, 2))
        self.assertEqual(self.point.reflect_x(3), (4, 2))
        self.assertEqual(self.point.reflect_x(-3), (-8, 2))

    def test_reflect_y(self):
        self.assertEqual(self.point.reflect_y(), (2, -2))
        self.assertEqual(self.point.reflect_y(3), (2, 4))
        self.assertEqual(self.point.reflect_y(-3), (2, -8))

    def test_reflect(self):
        self.assertEqual(self.point.reflect(), (-2, -2))
        self.assertEqual(self.point.reflect((3, 3)), (4, 4))
        self.assertEqual(self.point.reflect((-3, -3)), (-8, -8))

    def test_eq(self):
        self.assertEqual(self.point, (2,2))
        another_point = Point(2,2)
        self.assertEqual(self.point, another_point)
        self.assertEqual(self.point, (2,2))
        self.assertNotEqual(self.point, (0,2))
