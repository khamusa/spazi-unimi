import unittest
import json
import json_room_encoder
import time
from floor import Floor
from point import Point
from room import Room
from room_text import RoomText

class JsonEncodingTest(unittest.TestCase):
   def test_room_to_serializable(self):
      r = Room([(1,2), (3, 4), (5, 6)])
      r.add_text(RoomText("Encoded cool text", Point([1,1])))

      self.assertEqual(r.to_serializable(), { "points": r.points, "texts": r.texts })

   def test_room_text_to_serializable(self):
      rt = RoomText("Encoded cool text", Point([1,1]))

      self.assertEqual(rt.to_serializable(), { "text": rt.text, "anchor_point": rt.anchor_point })

   def test_point_to_serializable(self):
      p = Point([1,2])

      self.assertEqual(p.to_serializable(), { "x": p.x, "y": p.y })

   def test_room_encoding_and_decoding(self):
      r = Room([(1,2), (3, 4), (5, 6)])
      r.add_text(RoomText("Encoded cool text", Point([1,1])))

      s1 = json.dumps(r, cls = json_room_encoder.JsonRoomEncoder, indent = 3)
      d1 = json.loads(s1)

      r2 = Room.from_serializable(d1)
      self.assertEqual(r.points, r2.points)
      self.assertEqual(r.texts, r2.texts)

      s2 = json.dumps(r, cls = json_room_encoder.JsonRoomEncoder, indent = 4)
      d2 = json.loads(s2)
      self.assertEqual(d1, d2)

   def test_floor_to_serializable(self):
      r1 = Room([(0,0),(10,0),(10,10),(0,10)])
      r2 = Room([(12,0),(22,0),(22,10),(12,10)])
      f  = Floor("Building cool name","Floor cool name", [r1,r2])

      self.assertEqual( f.to_serializable() ,
         {
            "building_name"   : f.building_name,
            "floor_name"      : f.floor_name,
            "date"            : time.strftime("%m/%d/%Y"),
            "payload"         : {
               "n_rooms" : 2,
               "rooms"   : [r1,r2]
            }
         })

   def test_floor_encoding_and_decoding(self):
      r1 = Room([(0,0),(10,0),(10,10),(0,10)])
      r2 = Room([(12,0),(22,0),(22,10),(12,10)])
      f1 = Floor("Building cool name","Floor cool name", [r1,r2])

      f_dump = json.dumps(f1,cls= json_room_encoder.JsonRoomEncoder)
      f_load = json.loads(f_dump)

      f2 = Floor.from_serializable(f_load)

      self.assertEqual(f1,f2)
