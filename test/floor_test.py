import unittest
from model  import Floor
from model  import Room
from mock            import MagicMock
from model.drawable  import Text
from model.drawable  import Point
from model.drawable  import Polygon

class FloorTest(unittest.TestCase):

   def setUp(self):
      self.f = Floor("Pippo", "disneyland")
      self.polygon1 = Polygon.from_absolute_coordinates([(0,0),(5,0),(5,5),(10,5),(10,10),(0,10)])
      self.room1 = Room(self.polygon1)

   def test_floor_creation(self):
      self.assertEqual(self.f.building_name, "Pippo")
      self.assertEqual(self.f.floor_name, "disneyland")
      self.assertEqual(self.f.rooms, [])

   def test_floor_room_addition(self):
      self.f.add_room(self.room1)

      self.assertEqual(self.f.rooms[0], self.room1)

      p2 = Polygon.from_absolute_coordinates( [(4, 4), (22, 14), (53, 53)] )
      r2 = Room(p2)
      self.f.add_room(r2)

      self.assertEqual(len(self.f.rooms), 2)
      self.assertTrue( r2 in self.f.rooms )

   def test_associate_text_to_rooms(self):
      p2 = Polygon.from_absolute_coordinates([(12,0),(22,0),(22,10),(12,10)])
      r2 = Room(p2)
      t1 = Text("Text room 1", Point(5,5))
      t2 = Text("Text room 2", Point(15,8))
      t3 = Text("Text outside",Point(11,5))

      floor = Floor("Building 1", "Floor1",[self.room1, r2])
      floor.associate_room_texts([t1,t2,t3])

      self.assertEqual( len(self.room1.texts), 1 )
      self.assertTrue( len(r2.texts) == 1 )
      self.assertTrue( t1 in self.room1.texts )
      self.assertTrue( t2 in r2.texts )

   def test_associate_text_to_rooms2(self):
      p2 = Polygon.from_absolute_coordinates([(6,0),(12,0),(12,10),(11,10),(11,4),(6,4)])
      r2 = Room(p2)
      t1_1     = Text("Text room 1",Point(2,2))
      t1_2     = Text("Text room 1",Point(8,8))
      t2_1     = Text("Text room 2",Point(7,2))
      t2_2     = Text("Text room 2",Point(11,8))
      t_none   = Text("Text none",Point(5,12))

      floor = Floor("Building 1", "Floor1",[ self.room1,r2])
      floor.associate_room_texts([t1_1,t1_2,t2_1,t2_2,t_none])

      self.assertTrue( len(self.room1.texts) == 2 )
      self.assertTrue( len(r2.texts) == 2 )
      self.assertTrue( t1_1 in self.room1.texts )
      self.assertTrue( t1_2 in self.room1.texts )
      self.assertTrue( t2_1 in r2.texts )
      self.assertTrue( t2_2 in r2.texts )
      self.assertTrue( t1_1 in self.room1.texts )
      self.assertTrue( t_none not in self.room1.texts )

   def test_floor_equal(self):
      p2 = Polygon.from_absolute_coordinates([(12,0),(22,0),(22,10),(12,10)])
      r2 = Room(p2)
      t1 = Text("Text room 1",Point(5,5))
      t2 = Text("Text room 2",Point(15,8))
      t3 = Text("Text outside",Point(11,5))

      floor = Floor("Building 1", "Floor1", [self.room1,r2])
      floor2 = Floor("Building 1", "Floor1",[self.room1,r2])

      self.assertEqual(floor,floor2)
