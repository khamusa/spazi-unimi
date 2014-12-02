from .drawable import Text
from .drawable import Point
from .drawable import Polygon

class Room():
   def __init__(self, polygon = None, texts=None):
      self.polygon = polygon
      self.texts   = texts or []

   def __str__(self):
      return "Stanza(" + str(self.polygon) + ")"

   def __repr__(self):
      return str(self)

   def __eq__(self,other):
      return self.polygon == other.polygon

   def to_serializable(self):
      """Transform this object in something json-serializable"""
      return {
         "polygon": self.polygon.to_serializable(),
         "texts": [ el.to_serializable() for el in self.texts ]
      }

   def from_serializable(json_obj):
      """From a json serialization reconstruct the object"""
      return Room(
            Polygon.from_serializable(json_obj["polygon"]),
            [ Text.from_serializable(t) for t in json_obj["texts"] ]
         )

   def add_text(self, text):
      if( text not in self.texts ):
         self.texts.append(text)

   def clone(self):
      r = Room(self.polygon.clone(), [ t.clone() for t in self.texts ])
      return r

   def contains_text(self, text):
      """Returns true if current room contains the supplied text"""
      if not self.polygon:
         return False

      traslate_x = -self.polygon.anchor_point.x
      traslate_y = -self.polygon.anchor_point.y
      relative_point = text.anchor_point.traslated(traslate_x, traslate_y)
      return self.polygon._contains_point(relative_point)

   def min_absolute_point(self):
      min_point, _ = self.polygon.bounding_box
      return self.polygon.anchor_point.traslated(*min_point)

   ##########################
   # TRANSFORMATION METHODS #
   ##########################

   def traslate(self, amount_x, amount_y):
      """Traslates this room, by traslating it's polygon and texts"""
      self.polygon.anchor_point.traslate(amount_x, amount_y)
      for t in self.texts:
         t.anchor_point.traslate(amount_x, amount_y)
      return self

   def traslated(self, amount_x, amount_y):
      return self.clone().anchor_point.traslate(amount_x, amount_y)

   def reflected_y(self):
      return self.clone().reflect_y()

   def reflect_y(self):
      self.polygon.anchor_point.reflect_y()
      self.polygon.reflect_y()
      for t in self.texts:
         t.anchor_point.reflect_y()

   def scale(self, amount):
      """TODO: accept amount_x and amount_y separeted"""
      self.polygon.scale(amount)
      self.polygon.anchor_point.scale(amount)
      for t in self.texts:
         t.anchor_point.scale(amount)
