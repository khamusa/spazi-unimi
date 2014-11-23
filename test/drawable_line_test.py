import unittest
from model.drawable import DrawableLine, Point

class DrawableLineTest(unittest.TestCase):
   def test_line_creation(self):
      l1 = DrawableLine( (1, 2), (3, 4) )
      self.assertEqual(l1.start[0], 1)
      self.assertEqual(l1.start[1], 2)
      self.assertEqual(l1.end[0], 3)
      self.assertEqual(l1.end[1], 4)

      p1 = Point(1, 2)
      p2 = Point(3, 4)
      l2 = DrawableLine( p1, p2 )
      self.assertEqual(l2.start[0], 1)
      self.assertEqual(l2.start[1], 2)
      self.assertEqual(l2.end[0], 3)
      self.assertEqual(l2.end[1], 4)

   def test_line_eq(self):
      l1 = DrawableLine( (1, 2), (3, 4) )
      l2 = DrawableLine( Point(1, 2), Point(3, 4) )
      l3 = DrawableLine( Point(3, 4), Point(1, 2) )
      self.assertEqual(l1, l2)
      self.assertEqual(l1, l3)
      self.assertEqual(l3, l2)

      l4 = DrawableLine( (1, 2), (3, 5) )
      self.assertNotEqual(l1, l4)

      l4 = DrawableLine( (1, 2), (2, 4) )
      self.assertNotEqual(l2, l4)

      l4 = DrawableLine( (1, 3), (3, 4) )
      self.assertNotEqual(l3, l4)

      l4 = DrawableLine( (2, 2), (3, 4) )
      self.assertNotEqual(l1, l4)


   def test_line_traslation(self):
      l1 = DrawableLine( (1, 2), (3, 4) )
      l1.traslate(10, 0)
      self.assertEqual( l1, DrawableLine((11, 2), (13, 4)) )
      l1.traslate(0, 10)
      self.assertEqual( l1, DrawableLine((11, 12), (13, 14)) )
      l1.traslate(-10, -10)
      self.assertEqual( l1, DrawableLine((1, 2), (3, 4)) )

   def test_line_rotation(self):
      l1 = DrawableLine( (0, 0), (10, 0) )
      l1.rotate(90)
      self.assertEqual(l1, DrawableLine((0.0, 0.0), (0.0, 10.0)) )

      l1.rotate(-180)
      self.assertEqual(l1, DrawableLine((0.0, 0.0), (0.0, -10.0)) )

      l1.rotate(360)
      self.assertEqual(l1, DrawableLine((0.0, 0.0), (0.0, -10.0)) )

   def test_line_scale(self):
      l1 = DrawableLine( (3, 0), (10, 0) )
      l1.scale(2, 3)
      self.assertEqual(l1, DrawableLine( (6, 0), (20, 0) ) )

      l2 = DrawableLine( (3, 3), (10, 8) )
      l2.scale(2, 3)
      self.assertEqual(l2, DrawableLine( (6, 9), (20, 24) ) )
