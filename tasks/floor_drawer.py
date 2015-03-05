from model.drawable  import Polygon, Point
from io              import StringIO
from utils.logger    import Logger
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

      unidentified_rooms = floor.get("unidentified_rooms", [])

      for room in unidentified_rooms:

         points   = FloorDrawer.get_polygon_points(room)
         if points:
            FloorDrawer.draw_room(svg, points)

         if "cat_name" in room:
            svg.add(svg.text(room["cat_name"], (room["polygon"]["anchor_point"]["x"], room["polygon"]["anchor_point"]["y"])))

      rooms = floor.get("rooms", [])
      for r_id, room in rooms.items():

         points   = FloorDrawer.get_polygon_points(room)
         if points:
            FloorDrawer.draw_room(svg, points)
            text = r_id

            if "cat_name" in room:
               text = text + " - " + room["cat_name"]

            svg.add(svg.text(text, (room["polygon"]["anchor_point"]["x"], room["polygon"]["anchor_point"]["y"])))
      if len(svg.elements) <= 1:
         Logger.warning("Impossible generate csv: no room polylines founded")
      return svg

   @classmethod
   def get_polygon_points(self, room):
      poly     = room.get("polygon")
      if poly:
         polygon  = Polygon.from_serializable(poly)
         polygon.absolutize()
         return polygon.points

   @classmethod
   def draw_room(self, svg, points):
      color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
      poly     = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666")
      svg.add(poly)
