
class RoomText:
   def __init__(self, txt, anchor_point):
      self.text         = txt
      self.anchor_point = anchor_point

   def __str__(self):
      return "Text({}, {})".format(self.text[0:15], self.anchor_point)

   def __repr__(self):
      return str(self)

   def __eq__(self, other):
      return self.text == other.text and self.anchor_point == other.anchor_point

   def clone(self):
      return RoomText(self.text, self.anchor_point.clone())

   def traslated(self, amount_x, amount_y):
      return RoomText( self.text, self.anchor_point.clone() ).traslate( amount_x, amount_y )

   def traslate(self, amount_x, amount_y):
      self.anchor_point.traslate(amount_x, amount_y)
      return self

   def reflected_y(self):
      return RoomText( self.text, self.anchor_point.reflected_y() )
