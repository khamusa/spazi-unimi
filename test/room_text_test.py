import unittest
from point import Point
from room_text import RoomText

class RoomTextTest(unittest.TestCase):
   def test_text_translation(self):
      t  = RoomText( "ABC", Point(20, 20) )
      t2 = t.traslated(10, 20)

      # traslated must retur a new object
      self.assertFalse(t2 is t)
      self.assertTrue( t2.anchor_point.x==30 )
      self.assertTrue( t2.anchor_point.y==40 )

      t2 = t.traslated(-10, -20)

      # traslated must retur a new object
      self.assertFalse(t2 is t)
      self.assertTrue( t2.anchor_point.x==10 )
      self.assertTrue( t2.anchor_point.y==0 )


