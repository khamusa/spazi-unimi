from utils.myitertools  import circular_pairwise
from itertools          import chain
from . import Point, Drawable, Anchorable, Segment

class Polygon(Drawable, Anchorable):

   def __init__(self):
      self.bounding_box = ()
      self.center_point = None

   def from_absolute_coordinates(points):
      """Factory method, creates a polygon based on absolute coordinates
      (list of tuples)"""

      # Calculate anchor point.
      min_x = min(points, key=lambda s: s[0])
      min_y = min(points, key=lambda s: s[1])

      return Polygon.from_relative_coordinates(
               (min_x[0], min_y[1]),
               [ (x-min_x[0], y-min_y[1]) for (x, y) in points ]
            )

   def from_relative_coordinates(anchor_point, points):
      """Factory method, Creates a tuple based on an anchor_point coordinates
      tuple and a list of tuples for coordinates of points (relative to the
      anchor_point)"""

      p              = Polygon()
      p.anchor_point = Point(anchor_point)
      p.points       = Polygon._prepare_points(points)
      p._calculate_bounding_box()
      return p

   def is_closed(self, tollerance = 0.5):
      """
      True if the polygon is closed, i.e. first and last points are close enough,
      which is determined by the tollerance parameter.
      """
      first = self.points[0]
      last  = self.points[-1]

      return first.distance_to(last) < tollerance

   def ensure_is_closed(self, tollerance = 0.5):
      """
      If the first and last points of the polygon are not close enough, closes
      the polygon by adding the first point as tail of the points list.
      """
      if self.is_closed():
         return self

      if len(self.points) > 2:
         self.points.append(self.points[0].clone())
         self._calculate_bounding_box()

      return self

   def simplify_close_points(self, tollerance = 0.5):
      """
      Simplify the polygon points by replacing consecutive points with a
      distance smaller than tollerance into a single point.
      If the original polygon is closed, the final one is also granted to be.

      Returns self
      """
      to_remove   = set()
      was_closed  = self.is_closed()

      points = list(enumerate(self.points))
      for i, p in points:
         if i in to_remove:
            continue

         for i2, p2 in chain(points[i+1:], points[0:i]):
            if p.distance_to(p2) < tollerance:
               to_remove.add(i2)
            else:
               break

      if to_remove:
         self.points = [ p for i, p in points if i not in to_remove ]

         if was_closed:
            self.ensure_is_closed(tollerance)
         else:
            self._calculate_bounding_box()

      return self

   def _prepare_points(polypoints):
      """From a list of tuples, create a list of Point"""
      return [Point(p[0], p[1]) for p in polypoints]

   def __str__(self):
      return (
               "Polygon(" + str(self.anchor_point) + ")" +
               "[" +
                  ", ".join([ str(p) for p in self.points ]) +
               "]"
            )

   def __repr__(self):
      return str(self)

   def __eq__(self, other):
      """TODO: order of edges should not change the result"""
      return   (
                  self.points       == other.points and
                  self.anchor_point == other.anchor_point
               )

   def clone(self):
      p              = Polygon()
      p.points       = [p.clone() for p in self.points]
      p.anchor_point = self.anchor_point.clone()
      p._calculate_bounding_box()
      return p


   def to_serializable(self):
      return   {
                  "anchor_point" : self.anchor_point.to_serializable(),
                  "points": [ el.to_serializable() for el in self.points ]
               }

   def from_serializable(json_obj):
      p = Polygon()
      p.anchor_point = Point.from_serializable( json_obj["anchor_point"] )
      p.points = [ Point.from_serializable(el) for el in json_obj["points"] ]
      p._calculate_bounding_box()
      return p

   def __entities__(self):
      """Hook method for Anchorable"""
      return chain(self.points, self.bounding_box, [self.center_point])

   #############################
   # TESTS FOR POINT INCLUSION #
   #############################

   # Uses point crossproduct to determine if a point is to the right or to
   # the left of the line that passes through a segment.
   # http://martin-thoma.com/how-to-check-if-two-line-segments-intersect/#tocAnchor-1-3-1
   def _compare_line_and_point(segment_start, segment_end, point):
      """Returns -1 if the point is to the left of the segment, 0 if it is on
      the same line as the segment, +1 if it is to the right"""

      # Traslate both the line and the point to the origin
      tmpA = segment_end.traslated(-segment_start.x, -segment_start.y)
      tmpC = point.traslated(-segment_start.x, -segment_start.y)

      # We ensure that the cross_product logic doesn't give us problems
      # if we end up with special case negative values
      if(tmpA.y < 0):  # here we reflect y only
         tmpA = tmpA.reflected_y()
         tmpC = tmpC.reflected_y()

      if(tmpA.x < 0): # here we rotate
         tmpA = tmpA.rotated_clockwise()
         tmpC = tmpC.rotated_clockwise()

      return -tmpA.cross_product(tmpC)

   def _contains_point(self, point):
      """Tests whether or not the current room cointains a specific point

      Return true if this room object contains the supplied object
      Uses the ray casting algorithm:
      http://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm
      For simplicity we assume the ray is casted horizontally to the left
   """

      # We first compare against the bounding box. For most points this will be
      # enough
      min_point, max_point = self.bounding_box

      if (
            (point.x > max_point.x) or
            (point.x < min_point.x) or
            (point.y > max_point.y) or
            (point.y < min_point.y)
         ):
         return False

      # Amount of intersections counted
      match_count = 0

      # Handle some special cases
      counted_vertices = []
      for (a, b) in circular_pairwise(self.points):

         # Is the y coordinate of the point valid? I.e.: is it between
         # the y coordinates of a and b?
         if( a.y <= point.y <= b.y or a.y >= point.y >= b.y ):

            # The following function returns -1 if the point is to the left
            # of the segment, 0 if it is on the same line as the segment,
            # +1 if it is to the right
            comparison = Polygon._compare_line_and_point(a, b, point)

            # If the point is on the same line, we can conclude it belongs
            # to the shape if its x coordinates are between a's and b's
            if(comparison == 0 and
                  max(a.x, b.x) >= point.x >= min(a.x, b.x) and
                  max(a.y, b.y) >= point.y >= min(a.y, b.y)):
               return True # the point is over a border

            # If the point is not over the line, is it to the right?
            # Being to the right means that the ray being cast to the left
            # might actually intersect the segment.
            elif(comparison > 0):

               # Simple case, the ray does not match any vertice, so it
               # intersects inside the segment.
               if ((point.y != a.y) and (point.y != b.y)):
                  match_count = match_count + 1
               else:
                  # Special cases, the ray intersects precisely one of the vertices
                  if a.y == point.y and a.x <= point.x and a not in counted_vertices:
                     counted_vertices.append(a)
                     match_count = match_count + 1
                  if b.y == point.y and b.x <= point.x and (b not in counted_vertices):
                     counted_vertices.append(b)
                     match_count = match_count + 1

      # After analyzing all segments, if we found an even amount of intersections
      # it means the point is outside of the polygon
      return match_count % 2 != 0
