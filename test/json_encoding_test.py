import unittest
import json
import time
from mock import MagicMock
from model import Floor
from model import Room
from model.drawable import Point
from model.drawable import Text
from model.drawable import Polygon


def serialize_list(ls):
   return [ e.to_serializable() for e in ls ]

class JsonEncodingTest(unittest.TestCase):

   def setUp(self):
      self.polygon1 = Polygon.from_absolute_coordinates([(1,2), (3, 4), (5, 6)])
      self.room1 = Room(self.polygon1)

   def test_room_to_serializable(self):
      self.polygon1.to_serializable = MagicMock(return_value="pippo_serializzato")
      self.room1.add_text(Text("Encoded cool text", Point([1,1])))
      self.assertEqual(self.room1.to_serializable(), { "polygon": "pippo_serializzato", "texts": serialize_list(self.room1.texts) })

   def test_room_text_serializable(self):
      t1 = Text("Encoded cool text", Point([1,1]))
      self.assertEqual(t1.to_serializable(), { "text": t1.text, "anchor_point": t1.anchor_point.to_serializable() })
      t2 = Text.from_serializable(t1.to_serializable())
      self.assertEqual(t1, t2)

   def test_point_serializable(self):
      p = Point([1,2])
      self.assertEqual(p.to_serializable(), { "x": p.x, "y": p.y })
      p2 = Point.from_serializable(p.to_serializable())
      self.assertEqual(p, p2)

   def test_room_encoding_and_decoding(self):
      r = Room([(1,2), (3, 4), (5, 6)])
      self.room1.add_text(Text("Encoded cool text", Point([1,1])))

      s1 = json.dumps(self.room1.to_serializable(), indent = 3)
      d1 = json.loads(s1)

      r2 = Room.from_serializable(d1)
      self.assertEqual(self.room1.polygon.points, r2.polygon.points)
      self.assertEqual(self.room1.texts, r2.texts)

      s2 = json.dumps(self.room1.to_serializable(), indent = 4)
      d2 = json.loads(s2)
      self.assertEqual(d1, d2)

   def test_floor_to_serializable(self):
      p2 = Polygon.from_absolute_coordinates([(12,0),(22,0),(22,10),(12,10)])
      r2 = Room(p2)
      f  = Floor("Building cool name","Floor cool name", [self.room1, r2])

      self.assertEqual( f.to_serializable() ,
         {
            "walls"           : [],
            "b_id"            : f.b_id,
            "f_id"            : f.f_id,
            "rooms"           : [self.room1.to_serializable(), r2.to_serializable()]
         })

   def test_floor_encoding_and_decoding(self):
      p2 = Polygon.from_absolute_coordinates([(12,0),(22,0),(22,10),(12,10)])
      r2 = Room(p2)
      f1 = Floor("Building cool name","Floor cool name", [self.room1,r2])

      f_dump = json.dumps(f1.to_serializable())
      f_load = json.loads(f_dump)

      f2 = Floor.from_serializable(f_load)

      self.assertEqual(f1,f2)


   def test_polygon_to_serializable(self):
      self.polygon1.anchor_point.to_serializable = MagicMock(return_value="anchor_pippo")
      for p in self.polygon1.points:
         p.to_serializable = MagicMock(return_value="pippo_point")
      self.assertEqual( self.polygon1.to_serializable(),
         {
            "anchor_point" : "anchor_pippo",
            "points"       : [ "pippo_point" for p in self.polygon1.points ]
         })


   def test_polygon_from_serializable(self):
      p_dump = json.dumps(self.polygon1.to_serializable())
      p_load = json.loads(p_dump)
      pol2 = Polygon.from_serializable(p_load)
      self.assertEqual(self.polygon1, pol2)
