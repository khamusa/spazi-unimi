from .drawable import Text
from .drawable import Point
from .drawable import Polygon
from .drawable import Drawable

class Room(Drawable):
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
      relative_point = text.traslated_ac(traslate_x, traslate_y)
      return self.polygon._contains_point(relative_point)

   def min_absolute_point(self):
      min_point, _ = self.polygon.bounding_box
      return self.polygon.traslated_ac(*min_point)

   ##########################
   # TRANSFORMATION METHODS #
   ##########################

   def traslate(self, amount_x, amount_y):
      """Traslates this room, by traslating it's polygon and texts"""
      self.polygon.traslate_ac(amount_x, amount_y)
      for t in self.texts:
         t.traslate_ac(amount_x, amount_y)
      return self

   def reflect_y(self):
      self.polygon.reflect_y_ac()
      self.polygon.reflect_y()
      for t in self.texts:
         t.reflect_y_ac()

   def scale(self, amount):
      """TODO: accept amount_x and amount_y separeted"""
      self.polygon.scale(amount)
      self.polygon.scale_ac(amount)
      for t in self.texts:
         t.scale_ac(amount)

   def rotate(self, grades):
      self.polygon.rotate(grades)
      self.polygon.rotate_ac(grades)
      for t in self.texts:
         t.rotate_ac(amount)
