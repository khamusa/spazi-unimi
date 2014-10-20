from point import Point

class RoomText:
   def __init__(self, txt, anchor_point):
      self.text         = txt
      self.anchor_point = anchor_point

   def __str__(self):
      return "Text({}, {})".format(self.text[0:15], self.anchor_point)

   def __repr__(self):
      return str(self)

   def to_serializable(self):
      """Transform this object in something json-serializable"""
      return { "text": self.text, "anchor_point": self.anchor_point }

   def from_serializable(json_obj):
      """From a json serialization reconstruct the object"""
      return RoomText(json_obj["text"], Point.from_serializable(json_obj["anchor_point"]))

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

   def scale(self, amount):
      self.anchor_point.scale(amount)
