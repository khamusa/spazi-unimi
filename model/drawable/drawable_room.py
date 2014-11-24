from .drawable_text import DrawableText
from .point import Point
from .polygon import Polygon

class DrawableRoom():
   def __init__(self, polygon = None, texts=None):
      self.polygon = polygon
      self.texts   = texts or []

   def __str__(self):
      return "Stanza(" + str(self.polygon) + ")"

   def __repr__(self):
      return str(self)

   def __eq__(self,other):
      return self.polygon == other.polygon and self.texts == other.texts

   def to_serializable(self):
      """Transform this object in something json-serializable"""
      return {
         "polygon": self.polygon.to_serializable(),
         "texts": [ el.to_serializable() for el in self.texts ]
      }

   def from_serializable(json_obj):
      """From a json serialization reconstruct the object"""
      return DrawableRoom(
            Polygon.from_serializable(json_obj["polygon"]),
            [ DrawableText.from_serializable(t) for t in json_obj["texts"] ]
         )

   def add_text(self, text):
      if( text not in self.texts ):
         self.texts.append(text)

   def clone(self):
      r = DrawableRoom(self.polygon.clone(), [ t.clone() for t in self.texts ])
      return r

   def containsText(self, text):
      """TODO: rename to contains_text """
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
      self.polygon.traslate(amount_x, amount_y)
      for t in self.texts:
         t.anchor_point.traslate(amount_x, amount_y)
      return self

   def traslated(self, amount_x, amount_y):
      return self.clone().traslate(amount_x, amount_y)

   def reflected_y(self):
      return self.clone().reflect_y()

   def reflect_y(self):
      self.polygon.reflect_y()
      for t in self.texts:
         t.reflect_y()

   def scale(self, amount):
      """TODO: accept amount_x and amount_y separeted"""
      self.polygon.scale(amount)
      self.polygon.anchor_point.scale(amount)
      for t in self.texts:
         t.anchor_point.scale(amount)
