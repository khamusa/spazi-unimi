import unittest
from floor import Floor
import room

class FloorTest(unittest.TestCase):

   def setUp(self):
      self.f = Floor("Pippo", "disneyland")

   def test_floor_creation(self):
      self.assertEqual(self.f.building_name, "Pippo")
      self.assertEqual(self.f.floor_name, "disneyland")
      self.assertEqual(self.f.rooms, [])

   def test_floor_room_addition(self):
      r = room.Room( [(1, 2), (3, 4), (5, 5)] )
      self.f.add_room(r)

      self.assertEqual(self.f.rooms[0], r)

      r2 = room.Room( [(4, 4), (22, 14), (53, 53)] )
      self.f.add_room(r2)

      self.assertEqual(len(self.f.rooms), 2)
      self.assertTrue( r2 in self.f.rooms )
