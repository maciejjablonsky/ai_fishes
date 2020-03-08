from unittest import TestCase

from fishes.data.physics.point import Point
from fishes.data.physics.velocity import Velocity


class TestVelocity(TestCase):
    def setUp(self):
        self.velocity = Velocity(50, 50)

    def test_reposition(self):
        dtime = 0.5
        reposition = self.velocity.reposition(dtime)
        self.assertIsInstance(reposition, Point)
        self.assertEqual((25, 25), self.velocity.reposition(dtime))

    def test_reflect_x(self):
        reflected = self.velocity.reflect_x()
        self.assertIsInstance(reflected, Velocity)
        self.assertEqual(reflected, Velocity(-50, 50))

    def test_reflect_x(self):
        reflected = self.velocity.reflect_y()
        self.assertIsInstance(reflected, Velocity)
        self.assertEqual(reflected, Velocity(50, -50))

    def test_eq(self):
        self.assertEqual(self.velocity, (50, 50))
        another_velocity = Velocity(50, 50)
        self.assertEqual(self.velocity, another_velocity)
