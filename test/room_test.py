from room import Room
from point import Point
from room_text import RoomText
import itertools

import unittest
from mock import MagicMock

class RoomTest(unittest.TestCase):
   def setUp(self):
      # 10x10 square beginning on origin
      self.room1 = Room([(0,0),(10,0),(10,10),(0,10)],
         [
            RoomText("1234",Point(3,3)),
            RoomText("Super Cool",Point(4,7)),
            RoomText("Corner Text!",Point(1,10))
         ])

      # 10x10 diamond shape centered at origin
      self.room2 = Room([(10,0), (0, 10), (-10, 0), (0, -10)])

      # L-shaped room
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
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(2, 10), Point(1, 5)) == 0 )

      # Horizontal line with point aligned
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(10, 0), Point(4, 0)) == 0 )

      # vertical line with point aligned
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(0, 10), Point(0, 5)) == 0 )

   def test_room_traslation(self):
      def check_room_traslation(room, amount_x, amount_y):

         old_points = [ p.clone() for p in room.points ]
         old_texts = [ t.clone() for t in room.texts ]

         room.traslate(amount_x, amount_y)

         # Check points have been traslated
         for p1, p2 in zip(room.points, old_points):
            self.assertTrue(p1.x == p2.x + amount_x)
            self.assertTrue(p1.y == p2.y + amount_y)

         # Pending: test for every RoomText on room
         for new_text, old_text in zip(room.texts, old_texts):
            self.assertTrue(new_text.anchor_point.x == old_text.anchor_point.x + amount_x)
            self.assertTrue(new_text.anchor_point.y == old_text.anchor_point.y + amount_y)

      check_room_traslation(self.room1, 20, 33)
      check_room_traslation(self.room1, -10, -23)
      check_room_traslation(self.room1, 20, -33)
      check_room_traslation(self.room1, -10, 23)
      check_room_traslation(self.room1, 0, 0)


   def test_room_top_left_most_point(self):

      def check_top_most(room, expected):
         actual = room.top_left_most_point()
         self.assertTrue(actual == expected, "Expected top-left most point was {}, but actual is {}".format(expected, actual))

      check_top_most(self.room1, Point(0, 0))

   def test_room_cloning(self):
      r2 = self.room1.clone()

      self.assertTrue(r2.points == self.room1.points)
      self.assertTrue(r2.texts == self.room1.texts)

      self.assertTrue(r2 is not self.room1)

   def test_room_scale(self):
      for p in itertools.chain(self.room1.points, self.room1.texts):
         p.scale =  MagicMock()

      self.room1.scale(2)

      for p in itertools.chain(self.room1.points, self.room1.texts):
         p.scale.assert_called_with(2)


