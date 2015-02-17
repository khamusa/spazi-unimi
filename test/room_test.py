from model import Room
from model.drawable import Point
from model.drawable import Polygon
from model.drawable import Text
import itertools

import unittest
from mock import MagicMock

class RoomTest(unittest.TestCase):
   def setUp(self):
      # 10x10 square beginning on origin
      self.polygon1 = Polygon.from_absolute_coordinates([(0,0),(10,0),(10,10),(0,10)])
      self.room1 = Room(self.polygon1,
         [
            Text("1234",Point(3,3)),
            Text("Super Cool",Point(4,7)),
            Text("Corner Text!",Point(1,10))
         ])

      # 10x10 diamond shape centered at origin
      self.polygon2 = Polygon.from_absolute_coordinates([(10,0), (0, 10), (-10, 0), (0, -10)])
      self.room2 = Room(self.polygon2)

      # L-shaped room
      self.polygon3 = Polygon.from_absolute_coordinates([(0,0),(10,0),(10,5),(5,5),(5,10),(0,10)])
      self.room3 = Room(self.polygon3)

   def test_room_equality(self):
      # Equality is true
      r2 = Room(self.polygon1.clone(), [ t.clone() for t in self.room1.texts ])
      r3 = Room(
                  self.polygon1.clone(),
                  [ t.clone() for t in self.room1.texts[1:] ]
               )

      # Equality is false
      d = Room(
                  self.polygon1.clone().traslate(1, 0),
                  [ t.clone() for t in self.room1.texts ]
               )
      self.assertEqual(self.room1, r2)
      self.assertEqual(self.room1, r3)
      self.assertNotEqual(self.room1, d)

   def test_room_cloning(self):
      r2 = self.room1.clone()


      self.assertEqual(r2.texts, self.room1.texts)
      self.assertEqual(r2.polygon, self.room1.polygon)
      self.assertEqual(r2, self.room1)

      self.assertTrue(r2 is not self.room1)

   def test_room_min_absolute_point(self):
      def check_min_abs_point(room, expected_x, expected_y):
         minX, minY = room.min_absolute_point()
         self.assertEqual(minX, expected_x)
         self.assertEqual(minY, expected_y)

      check_min_abs_point(self.room1, 0, 0)
      self.room1.traslate(5, 5)
      check_min_abs_point(self.room1, 5, 5)
      self.room1.reflect_y()
      check_min_abs_point(self.room1, 5, -15)

   def test_room_contains_text(self):
      t1 = Text("In text!",Point(5,5))
      t2 = Text("Out text!",Point(11,5))
      self.assertTrue(self.room1.contains_text(t1))
      self.assertFalse(self.room1.contains_text(t2))

   ###################
   # TRANSFORMATIONS #
   ###################
   def test_room_traslation(self):
      def check_room_traslation(room, amount_x, amount_y):
         room.polygon = MagicMock();

         old_texts = [ t.clone() for t in room.texts ]

         room.traslate(amount_x, amount_y)

         # Check polygon have been traslated
         room.polygon.traslate_ac.assert_called_with(amount_x, amount_y)

         # Pending: test for every Text on room
         for new_text, old_text in zip(room.texts, old_texts):
            self.assertTrue(new_text.anchor_point.x == old_text.anchor_point.x + amount_x)
            self.assertTrue(new_text.anchor_point.y == old_text.anchor_point.y + amount_y)

      check_room_traslation(self.room1, 20, 33)
      check_room_traslation(self.room1, -10, -23)
      check_room_traslation(self.room1, 20, -33)
      check_room_traslation(self.room1, -10, 23)
      check_room_traslation(self.room1, 0, 0)

   def test_room_reflection(self):
      self.room1.reflect_y()
      self.assertEqual(
                        self.room1.polygon.points,
                        [Point(0,0), Point(10,0), Point(10,-10), Point(0,-10)]
                     )

      self.polygon1.anchor_point.reflect_y = MagicMock()
      self.polygon1.reflect_y = MagicMock()
      for t in self.room1.texts:
         t.anchor_point.reflect_y = MagicMock()

      self.room1.reflect_y()

      self.polygon1.anchor_point.reflect_y.assert_called_once_with()
      self.polygon1.reflect_y.assert_called_once_with()
      for t in self.room1.texts:
         t.anchor_point.reflect_y.assert_called_once_with()

   def test_room_scale(self):
      self.room1.polygon = MagicMock()
      for p in self.room1.texts:
         p.anchor_point.scale =  MagicMock()

      self.room1.scale(2)

      for t in self.room1.texts:
         t.anchor_point.scale.assert_called_with(2)
      self.room1.polygon.scale.assert_called_with(2)
