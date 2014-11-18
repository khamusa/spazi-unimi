from . import DrawablePoint
class DrawableLine:

   def __init__(self, p1, p2):
      self.start  = DrawablePoint(p1)
      self.end    = DrawablePoint(p2)

   def __eq__(self, o):
      """Two lines are equal even if they have different direction!"""
      return (
         (self.start == o.start and self.end == o.end) or
         (self.start == o.end and self.end == o.start)
         )

   def __str__(self):
      return "L({} -> {})".format(self.start, self.end)

   def __repr__(self):
      return str(self)

   def traslate(self, amount_x, amount_y):
      """Moves the line by amount_x, amount_y points"""
      self.start.traslate(amount_x, amount_y)
      self.end.traslate(amount_x, amount_y)
      return self

   def rotate(self, grades, center_x = 0, center_y = 0):
      self.start.rotate(grades, center_x, center_y)
      self.end.rotate(grades, center_x, center_y)
      return self

   def clone(self):
      return DrawableLine(self.start.clone(), self.end.clone())

   def scale(self, amount_x, amount_y = None):
      """Scales the line on the x or y coordinates, or both"""
      self.start.scale(amount_x, amount_y)
      self.end.scale(amount_x, amount_y)
      return self


