from model.drawable  import Polygon, Point
from io              import StringIO
from utils.logger    import Logger
from itertools       import chain, groupby
from config_manager  import ConfigManager
import svgwrite, re

class FloorDrawer():

   @classmethod
   def draw_floor(self, floor):
      """
      Create and save a map (in svg format) representing a floor.

      Arguments:
      - floor: a dictionary representing a merged floor.

      Returns: None
      """
      svg                  = svgwrite.Drawing()
      svg.add(FloorDrawer._get_style(svg))

      walls                = floor.get("walls", [])
      walls_group          = self._create_walls_group(svg, walls)

      unidentified_rooms   = floor.get("unidentified_rooms", [])
      unidentified_rooms   = ((None, room) for room in unidentified_rooms)
      rooms                = floor.get("rooms", {})
      all_rooms            = chain(rooms.items(), unidentified_rooms)

      get_cat_name         = lambda room: room[1].get("cat_name", "Sconosciuto")
      all_rooms            = sorted(all_rooms, key = get_cat_name)
      rooms_by_cat         = groupby(all_rooms, key = get_cat_name)

      for cat_name, cat_rooms in rooms_by_cat:
         id_cat_name = FloorDrawer._prepare_cat_name(cat_name)
         cat_group   = svgwrite.container.Group(id = id_cat_name)

         for r_id, room in cat_rooms:
            room_group = FloorDrawer._create_room_group(svg, r_id, room)
            cat_group.add(room_group)

         svg.add(cat_group)


      svg.add(walls_group)

      if len(svg.elements) <= 1:
         Logger.warning("Impossible generate csv: no room polylines founded")
      return svg

   @classmethod
   def _create_walls_group(self, svg, walls):
      g = svgwrite.container.Group(id = "walls")

      for p in walls:
         poly = self.create_polygon(p)
         g.add( svg.polyline( ((p.x, p.y) for p in poly.points), fill="rgb(0,0,0)") )

      return g

   @classmethod
   def _get_style(self, svg):
      with open("assets/svg.css") as fp:
         return svg.style(fp.read())

   @classmethod
   def _prepare_cat_name(self, cat_name):
      if cat_name.strip():
         return re.sub("[^a-zA-Z]", "-", cat_name)

      return "Sconosciuto"

   @classmethod
   def _create_room_group(self, svg, r_id, room):

      cat         = room.get("cat_name", "Sconosciuto")
      group       = svgwrite.container.Group(id = r_id)
      polygon     = FloorDrawer.create_polygon(room.get("polygon"))

      if polygon:
         FloorDrawer.draw_room(svg, group, polygon.points, r_id, color = "rgb(220, 220, 220)")
         center      = polygon.center_point
         center.y    += 10

         if FloorDrawer._is_cat_name_relevant(cat):
            name     = room.get("room_name", "")
            text     = svg.text(cat, (center.x - len(cat) * 8, center.y))
            text.add(svg.tspan(name, x = [center.x - len(cat) * 8], y = [center.y + 35]))
            group.add(text)

      return group

   @classmethod
   def _is_cat_name_relevant(self, cat_name):
      exceptions = [
         "Sconosciuto",
         "Corridoio",
         "Atrio",
         "Corridoio",
         "Balcone",
         "Porticato",
         "Terrazzo",
         "Cortile"
      ]
      return cat_name not in exceptions

   @classmethod
   def create_polygon(self, poly):
      if poly:
         polygon  = Polygon.from_serializable(poly)
         polygon.absolutize()
         return polygon

   @classmethod
   def draw_room(self, svg, group, points, r_id, color):
      if r_id:
         poly  = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666", id = r_id)
      else:
         poly  = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666")
      group.add(poly)

