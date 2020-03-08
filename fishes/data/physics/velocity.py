from fishes.data.physics.point import Point


class Velocity(Point):

    def reposition(self, dtime):
        return self * dtime

    def reflect_x(self, x=0):
        reflected = super().reflect_x(x)
        return Velocity(reflected.x, reflected.y)

    def reflect_y(self, y=0):
        reflected = super().reflect_y(y)
        return Velocity(reflected.x, reflected.y)

    def __str__(self):
        return "Velocity({0}, {1})".format(self.x, self.y)
