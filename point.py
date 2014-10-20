class Point():
   def __init__(self, a, b = None):
      a, b = b is None and (a[0], a[1]) or (a, b)
      self.x = self._round(a)
      self.y = self._round(b)

   def _round(self, a):
      return round(a, 3)

   def __eq__(self, other):
      return other.x == self.x and other.y == self.y

   def __str__(self):
      return "P({}, {})".format(self.x, self.y)

   def __repr__(self):
      return str(self)

   def to_serializable(self):
      """Transform this object in something json-serializable"""
      return ("Point", self.x, self.y)

   def from_serializable(json_obj):
      """From a json serialization reconstruct the object"""
      return Point(json_obj[1], json_obj[2])

   def __getitem__(self, index):
      if index == 0:
         return self.x
      if index == 1:
         return self.y

      raise IndexError("__getitem__: index {} out of bounds for subscritable".format(index))

   def traslated(self, x_amount, y_amount):
      """Returns a new point representing the current point translated"""
      return Point(self.x, self.y).traslate(x_amount, y_amount)

   def traslate(self, x_amount, y_amount):
      """Traslates the current point by the supplied amount, and return self for chainability"""
      self.x += x_amount
      self.y += y_amount
      return self

   def reflected_y(self):
      """Returns a new point, with y coordinate reflected_y"""
      return Point(self.x, -self.y)

   def clone(self):
      return Point(self.x, self.y)

   def rotated_clockwise(self):
      """Returns a new point, rotated 90 grades clockwise, with origin as reference"""
      return Point(self.y, -self.x)

   def cross_product(self, other):
      """Returns an integer obtained as the cross product of the two points"""
      return self.x * other.y - self.y * other.x

   def scale(self, amount):
      self.x = self.x * amount
      self.y = self.y * amount
