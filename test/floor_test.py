import unittest
from floor import Floor
from room import Room
from mock import MagicMock
from room_text import RoomText
from point import Point

class FloorTest(unittest.TestCase):

   def setUp(self):
      self.f = Floor("Pippo", "disneyland")

   def test_floor_creation(self):
      self.assertEqual(self.f.building_name, "Pippo")
      self.assertEqual(self.f.floor_name, "disneyland")
      self.assertEqual(self.f.rooms, [])

   def test_floor_room_addition(self):
      r = Room( [(1, 2), (3, 4), (5, 5)] )
      self.f.add_room(r)

      self.assertEqual(self.f.rooms[0], r)

      r2 = Room( [(4, 4), (22, 14), (53, 53)] )
      self.f.add_room(r2)

      self.assertEqual(len(self.f.rooms), 2)
      self.assertTrue( r2 in self.f.rooms )


   def test_associate_text_to_rooms(self):
      r1 = Room([(0,0),(10,0),(10,10),(0,10)])
      r2 = Room([(12,0),(22,0),(22,10),(12,10)])
      t1 = RoomText("Text room 1",Point(5,5))
      t2 = RoomText("Text room 2",Point(15,8))
      t3 = RoomText("Text outside",Point(11,5))

      floor = Floor("Building 1", "Floor1",[ r1,r2])
      floor.associate_room_texts([t1,t2,t3])

      self.assertTrue( len(r1.texts) == 1 )
      self.assertTrue( len(r2.texts) == 1 )
      self.assertTrue( t1 in r1.texts )
      self.assertTrue( t2 in r2.texts )

   def test_associate_text_to_rooms2(self):
      r1 = Room([(0,0),(5,0),(5,5),(10,5),(10,10),(0,10)])
      r2 = Room([(6,0),(12,0),(12,10),(11,10),(11,4),(6,4)])
      t1_1     = RoomText("Text room 1",Point(2,2))
      t1_2     = RoomText("Text room 1",Point(8,8))
      t2_1     = RoomText("Text room 2",Point(7,2))
      t2_2     = RoomText("Text room 2",Point(11,8))
      t_none   = RoomText("Text none",Point(5,12))

      floor = Floor("Building 1", "Floor1",[ r1,r2])
      floor.associate_room_texts([t1_1,t1_2,t2_1,t2_2,t_none])

      self.assertTrue( len(r1.texts) == 2 )
      self.assertTrue( len(r2.texts) == 2 )
      self.assertTrue( t1_1 in r1.texts )
      self.assertTrue( t1_2 in r1.texts )
      self.assertTrue( t2_1 in r2.texts )
      self.assertTrue( t2_2 in r2.texts )
      self.assertTrue( t1_1 in r1.texts )
      self.assertTrue( t_none not in r1.texts )
