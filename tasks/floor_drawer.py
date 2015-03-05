from model.drawable  import Polygon, Point
from io              import StringIO
import svgwrite, random

class FloorDrawer():

   @classmethod
   def draw_floor(self, floor):
      """
      Create and save a map (in svg format) representing a floor.

      Arguments:
      - floor: a dictionary representing a merged floor.

      Returns: None
      """
      svg = svgwrite.Drawing()

      for room in floor["unidentified_rooms"]:

         points   = FloorDrawer.get_polygon_points(room)
         FloorDrawer.draw_room(svg, points)

         if "cat_name" in room:
            svg.add(svg.text(room["cat_name"], (room["polygon"]["anchor_point"]["x"], room["polygon"]["anchor_point"]["y"])))

      for room in floor["rooms"].values():

         points   = FloorDrawer.get_polygon_points(room)
         FloorDrawer.draw_room(svg, points)

         if "cat_name" in room:
            svg.add(svg.text(room["cat_name"], (room["polygon"]["anchor_point"]["x"], room["polygon"]["anchor_point"]["y"])))

      return svg

   @classmethod
   def get_polygon_points(self, room):
      polygon  = Polygon.from_serializable(room["polygon"])
      polygon.absolutize()
      return polygon.points

   @classmethod
   def draw_room(self, svg, points):
      color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
      poly     = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666")
      svg.add(poly)
