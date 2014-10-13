import unittest
from point import Point

class PointTest(unittest.TestCase):
   def test_point_creation(self):
      # Test rounding function actually being applied
      self.assertTrue( 3.333 == Point(3.33333, 1).x )
      self.assertTrue( 3.333 == Point(1, 3.3333333).y )

      self.assertTrue( 10 == Point( (10, 20, 30) ).x )
      self.assertTrue( 20 == Point( (10, 20, 30) ).y )