import unittest, math
from model.drawable.segment import Segment
from model.drawable.point import Point

class DrawableSegmentTest(unittest.TestCase):

   def test_segment_creation(self):
      s  = Segment.from_tuples( (1,2), (3, 4) )
      s2 = Segment.from_coordinates( 1, 2, 3, 4 )
      self.assertEqual(s.start, s2.start)
      self.assertEqual(s.end, s2.end)
      self.assertEqual(s.start.x, 1)
      self.assertEqual(s.start.y, 2)
      self.assertEqual(s.end.x, 3)
      self.assertEqual(s.end.y, 4)

   def test_segment_equality(self):
      s  = Segment.from_tuples( (1,2), (3, 4) )
      s2 = Segment.from_coordinates( 1, 2, 3, 4 )

      self.assertEqual(s, s2)
      self.assertEqual(s2, s)
      self.assertEqual(s, (Point(1, 2), Point(3, 4.0009)) )
      self.assertNotEqual(s, (Point(1, 2), Point(3, 4.0011)) )

   def test_segment_length(self):
      s = Segment.from_coordinates(0, 0, 1, 1)
      self.assertEqual(s.length(), math.sqrt(2))

      s = Segment.from_coordinates(0, 0, 0, 2)
      self.assertEqual(s.length(), 2)

      s = Segment.from_coordinates(0, 0, -3, 0)
      self.assertEqual(s.length(), 3)

   def test_slope_calc(self):
      s = Segment.from_coordinates(0, 0, 1, 2)
      self.assertEqual(s.slope, 2)

      s = Segment.from_coordinates(0, 0, 3, 9)
      self.assertEqual(s.slope, 3)

      s = Segment.from_coordinates(0, 0, 3, 3)
      self.assertEqual(s.slope, 1)

      s = Segment.from_coordinates(0, 0, 0, 2)
      self.assertEqual(s.slope, float("+inf"))

   def test_vertical_lines(self):
      s = Segment.from_coordinates(0, 0, 3, 3)
      self.assertEqual(s.is_vertical(), False)
      self.assertEqual(s.x_value, None)

      s = Segment.from_coordinates(0, 0, 0, 2)
      self.assertEqual(s.is_vertical(), True)
      self.assertEqual(s.x_value, 0)

      s = Segment.from_coordinates(4, 0, 4, 2)
      self.assertEqual(s.is_vertical(), True)
      self.assertEqual(s.x_value, 4)

   def test_y_intercept_parameter(self):
      s = Segment.from_coordinates(0, 0, 1, 2)
      self.assertEqual(s.y_intercept, 0)

      s = Segment.from_coordinates(0, 2, 1, 2)
      self.assertEqual(s.y_intercept, 2)

      s = Segment.from_coordinates(0, 8, 1, 2)
      self.assertEqual(s.y_intercept, 8)

   def test_is_point_on_same_line(self):
      s = Segment.from_coordinates(0, 0, 0, 2)
      self.assertFalse(s.is_point_on_same_line(1, 2))
      self.assertFalse(s.is_point_on_same_line(Point(1, 2)))
      self.assertFalse(s.is_point_on_same_line(Point(3, 4)))
      self.assertTrue(s.is_point_on_same_line(0, 99))
      self.assertTrue(s.is_point_on_same_line(0, -999))
      self.assertTrue(s.is_point_on_same_line(Point(0, 4)))

      s = Segment.from_coordinates(3, 0, 3, 2)
      self.assertFalse(s.is_point_on_same_line(1, 2))
      self.assertFalse(s.is_point_on_same_line(Point(1, 2)))
      self.assertTrue(s.is_point_on_same_line(3, 72))
      self.assertTrue(s.is_point_on_same_line(3, 0))

      s = Segment.from_coordinates(0, 0, 1, 1)
      self.assertFalse(s.is_point_on_same_line(1, 2))
      self.assertFalse(s.is_point_on_same_line(Point(1, 3)))
      self.assertFalse(s.is_point_on_same_line(Point(-3, 3)))
      self.assertTrue(s.is_point_on_same_line(3, 3))
      self.assertTrue(s.is_point_on_same_line(-3, -3))
      self.assertTrue(s.is_point_on_same_line(0, 0))

   def test_contains_point(self):
      s = Segment.from_coordinates(0, 0, 0, 2)
      self.assertFalse(s.contains_point(1, 2))
      self.assertFalse(s.contains_point(Point(1, 2)))
      self.assertFalse(s.contains_point(Point(3, 4)))

      self.assertFalse(s.contains_point(0, 2.001))
      self.assertFalse(s.contains_point(0, -0.05))
      self.assertTrue(s.contains_point(0, 1))
      self.assertTrue(s.contains_point(0, 1.9))
      self.assertTrue(s.contains_point(Point(0, 0.1)))

      s = Segment.from_coordinates(3, 0, 3, 2)
      self.assertFalse(s.contains_point(1, 2))
      self.assertFalse(s.contains_point(Point(1, 2)))
      self.assertFalse(s.contains_point(3, 2.1))
      self.assertFalse(s.contains_point(3, -0.1))
      self.assertTrue(s.contains_point(3, 2))
      self.assertTrue(s.contains_point(3, 0))
      self.assertTrue(s.contains_point(3, 1))

      s = Segment.from_coordinates(0, 0, 1, 1)
      self.assertFalse(s.contains_point(1, 2))
      self.assertFalse(s.contains_point(Point(1, 3)))
      self.assertFalse(s.contains_point(Point(-3, 3)))
      self.assertTrue(s.contains_point(0.999, 0.999))
      self.assertTrue(s.contains_point(0.001, 0.001))
      self.assertTrue(s.contains_point(0.5, 0.5))

   def test_lines_intersection(self):
      s1 = Segment.from_coordinates(0, 0, 1, 1)
      s2 = Segment.from_coordinates(0, 0, -1, 1)
      s3 = Segment.from_coordinates(0, 0, 1, -1)
      s4 = Segment.from_coordinates(0, 0, -1, -1)

      self.assertEqual(s1._lines_intersection(s2), Point(0, 0))
      self.assertTrue(s2._lines_intersection(s3) )
      self.assertEqual(s3._lines_intersection(s4), Point(0, 0))
      self.assertTrue(s4._lines_intersection(s1) )

      # More parallel lines
      p1 = Segment.from_coordinates(-20, -20, 5, 5)
      p2 = Segment.from_coordinates(40, 40, 41, 41)
      self.assertTrue( s1._lines_intersection(p1) is True )
      self.assertTrue( s1._lines_intersection(p2) is True )
      self.assertTrue( p2._lines_intersection(p1) is True )

      # specific intersections
      # y = mx e y = -mx + 2 devono interseccarsi in y = 1, x = 1
      i1 = Segment.from_coordinates(0, 2, 2, 0)
      self.assertEqual( s1._lines_intersection(i1), Point(1, 1))

      # vertical lines
      v1 = Segment.from_coordinates(0, 0, 0, 2)
      v2 = Segment.from_coordinates(2, 0, 2, 3)
      self.assertFalse( v1._lines_intersection(v2) )

      self.assertEqual( v1._lines_intersection(s1), Point(0,0) )
      self.assertEqual( v1._lines_intersection(s2), Point(0,0) )
      self.assertEqual( v1._lines_intersection(s3), Point(0,0) )
      self.assertEqual( v1._lines_intersection(s4), Point(0,0) )
      self.assertEqual( v1._lines_intersection(s1), Point(0,0) )

      self.assertEqual( v1._lines_intersection(i1), Point(0,2) )
      self.assertEqual( i1._lines_intersection(v1), Point(0,2) )

      def test_line_intersection(
         r1_x1, r1_y1, r1_x2, r1_y2, r2_x1, r2_y1, r2_x2, r2_y2, resx, resy
         ):
         s1 = Segment.from_coordinates(r1_x1, r1_y1, r1_x2, r1_y2)
         s2 = Segment.from_coordinates(r2_x1, r2_y1, r2_x2, r2_y2)

         self.assertEqual(s1._lines_intersection(s2), Point(resx, resy) )

      # We love wolframalpha
      test_line_intersection(1, 2, 2, 1, 2, 0, 4, 3, 2.4, 0.6)
      test_line_intersection(-91,22, 60, -53, -90, 88, -17, -71, -50.4514, 1.85999)
      test_line_intersection(-74,-1, 78, -47, -3, 75, -76, -51, -51.0548, -7.94394)
      test_line_intersection(83,-25, 60, 57, 34, 47, -58, -38, 56.8765, 68.1359)

   def test_segment_intersection(self):

      def test_segment_intersection(
         r1_x1, r1_y1, r1_x2, r1_y2, r2_x1, r2_y1, r2_x2, r2_y2, res
         ):
         s1 = Segment.from_coordinates(r1_x1, r1_y1, r1_x2, r1_y2)
         s2 = Segment.from_coordinates(r2_x1, r2_y1, r2_x2, r2_y2)

         self.assertEqual(s1.intersect_with(s2), res)
         self.assertEqual(s2.intersect_with(s1), res)

      test_segment_intersection(0, 0, 1, 1, 0, 0, -1, 1, Point(0, 0))
      test_segment_intersection(0, 0, 1, 1, 1.1, 1.1, 2, 2, False)
      test_segment_intersection(0, 0, 1, 1, 0.9, 0.9, 2, 2, True)
      test_segment_intersection(0, 0, 1, 1, 1, 1, 2, -2, Point(1, 1))
      test_segment_intersection(0, 0, 1, 1, 0.5, 0.5, 1.5, -1.5, Point(0.5, 0.5))

      test_segment_intersection(0, 0, 1, 7, -1, 6, 1, 1, Point(0.3684, 2.578))
      test_segment_intersection(0, 0, 1, 1, 0.5, 0.5, 1.5, -1.5, Point(0.5, 0.5))
      test_segment_intersection(0, 0, 1, 1, 0.5, 0.5, 1.5, -1.5, Point(0.5, 0.5))








