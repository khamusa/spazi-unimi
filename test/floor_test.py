from model           import Floor, Room
from mock            import MagicMock
from model.drawable  import Text, Point, Polygon
import unittest

class FloorTest(unittest.TestCase):

   def setUp(self):
      self.f = Floor("Pippo", "disneyland")
      self.polygon1 = Polygon.from_absolute_coordinates([(0,0),(5,0),(5,5),(10,5),(10,10),(0,10)])
      self.room1 = Room(self.polygon1)

   def test_floor_creation(self):
      self.assertEqual(self.f.b_id, "Pippo")
      self.assertEqual(self.f.f_id, "disneyland")
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
      floor = Floor("Building 1", "Floor1", [self.room1,r2])
      floor2 = Floor("Building 1", "Floor1",[self.room1,r2])
      self.assertEqual(floor,floor2)
      floor3 = Floor("Building 1", "Floor", [self.room1,r2])
      self.assertNotEqual(floor, floor3)
      floor3 = Floor("Building", "Floor1", [self.room1,r2])
      self.assertNotEqual(floor, floor3)
      floor3 = Floor("Building 1", "Floor1", [self.room1])
      self.assertNotEqual(floor, floor3)

   def test_floor_trasform(self):
      self.room1.traslate = MagicMock()
      self.room1.scale = MagicMock()
      self.f.add_room(self.room1)
      self.f.transform()
      self.room1.traslate.assert_called_once_with(0, 0)
      self.room1.scale.assert_called_once_with(1)

      for count in range(1, 10):
         self.f.add_room(self.room1)

      self.f.transform()
      self.assertEqual(self.room1.traslate.call_count, 11)
      self.assertEqual(self.room1.scale.call_count, 11)

   def test_floor_normalize(self):
      self.f.transform = MagicMock()
      sa = self.f.calculate_scale_amount()
      self.f.normalize()
      self.f.transform.assert_called_once_with(
         scale_amount = sa,
         traslate_x   = -self.f.min_x,
         traslate_y   = -self.f.min_y
         )

   def test_calculate_scale_amount_and_trasform(self):
      polygon = Polygon.from_absolute_coordinates(
            [(0,0),(1024,0),(1024,1024),(2048,1024),(2048,2048),(0,2048)]
         )
      room = Room(polygon)
      f = Floor("Pippo", "disneyland", [room])
      self.assertEqual(f.max_output_size / 2048, f.calculate_scale_amount())

      f.normalize()
      for point in f.rooms[0].polygon.points:
         self.assertTrue(point.x <= f.max_output_size)
         self.assertTrue(point.y <= f.max_output_size)

