import unittest
import json
import time
from model.drawable import DrawableFloor
from model.drawable import Point
from model.drawable import DrawableRoom
from model.drawable import DrawableText


def serialize_list(ls):
   return [ e.to_serializable() for e in ls ]

class JsonEncodingTest(unittest.TestCase):

   def test_room_to_serializable(self):
      r = DrawableRoom([(1,2), (3, 4), (5, 6)])
      r.add_text(DrawableText("Encoded cool text", Point([1,1])))

      self.assertEqual(r.to_serializable(), { "points": serialize_list(r.points), "texts": serialize_list(r.texts) })

   def test_room_text_to_serializable(self):
      rt = DrawableText("Encoded cool text", Point([1,1]))

      self.assertEqual(rt.to_serializable(), { "text": rt.text, "anchor_point": rt.anchor_point.to_serializable() })

   def test_point_to_serializable(self):
      p = Point([1,2])

      self.assertEqual(p.to_serializable(), { "x": p.x, "y": p.y })

   def test_room_encoding_and_decoding(self):
      r = DrawableRoom([(1,2), (3, 4), (5, 6)])
      r.add_text(DrawableText("Encoded cool text", Point([1,1])))

      s1 = json.dumps(r.to_serializable(), indent = 3)
      d1 = json.loads(s1)

      r2 = DrawableRoom.from_serializable(d1)
      self.assertEqual(r.points, r2.points)
      self.assertEqual(r.texts, r2.texts)

      s2 = json.dumps(r.to_serializable(), indent = 4)
      d2 = json.loads(s2)
      self.assertEqual(d1, d2)

   def test_floor_to_serializable(self):
      r1 = DrawableRoom([(0,0),(10,0),(10,10),(0,10)])
      r2 = DrawableRoom([(12,0),(22,0),(22,10),(12,10)])
      f  = DrawableFloor("Building cool name","Floor cool name", [r1,r2])

      self.assertEqual( f.to_serializable() ,
         {
            "building_name"   : f.building_name,
            "floor_name"      : f.floor_name,
            "date"            : time.strftime("%m/%d/%Y"),
            "payload"         : {
               "n_rooms" : 2,
               "rooms"   : [r1.to_serializable(), r2.to_serializable()]
            }
         })

   def test_floor_encoding_and_decoding(self):
      r1 = DrawableRoom([(0,0),(10,0),(10,10),(0,10)])
      r2 = DrawableRoom([(12,0),(22,0),(22,10),(12,10)])
      f1 = DrawableFloor("Building cool name","Floor cool name", [r1,r2])

      f_dump = json.dumps(f1.to_serializable())
      f_load = json.loads(f_dump)

      f2 = DrawableFloor.from_serializable(f_load)

      self.assertEqual(f1,f2)
