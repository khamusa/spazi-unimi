from math import sin, cos, radians, sqrt
from sys import float_info

class Point():
   _precision  = 4
   _epsilon    = 0.001

   def __init__(self, a, b = None):
      a, b = b is None and (a[0], a[1]) or (a, b)
      self.x = self._round(a)
      self.y = self._round(b)

   def _round(self, a):
      return round(a, self.__class__._precision)

   def __eq__(self, other):
      if type(other) is not Point:
         try:
            other = Point(other[0], other[1])
         except Exception:
            return False

      return (
            abs(other.x - self.x) <= self.__class__._epsilon and
            abs(other.y - self.y) <= self.__class__._epsilon
            )

   def __str__(self):
      return "P({}, {})".format(self.x, self.y)

   def __repr__(self):
      return str(self)

   def __hash__(self):
      return hash(str(self))

   def to_serializable(self):
      """Transform this object in something json-serializable"""
      return { "x": self.x, "y": self.y }

   def from_serializable(json_obj):
      """From a json serialization reconstruct the object"""
      return Point(json_obj["x"], json_obj["y"])

   def __getitem__(self, index):
      if index == 0:
         return self.x
      if index == 1:
         return self.y

      raise IndexError("__getitem__: index {} out of bounds for subscritable".format(index))

   def distance_to(self, a, b = None):
      """Calculates distance from current point to another point or tuple of coordinates"""
      other_x, other_y = b is None and (a[0], a[1]) or (a, b)
      x1 = abs(self.x - other_x)
      y1 = abs(self.y - other_y)
      return sqrt(x1*x1 + y1*y1)

   def min_x(self):
      return self.x

   def min_y(self):
      return self.y

   def max_x(self):
      return self.x

   def max_y(self):
      return self.y

   def clone(self):
      return Point(self.x, self.y)

   def cross_product(self, other):
      """Returns an integer obtained as the cross product of the two points"""
      return self.x * other.y - self.y * other.x

   ##########################
   # TRANSFORMATION METHODS #
   ##########################

   def traslate(self, x_amount, y_amount):
      """Traslates the current point by the supplied amount, and return self for chainability"""
      self.x += x_amount
      self.y += y_amount
      return self

   def reflect_y(self):
      self.y = -self.y

      return self

   def rotate(self, grades, center_x = 0, center_y = 0):
      theta = radians(grades)
      self.x -= center_x
      self.y -= center_y
      x = self.x * cos(theta) - self.y * sin(theta)
      y = self.x * sin(theta) + self.y * cos(theta)
      self.x = center_x + self._round(x)
      self.y = center_y + self._round(y)

      return self

   def scale(self, amount_x, amount_y = None):
      amount_y = amount_y or amount_x
      self.x = self.x * amount_x
      self.y = self.y * amount_y

      return self

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

   # Anomaly! Use carefully, only defined by Point
   def rotated_clockwise(self):
      """Returns a new point, rotated 90 grades clockwise, with origin as reference"""
      return Point(self.y, -self.x)
