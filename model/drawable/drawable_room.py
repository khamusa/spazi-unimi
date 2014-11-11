from utils.myitertools import circular_pairwise
from itertools import chain
from .drawable_text import DrawableText
from .drawable_point import DrawablePoint

class DrawableRoom():
   def __init__(self, points, texts=None):
      self.points = DrawableRoom.prepare_points(points)
      self.texts  = texts or []

   def __str__(self):
      return "Stanza(" + ", ".join(str(p) for p in (self.points)) + ")"

   def __repr__(self):
      return str(self)

   def __eq__(self,other):
      return self.points == other.points and self.texts == other.texts

   def prepare_points(polypoints):
      return [DrawablePoint(point[0], point[1]) for point in polypoints]

   def to_serializable(self):
      """Transform this object in something json-serializable"""
      return {
         "points": [ el.to_serializable() for el in self.points ],
         "texts": [ el.to_serializable() for el in self.texts ]
      }

   def from_serializable(json_obj):
      """From a json serialization reconstruct the object"""
      r = DrawableRoom( (DrawablePoint.from_serializable(p) for p in json_obj["points"]), \
         [DrawableText.from_serializable(t) for t in json_obj["texts"]] )
      return r

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
            comparison = DrawableRoom._compare_line_and_point(a, b, point)

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

   def containsText(self, text):
      return self._contains_point(text.anchor_point)

   def add_text(self, text):
      if( text not in self.texts ):
         self.texts.append(text)

   def clone(self):
      r = DrawableRoom([])
      r.points = [ p.clone() for p in self.points ]
      r.texts = [ t.clone() for t in self.texts ]
      return r

   def traslate(self, amount_x, amount_y):
      for pt in chain(self.points, self.texts):
         pt.traslate(amount_x, amount_y)
      return self

   def traslated(self, amount_x, amount_y):
      return self.clone().traslate(amount_x, amount_y)

   def offset_from_origin(self):
      """Of all points of the room's polygon return the top-left most"""
      minX = min(self.points, key=lambda s: s.x)
      minY = min(self.points, key=lambda s: s.y)

      return (minX.x, minY.y)

   def reflected_y(self):
      room        = self.clone()
      room.reflect_y()
      return room

   def reflect_y(self):
      for pt in chain(self.texts, self.points):
         pt.reflect_y()

   def scale(self, amount):
      for pt in chain(self.texts, self.points):
         pt.scale(amount)
