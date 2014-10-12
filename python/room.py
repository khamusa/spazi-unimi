from point import Point
from myitertools import circular_pairwise

class Room():
   def __init__(self, points):
      self.points = Room.prepare_points(points)

   def prepare_points(polypoints):
      return [Point(point[0], point[1]) for point in polypoints]

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

   # Return true if this room object contains the supplied object
   # Uses the ray casting algorithm:
   # http://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm
   # For simplicity we assume the ray is casted horizontally to the left
   def contains_point(self, point_or_x, y = None):
      """Tests wether or not the current room cointains a specific point"""
      point = Point(point_or_x, y)

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
            comparison = Room._compare_line_and_point(a, b, point)

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



import unittest
class RoomTest(unittest.TestCase):
   def test_room_creation(self):
      original_points = [(0.3333333, 0.123123), (0.2222333, 10.19), (10.33334, 10.78530), (10.51111, 0.898999)]
      room = Room(original_points)

      # points have been saved?
      self.assertTrue(room.points)

   def test_point_to_right_of_line(self):
      self.assertTrue(Room._compare_line_and_point( Point(10, 0), Point(0, 10), Point(9.9, 9.9)) > 0 )
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 2)) > 0 )
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8)) > 0 )
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8.999)) > 0 )

      # Diagonal line
      self.assertFalse(Room._compare_line_and_point( Point(1, 1), Point(9, 9), Point(1, 2)) > 0 )
      self.assertFalse(Room._compare_line_and_point( Point(0, 0), Point(9, 9), Point(1, 8)) > 0 )
      self.assertFalse(Room._compare_line_and_point( Point(9, 9), Point(5, 5), Point(1, 6)) > 0 )

      # Horizontal line with point aligned
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(10, 0), Point(4, 0)) == 0 )

      # vertical line with point aligned
      self.assertTrue(Room._compare_line_and_point( Point(0, 0), Point(0, 10), Point(0, 5)) == 0 )


   def test_room_contains_point(self):
      room = Room([(0,0),(10,0),(10,10),(0,10)])

      def room_contains(room, x, y):
            self.assertTrue( room.contains_point(x, y), "Room should contain {}, {}".format(x, y) )

      def room_not_contains(room, x, y):
            self.assertFalse( room.contains_point(x, y), "Room should not contain {}, {}".format(x, y) )

      # Points inside
      for x, y in circular_pairwise(range(1,10)):
         room_contains(room, x, y)

      expected_truth = [
         # Inside, but near borders
         (0.1, 0.001),
         (9.99, 9.7), 
         (5, 9.99),   
         (0.1, 8),    

         # Close to the border
         (0.001, 0.001),
         (9.999, 9.999),

         # Points precisely on the border
         (5, 0),     
         (10, 5),    
         (5, 10),    
         (0, 5),     
         (0, 0),   
         (10, 0),  
         (10, 10), 
         (0, 10)  
      ]

      for x, y in expected_truth:
         room_contains(room, x, y)

      # Points outside
      expected_lie = [
         (5, -4),
         (5, 11),  
         (10.001, 10.001),  
         (-2, 5)
      ]

      for x, y in expected_lie:
         room_not_contains(room, x, y)

      room2 = Room([(10,0), (0, 10), (-10, 0), (0, -10)])
      
      expected_truth = [
         # Close to the vertices
         (9.9, 0), (0, 9.9), (-9.9, 0), (0, -9.9),  
         # Close to the center
         (0.001, 0.001), (3, 3), (-4.8, -4.8), (4.1, 3.8),

         # Points precisely over the border
         (10, 0), (0, 10), (-10, 0), (0, -10)      
      ]

      for x, y in expected_truth:
         room_contains(room2, x, y)

      expected_lie = [
         # Points definetely outside
         (9.9, 9.9), (10.2, 0), (0, -10.1), (10.001, 10.001), (33, 12)
      ]

      for x, y in expected_lie:
         room_not_contains(room2, x, y)

if __name__ == '__main__':
   unittest.main()
