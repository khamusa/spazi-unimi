from .drawable import Drawable
from .point import Point

class Segment(Drawable):

   def __init__(self, start, end):
      self.start        = start
      self.end          = end
      self.slope        = self.__class__._calculate_slope(start, end)

      if not self.is_vertical():
         self.y_intercept = start.y - self.slope * start.x
         self.x_value     = None
      else:
         self.y_intercept = None
         self.x_value     = start.x

      super().__init__()

   @classmethod
   def from_tuples(klass, start_tuple, end_tuple):
      segment = klass( Point(start_tuple), Point(end_tuple) )
      return segment

   @classmethod
   def from_coordinates(klass, x1, y1, x2, y2):
      return klass.from_tuples( (x1, y1), (x2, y2) )

   def __str__(self):
      return "Segment({} <--> {})".format(self.start, self.end)

   def __repr__(self):
      return str(self)

   def __eq__(self, other):
      if type(other) is not Segment:
         try:
            other = Segment(other[0], other[1])
         except Exception:
            return False

      return (
         (self.start == other.start and self.end == other.end) or
         (self.start == other.end and self.end == other.start)
      )

   def __getitem__(self, index):
      if index == 0:
         return self.start
      if index == 1:
         return self.end

      raise IndexError("__getitem__: index {} out of bounds for subscritable".format(index))

   # Tests / questions
   def length(self):
      return self.start.distance_to(self.end)

   def is_vertical(self):
      """Returns True if current segment is on a vertical line"""
      return self.slope == float("+inf")

   def contains_point(self, x, y = None):
      """Returns True if the segment contains the supplied point. The point
      can be passed as a single Point object or as x, y coordinates"""
      x, y = y is not None and Point(x, y) or Point(x[0], x[1])

      cond1 = self.min_x() <= x <= self.max_x()
      cond2 = self.min_y() <= y <= self.max_y()
      return self.is_point_on_same_line(x, y) and cond1 and cond2

   def is_point_on_same_line(self, x, y = None):
      """Returns True if the supplied point is on the same line as the current
      Segment"""
      x, y = y is not None and (x, y) or (x[0], x[1])

      if self.is_vertical():
         return Point(x, 0) == Point(self.x_value, 0)
      else:
         return Point(0, y) == Point(0, (self.slope * x + self.y_intercept))

   def links_with(self, other, tollerance = 0.05):
      """
      Returns true if current segment can be linked to other segment, i.e,
      starting or ending points of both are close enough
      """
      return (
         self.start.distance_to(other.start) < tollerance or
         self.start.distance_to(other.end) < tollerance or
         self.end.distance_to(other.end) < tollerance or
         self.end.distance_to(other.start) < tollerance
      )

   def intersect_with(self, other):
      """
      Tests whether or not two segments intersect.

      Return value:
      - True if the two segments are on the same line and overlaps on at least
      one point.
      - False if the two segments never intersect
      - a Point object indicating the intersectino point if the segments
      intersect.
      """
      point = self._lines_intersection(other)

      if point is False:
         return False

      if point is True:
         return not(
                  self.min_x() > other.max_x() or
                  other.min_x() > self.max_x() or
                  self.min_y() > other.max_y() or
                  other.min_y() > self.max_y()
                  )

      else:
         return (
            self.contains_point(point) and
            other.contains_point(point) and
            point
            )

   def _lines_intersection(self, other):
      """
      Tests whether or not the line on which two segments stand intersect.

      Return value:
      - True if the two lines are actually the same
      - False if the two lines are parallel and, hence, never intersect
      - a Point object indicating the intersectino point.
      """

      the_slope, the_y_intercept = False, False

      # parallel?
      if self.slope == other.slope:
         return (
            self.y_intercept == other.y_intercept and
            self.x_value == other.x_value
            )

      if self.is_vertical():
         x                 = self.x_value
         the_slope         = other.slope
         the_y_intercept   = other.y_intercept
      elif other.is_vertical():
         x                 = other.x_value
      else:
         x = (other.y_intercept - self.y_intercept) / (self.slope - other.slope)

      if the_slope is None or the_slope is False:
         the_slope         = self.slope
         the_y_intercept   = self.y_intercept

      y = the_slope * x + the_y_intercept

      return Point(x, y)

   @classmethod
   def _calculate_slope(klass, p1, p2):
      """
      Given two points, calculate the slope of the line passing through them.
      The slope is the m value of the line equation y = mx + b
      """
      xdiff = p1.x - p2.x
      if xdiff:
         return (p1.y - p2.y) / xdiff
      else:
         return float("+inf")

   def __entities__(self):
      return (self.start, self.end)

   def to_serializable(self):
      return [ self.start.to_serializable(), self.end.to_serializable() ]

   def from_serializable(data):
      return Segment(
         Point.from_serializable(data[0]),
         Point.from_serializable(data[1])
      )
