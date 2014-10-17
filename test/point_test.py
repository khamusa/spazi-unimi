import unittest
from point import Point

class PointTest(unittest.TestCase):
   def test_point_creation(self):
      # Test rounding function actually being applied
      self.assertTrue( 3.333 == Point(3.33333, 1).x )
      self.assertTrue( 3.333 == Point(1, 3.3333333).y )

      self.assertTrue( 10 == Point( (10, 20, 30) ).x )
      self.assertTrue( 20 == Point( (10, 20, 30) ).y )

   def test_point_traslation(self):
      p = Point(3, 4)

      p.traslate(10, 20)

      self.assertTrue(p.x == 13)
      self.assertTrue(p.y == 24)

      p.traslate(-33, -44)

      self.assertTrue(p.x == -20)
      self.assertTrue(p.y == -20)

   def test_traslated_points(self):
      p = Point(3, 4)

      p2 = p.traslated(10, 20)

      self.assertTrue(p.x + 10 == p2.x)
      self.assertTrue(p.y + 20 == p2.y)

      p2 = p.traslated(-33, -44)

      self.assertTrue(p.x - 33 == p2.x)
      self.assertTrue(p.y - 44 == p2.y)

   def test_point_cloning(self):
      p = Point(3, 4)
      p2 = p.clone()

      self.assertTrue(p == p2)
      self.assertTrue(p is not p2)

