import unittest
from model.drawable import Point
from model.drawable import Text

class TextTest(unittest.TestCase):

   def test_room_text_cloning(self):
      t  = Text( "ABC", Point(20, 20) )
      t2 = t.clone()

      self.assertTrue(t is not t2)
      self.assertTrue(t.anchor_point == t2.anchor_point)
      self.assertTrue(t.text == t2.text)
