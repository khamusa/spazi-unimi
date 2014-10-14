from room import Room
from point import Point
from room_text import RoomText
from myitertools import circular_pairwise

import unittest
class RoomTest(unittest.TestCase):

   def setUp(self):
      self.room1 = Room([(0,0),(10,0),(10,10),(0,10)])
      self.room1.addText(RoomText("1234",Point(3,3)))

      self.room2 = Room([(10,0), (0, 10), (-10, 0), (0, -10)])
      self.room3 = Room([(0,0),(10,0),(10,5),(5,5),(5,10),(0,10)])

   def test_room_creation(self):
      original_points = [(0.3333333, 0.123123), (0.2222333, 10.19), (10.33334, 10.78530), (10.51111, 0.898999)]
      room = Room(original_points)

      # points have been saved?
      self.assertTrue(room.points)

   def test_point_to_right_of_line(self):
      self.assertTrue(Room._compare_line_and_point( Point(10, 0), Point(0, 10), Point(9.9, 9.9)) > 0 )
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 2)) > 0 )
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8)) > 0 )
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8.999)) > 0 )

      # Diagonal line
      self.assertFalse(Room._compare_line_and_point( Point(1, 1), Point(9, 9), Point(1, 2)) > 0 )
      self.assertFalse(Room._compare_line_and_point( Point(0, 0), Point(9, 9), Point(1, 8)) > 0 )
      self.assertFalse(Room._compare_line_and_point( Point(9, 9), Point(5, 5), Point(1, 6)) > 0 )

      # Horizontal line with point aligned
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(10, 0), Point(4, 0)) == 0 )

      # vertical line with point aligned
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(0, 10), Point(0, 5)) == 0 )

   def test_room_traslation(self):
      room_new = self.room1.traslated(20,20)
      for p1, p2 in zip(room_new.points, self.room1.points):
         self.assertTrue(p1.x == p2.x+20)
         self.assertTrue(p1.y == p2.y+20)

      textX,textY = room_new.texts[0].anchor_point.x,room_new.texts[0].anchor_point.y
      self.assertTrue(textX == self.room1.texts[0].anchor_point.x+20)
      self.assertTrue(textY == self.room1.texts[0].anchor_point.y+20)

      room_new = self.room1.traslated(35,0)
      for p1, p2 in zip(room_new.points, self.room1.points):
         self.assertTrue(p1.x == p2.x+35)
         self.assertTrue(p1.y == p2.y+0)


   def test_room_contains_point(self):
      room = self.room1

      def room_contains(room, x, y):
            self.assertTrue( room._contains_point(Point(x, y)), "Room should contain {}, {}".format(x, y) )

      def room_not_contains(room, x, y):
            self.assertFalse( room._contains_point(Point(x, y)), "Room should not contain {}, {}".format(x, y) )

      # Points inside
      for x, y in circular_pairwise(range(1,10)):
         room_contains(room, x, y)

      expected_truth = [
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
      ]

      for x, y in expected_truth:
         room_contains(room, x, y)

      # Points outside
      expected_lie = [
         (5, -4),
         (5, 11),
         (10.001, 10.001),
         (-2, 5)
      ]

      for x, y in expected_lie:
         room_not_contains(room, x, y)

      room2 = self.room2

      expected_truth = [
         # Close to the vertices
         (9.9, 0), (0, 9.9), (-9.9, 0), (0, -9.9),
         # Close to the center
         (0.001, 0.001), (3, 3), (-4.8, -4.8), (4.1, 3.8),

         # Points precisely over the border
         (10, 0), (0, 10), (-10, 0), (0, -10)
      ]

      for x, y in expected_truth:
         room_contains(room2, x, y)

      expected_lie = [
         # Points definetely outside
         (9.9, 9.9), (10.2, 0), (0, -10.1), (10.001, 10.001), (33, 12)
      ]

      for x, y in expected_lie:
         room_not_contains(room2, x, y)


      room3 = self.room3

      expected_truth = [
         # Close to the vertices
         (1, 2), (0.1, 0.1), (9.9, 0.1), (0.1, 9.9),
         # Close to the center
         (2, 3), (4, 5), (8, 2), (1, 7),

         # Points precisely over the vertices
         (0,0),(10,0),(10,5),(5,5),(5,10),(0,10)
      ]

      for x, y in expected_truth:
         room_contains(room3, x, y)

      expected_lie = [
         # Points definetely outside
         (10.1, 0.3), (-0.1, 1), (2, 10.1), (-0.1, -0.1), (1, -0.1),
         (6,6), (5.1, 5.1)
      ]

      for x, y in expected_lie:
         room_not_contains(room3, x, y)
