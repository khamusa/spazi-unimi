from model.drawable  import Polygon, Point
from io              import StringIO
from utils.logger    import Logger
from itertools       import chain
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

      unidentified_rooms = ((None, room) for room in unidentified_rooms)

      rooms = floor.get("rooms", {})
      for r_id, room in chain(rooms.items(), unidentified_rooms):

         if r_id:
            group = svgwrite.container.Group(id = r_id)

         else:
            group    = svgwrite.container.Group()

         points   = FloorDrawer.get_polygon_points(room)
         if points:
            FloorDrawer.draw_room(svg, group, points)

            if "cat_name" in room:
               group.add(svg.text(room["cat_name"], (room["polygon"]["anchor_point"]["x"], room["polygon"]["anchor_point"]["y"])))

            svg.add(group)

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
   def draw_room(self, svg, group, points):
      color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
      poly     = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666")
      group.add(poly)
