from model.drawable  import Polygon, Point
from io              import StringIO
from utils.logger    import Logger
from itertools       import chain, groupby
from config_manager  import ConfigManager
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
      config = ConfigManager("config/svg_categories.json")
      svg = svgwrite.Drawing()

      unidentified_rooms = floor.get("unidentified_rooms", [])

      unidentified_rooms = ((None, room) for room in unidentified_rooms)

      rooms = floor.get("rooms", {})

      cats_svg = []
      for r_id, room in chain(rooms.items(), unidentified_rooms):

         if "cat_name" in room:
            cat_id   =  room["cat_name"].replace(" ", "-")
            group    = svgwrite.container.SVG(id = cat_id[0:11])

         else:
            group    = svgwrite.container.SVG()

         polygon  = FloorDrawer.create_polygon(room)

         if polygon:
            FloorDrawer.draw_room(svg, group, polygon.points, r_id)

            center = polygon.center_point

            cat = room.get("cat_name", "Sconosciuto")
            group.add(svg.text(cat, (center.x, center.y)))

            svg.add(group)

      if len(svg.elements) <= 1:
         Logger.warning("Impossible generate csv: no room polylines founded")
      return svg

   @classmethod
   def create_polygon(self, room):
      poly     = room.get("polygon")
      if poly:
         polygon  = Polygon.from_serializable(poly)
         polygon.absolutize()
         return polygon

   @classmethod
   def draw_room(self, svg, group, points, r_id):
      color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
      if r_id:
         poly  = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666", id = r_id)
      else:
         poly  = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666")
      group.add(poly)
