from .point import Point

class Drawable():
   """
   Base class for drawable objects, implement some ausiliary methods but no
   concrete behavior.

   If the Drawable is composed of sub-elements and the drawing operations are
   obtained by applying the operations atomically to it's sub-elements, the
   Drawable may define a __entities__ method returning those sub-elements,
   and in that case Drawable will supply the hooks for calling the
   transformation methos directly on the sub-elements.

   Example: a polygon is traslated by traslating it's single points. Hence,
   if a Polygon class defines __entities(self) that returns it's points,
   the translation will happen automatically by calling translate on each
   point object."""

   def __init__(self):
      self._calculate_bounding_box()

   def traslated(self, *args, **kargs):
      """Immutable version of traslate"""
      return self.clone().traslate(*args, **kargs)

   def reflected_y(self, *args, **kargs):
      """Immutable version of reflecte_y"""
      return self.clone().reflect_y(*args, **kargs)

   def scaled(self, *args, **kargs):
      return self.clone().scale(*args, **kargs)

   def rotated(self, *args, **kargs):
      return self.clone().rotate(*args, **kargs)

   def traslate(self, amount_x, amount_y):
      """Traslates the drawable's elements'"""
      for e in self.__entities__():
         e.traslate(amount_x, amount_y)

      return self

   def scale(self, amount_x, amount_y = None):
      for e in self.__entities__():
         e.scale(amount_x, amount_y)

      return self

   def reflect_y(self):
      for e in self.__entities__():
         e.reflect_y()

      self._calculate_bounding_box()
      return self

   def rotate(self, grades):
      for e in self.__entities__():
         e.rotate(grades, 0, 0)

      self._calculate_bounding_box()
      return self

   def min_x(self):
      return self.bounding_box[0][0]

   def min_y(self):
      return self.bounding_box[0][1]

   def max_x(self):
      return self.bounding_box[1][0]

   def max_y(self):
      return self.bounding_box[1][1]

   def _calculate_bounding_box(self):
      min_x = float("+inf")
      min_y = float("+inf")
      max_x = float("-inf")
      max_y = float("-inf")

      # TODO: chiedere min_x all'entita' invece di chiamare .x
      for p in self.__entities__():
         if p is not None:
            min_x = min(min_x, p.min_x())
            min_y = min(min_y, p.min_y())
            max_x = max(max_x, p.max_x())
            max_y = max(max_y, p.max_y())

      self.bounding_box = (Point(min_x, min_y), Point(max_x, max_y))
      center_x = (min_x - max_x) / 2
      center_y = (min_y - max_y) / 2
      self.center_point = Point(abs(center_x), abs(center_y))
