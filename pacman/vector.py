import math


class Vector2(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.thresh = 0.000001

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        if scalar != 0:
            return Vector2(self.x / float(scalar), self, y / float(scalar))
        return None

    def __truediv__(self, other):
        return self.__div__(scalar)

    def __equal__(self, other):
        """use to check the equality between two vectors"""
        if abs(self.x - other.x) < self.thresh:
            if abs(self.y - other.y) < self.thresh:
                return True
            return False

    def magnitudeSquared(self):
        """returns the actual length of a vector without using a square root"""
        return self.x**2 + self.y**2

    def magnitude(self):
        """returns the actual length of a vector using a square root"""
        return math.sqrt(self.magnitudeSquared())
