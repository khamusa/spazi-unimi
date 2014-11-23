from model.drawable import DrawableRoom
from model.drawable import DrawableText
from model.drawable import Point
from utils.myitertools import circular_pairwise, partition
import itertools
import unittest

class DrawableRoomTestPointsInside(unittest.TestCase):
   def setUp(self):
      # 10x10 square beginning on origin
      self.room1 = DrawableRoom([(0,0),(10,0),(10,10),(0,10)],
         [
            DrawableText("1234",Point(3,3)),
            DrawableText("Super Cool",Point(4,7)),
            DrawableText("Corner Text!",Point(1,10))
         ])

      # 10x10 diamond shape centered at origin
      self.room2 = DrawableRoom([(10,0), (0, 10), (-10, 0), (0, -10)])

      # L-shaped room
      self.room3 = DrawableRoom([(0,0),(10,0),(10,5),(5,5),(5,10),(0,10)])

   def test_room_contains_point(self):
      def room_contains(room, x, y):
            self.assertTrue( room._contains_point(Point(x, y)), "Room should contain {}, {}".format(x, y) )

      def room_not_contains(room, x, y):
            self.assertFalse( room._contains_point(Point(x, y)), "Room should not contain {}, {}".format(x, y) )

      # Generic points inside the square room
      for x, y in circular_pairwise(range(1,10)):
         room_contains(self.room1, x, y)

      test_data = [
         {
            "room"   : self.room1,
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
            "room"   : self.room2,
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
            "room"   : self.room3,
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
         }
      ]

      for test_room in test_data:
         for (x, y) in test_room["truths"]:
            room_contains(test_room["room"], x, y)

         for (x, y) in test_room["falses"]:
            room_not_contains(test_room["room"], x, y)
