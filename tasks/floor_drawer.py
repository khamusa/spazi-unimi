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
      svg.add(klass._get_style(svg))

      walls                = floor.get("walls", [])
      walls_group          = klass._create_group(svg, walls, "walls")
      svg.add(walls_group)

      windows              = floor.get("windows", [])
      windows_group        = klass._create_group(svg,  windows, "windows")
      svg.add(windows_group)

      unidentified_rooms   = floor.get("unidentified_rooms", [])
      unidentified_rooms   = ((None, room) for room in unidentified_rooms)
      rooms                = floor.get("rooms", {})
      all_rooms            = chain(rooms.items(), unidentified_rooms)

      get_cat_name         = lambda room: room[1].get("cat_name", "Sconosciuto")
      all_rooms            = sorted(all_rooms, key = get_cat_name)
      rooms_by_cat         = groupby(all_rooms, key = get_cat_name)

      for cat_name, cat_rooms in rooms_by_cat:
         id_cat_name = klass._prepare_cat_name(cat_name)
         cat_group   = svgwrite.container.Group(id = id_cat_name)

         for r_id, room in cat_rooms:
            room_group = klass._create_room_group(svg, r_id, room)
            cat_group.add(room_group)

         svg.add(cat_group)

      if len(svg.elements) <= 1:
         Logger.warning("Impossible generate csv: no room polylines founded")
      return svg

   @classmethod
   def _create_group(klass, svg, lines, group_name):
      g = svgwrite.container.Group(id = group_name)

      for start, end in lines:
         g.add( svg.line( start=(start["x"], start["y"]), end=(end["x"], end["y"]) ) )

      return g

   @classmethod
   def _get_style(klass, svg):
      with open("assets/svg.css") as fp:
         return svg.style(fp.read())

   @classmethod
   def _prepare_cat_name(klass, cat_name):
      if cat_name.strip():
         return re.sub("[^a-zA-Z]", "-", cat_name)

      return "Sconosciuto"

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
      polygon     = klass._create_polygon(room.get("polygon"))

      if polygon:
         klass._draw_room(svg, group, polygon.points, r_id)
         center      = polygon.center_point
         center.y    += 10

         if klass._is_cat_name_relevant(cat):
            name     = room.get("room_name", "")
            text     = svg.text(cat, (center.x - len(cat) * 4, center.y))
            text.add(svg.tspan(name, x = [center.x - len(cat) * 4], y = [center.y + 20]))
            group.add(text)

      return group

   @classmethod
   def _create_polygon(klass, poly):
      """
      Create a polygon from a room's polyline.

      Arguments:
      - poly: a dictionary representing the room's polygon informations.

      Returns:
      - a polygon object.
      """
      if poly:
         polygon  = Polygon.from_serializable(poly)
         polygon.absolutize()
         return polygon

   @classmethod
   def _draw_room(klass, svg, group, points, r_id):
      """
      Add an svg polyline from a points list to a group.

      Arguments:
      - svg: the svg we are editing;
      - group: the svg Group we want update with the polyline;
      - points: a list representing the points of the polyline;

      Returns: None.
      """
      if r_id:
         poly  = svg.polyline( ((p.x, p.y) for p in points), id = r_id, fill="rgb(255, 255, 255)")
      else:
         poly  = svg.polyline( ((p.x, p.y) for p in points), fill="rgb(255, 255, 255)")
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

