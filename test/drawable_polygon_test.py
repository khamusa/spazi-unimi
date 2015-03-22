from model.drawable import Point, Polygon
from mock           import MagicMock
from itertools      import chain
import unittest

class PolygonTest(unittest.TestCase):

   def setUp(self):
      self.polygon1 = Polygon.from_relative_coordinates(
         (100, 200),
         [ (0, 0), (10, 0), (10, 10), (0, 10) ]
      )

      self.polygon2 = Polygon.from_absolute_coordinates(
         [ (-20, 30), (0, -10), (20, -30), (40, -10) ]
      )

   def test_simplify_close_points(self):
      p1 = Polygon.from_relative_coordinates( Point(0,0),
         [ (-20, 30), (-20.35, 30.25), (0, -10), (-0.3, -10.36), (40, -10) ]
      ).simplify_close_points()

      self.assertEqual(p1.points, [ (-20, 30), (0, -10), (40, -10) ])

      p2 = Polygon.from_relative_coordinates( Point(0,0),
         [ (-20, 30), (-20.25, 30.15), (0, -10), (-0.13, -10.16), (15, 15), (-20, 30) ]
      ).simplify_close_points()

      self.assertEqual(p2.points, [ (0, -10), (15, 15), (-20, 30), (0, -10) ])

      p3 = Polygon.from_relative_coordinates( Point(0,0),
         [ (0, 0), (0, 0.49), (0, 0.495), (0, 0.396), (0, 0.9), (0, 1.3), (0, 1.41) ]
      ).simplify_close_points()

      self.assertEqual(p3.points, [ (0, 0), (0, 0.9), (0, 1.41) ])

   def test_is_self_crossing(self):
      l_shaped = Polygon.from_absolute_coordinates(
         [ (0, 0), (10, 0), (10, 10), (5, 10), (5, 5), (0,5), (0,0) ] )
      crossing = Polygon.from_absolute_coordinates(
         [ (0, 0),          (10, 10), (5, 10), (5, 5), (0,5) ] )

      self.assertFalse(l_shaped.is_self_crossing())
      self.assertTrue(crossing.is_self_crossing())
      print(crossing.is_self_crossing())

   def test_point_to_right_of_line(self):
      self.assertTrue(Polygon._compare_line_and_point( Point(10, 0), Point(0, 10), Point(9.9, 9.9)) > 0 )
      self.assertTrue(Polygon._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 2)) > 0 )
      self.assertTrue(Polygon._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8)) > 0 )
      self.assertTrue(Polygon._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8.999)) > 0 )

      # Diagonal line
      self.assertFalse(Polygon._compare_line_and_point( Point(1, 1), Point(9, 9), Point(1, 2)) > 0 )
      self.assertFalse(Polygon._compare_line_and_point( Point(0, 0), Point(9, 9), Point(1, 8)) > 0 )
      self.assertFalse(Polygon._compare_line_and_point( Point(9, 9), Point(5, 5), Point(1, 6)) > 0 )
      self.assertTrue(Polygon._compare_line_and_point( Point(0, 0), Point(2, 10), Point(1, 5)) == 0 )

      # Horizontal line with point aligned
      self.assertTrue(Polygon._compare_line_and_point( Point(0, 0), Point(10, 0), Point(4, 0)) == 0 )

      # vertical line with point aligned
      self.assertTrue(Polygon._compare_line_and_point( Point(0, 0), Point(0, 10), Point(0, 5)) == 0 )

   def test_polygon_equality(self):
      p2 = Polygon();
      p2.points = self.polygon1.points
      p2.anchor_point = self.polygon1.anchor_point
      self.assertEqual(self.polygon1.points, p2.points)
      self.assertEqual(self.polygon1.anchor_point, p2.anchor_point)
      self.assertEqual(self.polygon1, p2)


   def test_polygon_creation(self):
      # Absolute coordinates
      self.assertEqual(self.polygon2.anchor_point, Point(-20, -30))
      self.assertEqual(
            self.polygon2.points,
            [ Point(0, 60), Point(20, 20), Point(40, 0), Point(60, 20) ]
         )

      # Relative coordinates
      self.assertEqual(self.polygon1.anchor_point, Point(100, 200))
      self.assertEqual(self.polygon1.points,
         [ Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10) ]
      )

   def test_polygon_cloning(self):
      p2 = self.polygon1.clone()
      self.assertTrue(p2 is not self.polygon1)
      self.assertEqual(self.polygon1, p2)

   def test_polygon_translation(self):
      #[ (0, 0), (10, 0), (10, 10), (0, 10) ]
      anchor_point = self.polygon1.anchor_point.clone()
      self.polygon1.traslate(30, 40)
      self.assertTrue(Point(30, 40) in self.polygon1.points)

      self.polygon1.traslate(-230, 0)
      self.assertTrue(Point(40-230, 40) in self.polygon1.points)

      p2 = self.polygon1.traslate(0, -340)
      self.assertTrue(Point(10+30-230, 10+40-340) in self.polygon1.points)
      self.assertTrue(p2 is self.polygon1)

      # Immutable version
      p3 = self.polygon1.traslated(100, 100)
      self.assertTrue(Point(30-230, 10+40-340) in self.polygon1.points)
      self.assertFalse(p3 is self.polygon1)

      # After all translations, make sure the anchor point didn't change
      self.assertEqual(self.polygon1.anchor_point, anchor_point)

   def test_polygon_reflection(self):
      p1 = self.polygon1.reflect_y()
      self.assertEqual(self.polygon1.anchor_point, Point(100, 200))
      self.assertEqual(self.polygon1.points,
         [ Point(0, 0), Point(10, 0), Point(10, -10), Point(0, -10) ]
      )
      self.assertTrue(p1 is self.polygon1)

      p2 = self.polygon1.reflected_y()
      self.assertTrue(self.polygon1 is not p2)
      self.assertEqual(p2.points,
         [ Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10) ]
      )

   def test_polygon_scale(self):
      p1 = self.polygon1.scale(3, 2)
      self.assertEqual(self.polygon1.anchor_point, Point(100, 200))
      self.assertEqual(self.polygon1.points,
         [ Point(0, 0), Point(30, 0), Point(30, 20), Point(0, 20) ]
      )
      self.assertTrue(p1 is self.polygon1)

      self.polygon1.scale(-1)

      # Immutability
      p2 = self.polygon1.scaled(.5)
      self.assertTrue(p2 is not self.polygon1)
      self.assertEqual(p2.anchor_point, Point(100, 200))
      self.assertEqual(p2.points,
         [ Point(0, 0), Point(-15, 0), Point(-15, -10), Point(0, -10) ]
      )

      # test previous scale on polygon1
      self.assertEqual(self.polygon1.anchor_point, Point(100, 200))
      self.assertEqual(self.polygon1.points,
         [ Point(0, 0), Point(-30, 0), Point(-30, -20), Point(0, -20) ]
      )

   def test_polygon_rotate(self):
      # [ (0, 0), (10, 0), (10, 10), (0, 10) ]
      p1 = self.polygon1.rotate(90)
      self.assertEqual(self.polygon1.anchor_point, Point(100, 200))
      self.assertEqual(self.polygon1.points,
         [ Point(0, 0), Point(0, 10), Point(-10, 10), Point(-10, 0) ]
         )
      self.assertTrue(p1 is self.polygon1)

      p2 = self.polygon1.rotated(90)
      self.assertEqual(self.polygon1.points,
         [ Point(0, 0), Point(0, 10), Point(-10, 10), Point(-10, 0) ]
         )
      self.assertTrue(p2 is not self.polygon1)
      self.assertEqual(p2.anchor_point, Point(100, 200))
      self.assertEqual(p2.points,
         [ Point(0, 0), Point(-10, 0), Point(-10, -10), Point(0, -10) ]
         )

   def test_calculate_bounding_box(self):
      self.assertEqual(self.polygon1.bounding_box, (Point(0, 0), Point(10, 10)))
      self.assertEqual(self.polygon2.bounding_box, (Point(0, 0), Point(60, 60)))
      self.polygon1._calculate_bounding_box = MagicMock()
      self.polygon1.traslate(10, 10)
      self.polygon1.scale(4)
      self.assertEqual(self.polygon1._calculate_bounding_box.call_count, 0)
      self.polygon1.reflect_y()
      self.polygon1.rotate(90)
      self.assertEqual(self.polygon1._calculate_bounding_box.call_count, 2)

   def test___entities__method(self):
      # We want to make sure polygon defines this method, that's the only
      # reason this test exists
      result = chain(
         self.polygon1.points,
         self.polygon1.bounding_box,
         [self.polygon1.center_point]
      )

      self.assertEqual(list(result), list(self.polygon1.__entities__()))
