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


if __name__ == '__main__':
   unittest.main()

import unittest
class PointTest(unittest.TestCase):
   def test_point_creation(self):
      # Test rounding function actually being applied
      self.assertTrue( 3.333 == Point(3.33333, 1).x )
      self.assertTrue( 3.333 == Point(1, 3.3333333).y )
