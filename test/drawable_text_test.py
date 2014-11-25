import unittest
from model.drawable import Point
from model.drawable import Text

class TextTest(unittest.TestCase):

   def test_text_cloning(self):
      t  = Text( "ABC", Point(20, 20) )
      t2 = t.clone()

      self.assertTrue(t is not t2)
      self.assertTrue(t.anchor_point == t2.anchor_point)
      self.assertTrue(t.text == t2.text)

   def test_text_equality(self):
      t  = Text( "ABC", Point(20, 20) )
      t2 = Text( "ABC", Point(20, 20) )

      d1 = Text( "ABc", Point(20, 20) )
      d2 = Text( "ABC", Point(20, 21) )
      d3 = Text( "ABC", Point(21, 20) )

      self.assertEqual(t, t2)
      self.assertNotEqual(t, d1)
      self.assertNotEqual(t, d2)
      self.assertNotEqual(t, d3)
