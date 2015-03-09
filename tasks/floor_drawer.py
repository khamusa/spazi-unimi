from model.drawable  import Polygon, Point
from io              import StringIO
from utils.logger    import Logger
from itertools       import chain, groupby
from config_manager  import ConfigManager
import svgwrite, re

class FloorDrawer():

   @classmethod
   def draw_floor(klass, floor):
      """
      Create and save a map (in svg format) representing a floor.

      Arguments:
      - floor: a dictionary representing a merged floor.

      Returns: None
      """
      svg                  = svgwrite.Drawing()
      svg.add(FloorDrawer._get_style(svg))

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
   def _create_room_group(klass, svg, r_id, room):
      """
      Create an svg Group that contains room's elements: a polyline and a text.

      Arguments:
      - svg: the svg we are editing;
      - r_id: a string representing the room id;
      - room: a dictionary representing the room's informations.

      Returns:
      - an svg Group.
      """
      cat         = room.get("cat_name", "Sconosciuto")
      group       = svgwrite.container.Group(id = r_id)
      polygon     = FloorDrawer._create_polygon(room)

      if polygon:
         FloorDrawer._draw_room(svg, group, polygon.points, r_id, color = "rgb(220, 220, 220)")
         center = polygon.center_point

         if FloorDrawer._is_cat_name_relevant(cat):
            name     = room.get("room_name", "")
            text     = svg.text(cat, (center.x - len(cat) * 4.5, center.y))
            text.add(svg.tspan(name, x = [center.x - len(cat) * 4.5], y = [center.y + 20]))
            group.add(text)

      return group

   @classmethod
   def _create_polygon(klass, room):
      """
      Create a polygon from a room's polyline.

      Arguments:
      - room: a dictionary representing the room's informations.

      Returns:
      - a polygon object.
      """
      poly        = room.get("polygon")
      if poly:
         polygon  = Polygon.from_serializable(poly)
         polygon.absolutize()
         return polygon

   @classmethod
   def _draw_room(klass, svg, group, points, r_id, color):
      """
      Add an svg polyline from a points list to a group.

      Arguments:
      - svg: the svg we are editing;
      - group: the svg Group we want update with the polyline;
      - points: a list representing the points of the polyline;
      - color: the fill color for the polyline.

      Returns: None.
      """
      if r_id:
         poly  = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666", id = r_id)
      else:
         poly  = svg.polyline( ((p.x, p.y) for p in points), fill=color, stroke="#666")
      group.add(poly)

   @classmethod
   def _get_style(klass, svg):
      """
      Read the svg.css file and return an svg Style object that contains his
      informations.

      Arguments:
      - svg: the svg we are editing.

      Returns:
      - an svg Style object.
      """
      with open("assets/svg.css") as fp:
         return svg.style(fp.read())

   @classmethod
   def _prepare_cat_name(klass, cat_name):
      """
      Prepare a cat name to be used as svg's id.

      Arguments:
      - cat_name: a string representing a room category name.

      Returns: a string representing a cat_name usable as svg's id.
      """
      if cat_name.strip():
         return re.sub("[^a-zA-Z]", "-", cat_name)
      return "Sconosciuto"

   @classmethod
   def _is_cat_name_relevant(klass, cat_name):
      """
      Say if a cat_name can be added as text to the room's group.

      Arguments:
      - cat_name: a string representing a room category name.

      Returns: True or False.
      """
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

