from model.drawable  import Polygon, Point
from io              import StringIO
from utils.logger    import Logger
from itertools       import chain, groupby
from config_manager  import ConfigManager
import svgwrite

class FloorDrawer():

   @classmethod
   def draw_floor(self, floor):
      """
      Create and save a map (in svg format) representing a floor.

      Arguments:
      - floor: a dictionary representing a merged floor.

      Returns: None
      """
      self.room_colors     = {
         "Aula"               : "rgb(39,  88,  107)",
         "Aula Informatica"   : "rgb(97,  126, 136)",
         "WC"                 : "rgb(122, 64,  0  )",
         "Antibagno"          : "rgb(122, 64,  0  )",
         "Corridoio"          : "rgb(120, 120, 120)",
         "Ascensore"          : "rgb(225, 0,   0  )",
         "Vano Scala"         : "rgb(170, 57,  57 )",
         "Studio"             : "rgb(136, 162, 54 )",
         "Ufficio"            : "rgb(136, 162, 54 )",
         "Sala Lauree"        : "rgb(125, 42,  104)",
         "Sala Riunioni"      : "rgb(143, 74,  126)"
      }

      svg                  = svgwrite.Drawing()

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

      if len(svg.elements) <= 1:
         Logger.warning("Impossible generate csv: no room polylines founded")
      return svg

   @classmethod
   def _prepare_cat_name(self, cat_name):
      id_cat_name = cat_name.replace(" ", "-")
      return id_cat_name[0:11]

   @classmethod
   def _create_room_group(self, svg, r_id, room):

      cat         = room.get("cat_name", "Sconosciuto")
      cat_color   = self._get_cat_color(cat)
      group       = svgwrite.container.Group(id = r_id)
      polygon     = FloorDrawer.create_polygon(room)

      if polygon:
         FloorDrawer.draw_room(svg, group, polygon.points, r_id, color = cat_color)
         center = polygon.center_point

         if FloorDrawer._is_cat_name_relevant(cat):
            name     = room.get("room_name", "")
            text     = svg.text(cat, (center.x - len(cat) * 4.5, center.y))
            text.add(svg.tspan(name, x = [center.x - len(cat) * 4.5], y = [center.y + 20]))
            group.add(text)

      return group

   @classmethod
   def _is_cat_name_relevant(self, cat_name):
      return not cat_name == "Corridoio" and cat_name in self.room_colors.keys()

   @classmethod
   def _get_cat_color(self, cat_name):
      return self.room_colors.get(cat_name, "rgb(220, 220, 220)")

   @classmethod
   def create_polygon(self, room):
      poly        = room.get("polygon")
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

