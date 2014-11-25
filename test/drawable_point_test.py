import unittest
from model.drawable import Point

class PointTest(unittest.TestCase):
   def test_point_creation(self):
      # Test rounding function actually being applied
      self.assertTrue( 3.333 == Point(3.33333, 1).x )
      self.assertTrue( 3.333 == Point(1, 3.3333333).y )

      self.assertTrue( 10 == Point( (10, 20, 30) ).x )
      self.assertTrue( 20 == Point( (10, 20, 30) ).y )

   def test_distance_to(self):
      p1 = Point(0, 0)
      self.assertEqual(p1.distance_to(0, 10), 10)
      self.assertEqual(p1.distance_to(p1.x, p1.y), 0)

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
      self.assertTrue(p2 is not p)

      p2 = p.traslated(-33, -44)

      self.assertTrue(p.x - 33 == p2.x)
      self.assertTrue(p.y - 44 == p2.y)

   def test_point_cloning(self):
      p = Point(3, 4)
      p2 = p.clone()

      self.assertTrue(p == p2)
      self.assertTrue(p is not p2)

   def test_point_scaling(self):
      p = Point(10, 20)
      p1 = p.scale(.2)

      self.assertEqual(p.x, 2)
      self.assertEqual(p.y, 4)
      self.assertTrue(p1 is p)

      p.scale(2)

      self.assertEqual(p.x, 4)
      self.assertEqual(p.y, 8)

      p2 = p.scaled(2, 3)

      self.assertEqual(p2.x, 8)
      self.assertEqual(p2.y, 24)
      self.assertTrue(p2 is not p)


   def test_point_rotation(self):
      p = Point(10, 20)
      p1 = p.rotate(90)

      self.assertEqual(p.x, -20)
      self.assertEqual(p.y, 10)
      self.assertTrue(p1 is p)

      p.rotate(90)

      self.assertEqual(p.x, -10)
      self.assertEqual(p.y, -20)

      p2 = p.rotated(-180)

      self.assertEqual(p2.x, 10)
      self.assertEqual(p2.y, 20)
      self.assertTrue(p2 is not p)

   def test_point_reflect_y(self):
      p = Point(3, 4)
      p2 = p.reflect_y()

      self.assertEqual(p, Point(3, -4))
      self.assertTrue(p is p2)

      p2 = p.reflected_y()
      self.assertEqual(p2, Point(3, 4))
      self.assertTrue(p is not p2)
