from .point import Point

class DrawableText:
   def __init__(self, txt, anchor_point):
      self.text         = txt
      self.anchor_point = anchor_point

   def __str__(self):
      return "Text({}, {})".format(self.text[0:15], self.anchor_point)

   def __repr__(self):
      return str(self)

   def to_serializable(self):
      """Transform this object in something json-serializable"""
      return { "text": self.text, "anchor_point": self.anchor_point.to_serializable() }

   def from_serializable(json_obj):
      """From a json serialization reconstruct the object"""
      return DrawableText(json_obj["text"], Point.from_serializable(json_obj["anchor_point"]))

   def __eq__(self, other):
      return self.text == other.text and self.anchor_point == other.anchor_point

   def clone(self):
      return DrawableText(self.text, self.anchor_point.clone())

   def traslated(self, amount_x, amount_y):
      return DrawableText( self.text, self.anchor_point.clone() ).traslate( amount_x, amount_y )

   def traslate(self, amount_x, amount_y):
      self.anchor_point.traslate(amount_x, amount_y)
      return self

   def reflected_y(self):
      rt = self.clone()
      rt.reflect_y()
      return rt

   def reflect_y(self):
      self.anchor_point.reflect_y()

   def scale(self, amount):
      self.anchor_point.scale(amount)