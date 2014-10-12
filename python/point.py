class Point():
   def __init__(self, a, b = None):
      a, b = b is None and (a[0], a[1]) or (a, b)
      self.x = self._round(a)
      self.y = self._round(b)

   def _round(self, a):
      return round(a, 3)

   def __eq__(self, other):
      return other.x == self.x and other.y == self.y

   def __str__(self):
      return "P({}, {})".format(self.x, self.y)

   def __repr__(self):
      return self.str()

   def traslated(self, x_amount, y_amount):
      """Returns a new point representing the current point translated"""
      return Point(self.x + x_amount, self.y + y_amount)

   def reflected_y(self):
      """Returns a new point, with y coordinate reflected_y"""
      return Point(self.x, -self.y)

   def rotated_clockwise(self):
      """Returns a new point, rotated 90 grades clockwise, with origin as reference"""
      return Point(self.y, -self.x)

   def cross_product(self, other):
      """Returns an integer obtained as the cross product of the two points"""
      return self.x * other.y - self.y * other.x


if __name__ == '__main__':
   unittest.main()

import unittest
class PointTest(unittest.TestCase):
   def test_point_creation(self):
      # Test rounding function actually being applied
      self.assertTrue( 3.333 == Point(3.33333, 1).x )
      self.assertTrue( 3.333 == Point(1, 3.3333333).y )