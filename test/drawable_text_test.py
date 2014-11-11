import unittest
from model.drawable import DrawablePoint
from model.drawable import DrawableText

class DrawableTextTest(unittest.TestCase):
   def test_text_translation(self):
      t  = DrawableText( "ABC", DrawablePoint(20, 20) )
      old_x, old_y = t.anchor_point
      t.traslate(10, 20)

      self.assertTrue( t.anchor_point.x == old_x + 10 )
      self.assertTrue( t.anchor_point.y == old_y + 20 )

      t.traslate(-20, -30)

      self.assertTrue( t.anchor_point.x == old_x - 10 )
      self.assertTrue( t.anchor_point.y == old_y - 10 )

   def test_text_traslated(self):
      t  = DrawableText( "ABC", DrawablePoint(20, 20) )
      t2 = t.traslated(10, 20)

      # traslated must retur a new object
      self.assertFalse(t2 is t)
      self.assertTrue( t2.anchor_point.x == 30 )
      self.assertTrue( t2.anchor_point.y == 40 )

      t2 = t.traslated(-10, -20)

      # traslated must retur a new object
      self.assertFalse(t2 is t)
      self.assertTrue( t2.anchor_point.x == 10 )
      self.assertTrue( t2.anchor_point.y == 0 )

   def test_room_text__cloning(self):
      t  = DrawableText( "ABC", DrawablePoint(20, 20) )
      t2 = t.clone()

      self.assertTrue(t is not t2)
      self.assertTrue(t.anchor_point == t2.anchor_point)
      self.assertTrue(t.text == t2.text)
