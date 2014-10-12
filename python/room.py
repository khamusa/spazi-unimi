from itertools import tee, chain

def circular_pairwise(iterable):
   """s -> (s0,s1), (s1,s2), (s2, s3), ... (sn, s0) """
   a, b = tee(iterable)
   next(b, None)
   return chain(zip(a, b), [(iterable[-1], iterable[0])])


class Point():
   def __init__(self, a, b = None):
      a, b = b is None and (a[0], a[1]) or (a, b)
      self.x = a
      self.y = b

   def __eq__(self, other):
      return other.x == self.x and other.y == self.y

   def __str__(self):
      return "P({}, {})".format(self.x, self.y)

   def __repl__(self):
      return self.str()

class Room():
   def __init__(self, points):
      self.points = Room.sanitize_polypoints(points)

   def sanitize_polypoints(polypoints):
      return [Point( round(point[0], 1), round(point[1], 1) ) for point in polypoints]

   def compare_line_and_point(a, b, c):
      tmpA = Point(b.x - a.x, b.y - a.y)
      tmpC = Point(c.x - a.x, c.y - a.y)

      # here we mirror - incorrect
      if(tmpA.y < 0):  # here we reflect y only
         tmpA.y = -tmpA.y
         tmpC.y = -tmpC.y

      if(tmpA.x < 0): # here we rotate
         tmpA.x, tmpA.y = tmpA.y, -tmpA.x
         tmpC.x, tmpC.y = tmpC.y, -tmpC.x

      cross = tmpA.x * tmpC.y - tmpA.y * tmpC.x
      return -cross

   # Return true if this room object contains the supplied object
   def contains_point(self, point_or_x, y = None):
      """Tests wether or not the current room cointains a specific point"""
      # We're going to use as a reference a horizontal line that passes
      # through (x,y), i.e: the constant y, but we're going to consider it in only
      # one direction (to the left, I.e.: the point must be to the right of
      # the considered polygon segment)

      point = Point(point_or_x, y)

      match_count = 0
      counted_vertices = []
      for (a, b) in circular_pairwise(self.points):
         if( a.y <= point.y <= b.y or a.y >= point.y >= b.y ):
            # The point satisfies the first precondition to intersect the
            # considered segment (it's y is valid)            

            comparison = Room.compare_line_and_point(a, b, point)
            # The point is on the same line, hence to know if it is actually
            # over the segment, we compare the segment bounding box to the
            # point location. If it is over the segment, it is inside the polygon
            if(comparison == 0 and 
                  max(a.x, b.x) >= point.x >= min(a.x, b.x) and
                  max(a.y, b.y) >= point.y >= min(a.y, b.y)):
               return True # the point is over a border

            # Point is not over the line, but is to its right, so we must count
            # the number of intersections
            elif(comparison > 0):

               # Simples case, the ray does not match any vertice, so it 
               # intersects inside the segment
               if ((point.y != a.y) and (point.y != b.y)):
                  match_count = match_count + 1
               else:
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
      original_points = [(0.33, 0), (0, 10.19), (10.33, 10), (10.5, 0.898)]
      room = Room(original_points)

      # points have been saved?
      self.assertTrue(room.points)

      # test coordinates sanitization (floating point imprecision doesn't seem
      # to cause any problems)
      self.assertEqual(room.points, [Point(0.3, 0), Point(0, 10.2), Point(10.3, 10), Point(10.5, 0.9)])

   def test_point_to_right_of_line(self):
      self.assertTrue(Room.compare_line_and_point( Point(10, 0), Point(0, 10), Point(9.9, 9.9)) > 0 )
      self.assertTrue(Room.compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 2)) > 0 )
      self.assertTrue(Room.compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8)) > 0 )
      self.assertTrue(Room.compare_line_and_point( Point(0, 0), Point(1, 9), Point(1, 8.99999)) > 0 )

      # Diagonal line
      self.assertFalse(Room.compare_line_and_point( Point(1, 1), Point(9, 9), Point(1, 2)) > 0 )
      self.assertFalse(Room.compare_line_and_point( Point(0, 0), Point(9, 9), Point(1, 8)) > 0 )
      self.assertFalse(Room.compare_line_and_point( Point(9, 9), Point(5, 5), Point(1, 6)) > 0 )

      # Horizontal line with point aligned
      self.assertTrue(Room.compare_line_and_point( Point(0, 0), Point(10, 0), Point(4, 0)) == 0 )

      # vertical line with point aligned
      self.assertTrue(Room.compare_line_and_point( Point(0, 0), Point(0, 10), Point(0, 5)) == 0 )


   def test_room_contains_point(self):
      room = Room([(0,0),(10,0),(10,10),(0,10)])

      def room_contains(room, p1, p2):
            self.assertTrue( room.contains_point(p1, p2), "Failed for {}, {}".format(p1, p2) )

      # Points definetely inside
      for x, y in circular_pairwise(range(1,10)):
         room_contains(room, x, y)

      # Inside
      room_contains(room, 0.1, 0.001)
      room_contains(room, 9.99, 9.7) 
      room_contains(room, 5, 9.99)   
      room_contains(room, 0.1, 8)    

      # Close to the border
      room_contains(room, 0.001, 0.001)
      room_contains(room, 9.999, 9.999)

      print("points outside")
      # Points definetely outside
      self.assertFalse( room.contains_point(5, -4)    )
      self.assertFalse( room.contains_point(5, 11)    )
      self.assertFalse( room.contains_point(10.001, 10.001)  )
      self.assertFalse( room.contains_point(-2, 5) )   

      print("Points on the border are considered inside ")
      room_contains(room, 5, 0)     
      room_contains(room, 10, 5)    
      room_contains(room, 5, 10)    
      room_contains(room, 0, 5)     
      # Points precisely over the border
      room_contains(room, 0, 0)   
      room_contains(room, 10, 0)  
      room_contains(room, 10, 10) 
      room_contains(room, 0, 10)  

      room2 = Room([(10,0), (0, 10), (-10, 0), (0, -10)])

      # Close to the vertices
      room_contains(room2, 9.9, 0)  
      room_contains(room2, 0, 9.9)  
      room_contains(room2, -9.9, 0) 
      room_contains(room2, 0, -9.9)  
      # Close to the center
      room_contains(room2, 0.001, 0.001)
      room_contains(room2, 3, 3)
      room_contains(room2, -4.8, -4.8)
      room_contains(room2, 4.1, 3.8)

      print("points outside")
      # Points definetely outside
      self.assertFalse( room2.contains_point(9.9, 9.9)   )
      self.assertFalse( room2.contains_point(10.2, 0)     )
      self.assertFalse( room2.contains_point(0, -10.1)    )
      self.assertFalse( room2.contains_point(10.001, 10.001)   )
      self.assertFalse( room2.contains_point(33, 12)     )

      print("Points on the border are considered inside ")
      # Points precisely over the border
      room_contains(room2, 10, 0)      
      room_contains(room2, 0, 10)     
      room_contains(room2, -10, 0)    
      room_contains(room2, 0, -10)      


if __name__ == '__main__':
   unittest.main()
