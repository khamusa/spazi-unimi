from model.drawable     import Point, Polygon
from utils.myitertools  import circular_pairwise
import unittest

class PolygonPointsInsideTest(unittest.TestCase):
   def setUp(self):
      # 10x10 square beginning on origin
      self.polygon1 = Polygon.from_relative_coordinates((0, 0), [(0,0),(10,0),(10,10),(0,10)])

      # 10x10 diamond shape centered at origin
      self.polygon2 = Polygon.from_relative_coordinates((0, 0), [(10,0), (0, 10), (-10, 0), (0, -10)])

      # L-shaped polygon
      self.polygon3 = Polygon.from_relative_coordinates((0, 0), [(0,0),(10,0),(10,5),(5,5),(5,10),(0,10)])

      self.polygon4 = Polygon.from_absolute_coordinates([(0,0),(5,0),(5,5),(10,5),(10,10),(0,10)])

   def test_polygon_contains_point(self):
      def polygon_contains(polygon, x, y):
            self.assertTrue( polygon._contains_point(Point(x, y)), "{} should contain {}, {}".format(polygon, x, y) )

      def polygon_not_contains(polygon, x, y):
            self.assertFalse( polygon._contains_point(Point(x, y)), "{} should not contain {}, {}".format(polygon, x, y) )

      # Generic points inside the square polygon
      for x, y in circular_pairwise(range(1,10)):
         polygon_contains(self.polygon1, x, y)

      test_data = [
         {
            "polygon"   : self.polygon1,
            "truths" : [
               # Inside, but near borders
               (0.1, 0.001),
               (9.99, 9.7),
               (5, 9.99),
               (0.1, 8),

               # Close to the border
               (0.001, 0.001),
               (9.999, 9.999),

               # Points precisely on the border
               (5, 0),
               (10, 5),
               (5, 10),
               (0, 5),
               (0, 0),
               (10, 0),
               (10, 10),
               (0, 10)
            ],
            "falses" : [
               (5, -4),
               (5, 11),
               (10.001, 10.001),
               (-2, 5)
            ]
         },
         {
            "polygon"   : self.polygon2,
            "truths" : [
               # Close to the vertices
               (9.9, 0), (0, 9.9), (-9.9, 0), (0, -9.9),
               # Close to the center
               (0.001, 0.001), (3, 3), (-4.8, -4.8), (4.1, 3.8),

               # Points precisely over the border
               (10, 0), (0, 10), (-10, 0), (0, -10)
            ],
            "falses" : [
               # Points definetely outside
               (9.9, 9.9), (10.2, 0), (0, -10.1), (10.001, 10.001), (33, 12)
            ]
         },

         {
            "polygon"   : self.polygon3,
            "truths" : [
               # Close to the vertices
               (1, 2), (0.1, 0.1), (9.9, 0.1), (0.1, 9.9),
               # Close to the center
               (2, 3), (4, 5), (8, 2), (1, 7),

               # Points precisely over the vertices
               (0,0),(10,0),(10,5),(5,5),(5,10),(0,10)
            ],
            "falses" : [
               # Points definetely outside
               (10.1, 0.3), (-0.1, 1), (2, 10.1), (-0.1, -0.1), (1, -0.1),
               (6,6), (5.1, 5.1)
            ]
         },


         {
            "polygon"   : self.polygon4,
            "truths" : [
               (5, 5)
            ],
            "falses" : [
               # Points definetely outside
               (11, 5)
            ]
         }
      ]

      for test_polygon in test_data:
         for (x, y) in test_polygon["truths"]:
            polygon_contains(test_polygon["polygon"], x, y)

         for (x, y) in test_polygon["falses"]:
            polygon_not_contains(test_polygon["polygon"], x, y)
