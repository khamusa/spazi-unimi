from model.drawable  import Polygon
from utils.logger    import Logger
from itertools       import chain, groupby

import lesscpy
import svgwrite, re
import rdp


class FloorDrawer():

   css_style = ""

   @classmethod
   def draw_floor(klass, floor):
      """
      Create and save a map (in svg format) representing a floor.

      Arguments:
      - floor: a dictionary representing a merged floor.

      Returns: None
      """
      klass.max_x          = 0
      klass.svg            = svgwrite.Drawing()
      klass._add_style_to_svg()

      window_lines         = floor.get("windows", [])
      windows_group        = klass._create_lines_group(window_lines, group_id="windows")

      wall_lines           = floor.get("walls", [])
      walls_group          = klass._create_lines_group(wall_lines, group_id="walls")

      rooms_group          = klass._create_rooms_group(floor)
      rooms_labels_g       = klass._create_rooms_labels_group(floor)

      legend               = klass._create_legend_group(floor)

      klass.svg.add(windows_group)
      klass.svg.add(rooms_group)
      klass.svg.add(walls_group)
      klass.svg.add(rooms_labels_g)
      klass.svg.add(legend)

      if len(klass.svg.elements) <= 1:
         Logger.warning("Impossible generate csv: no room polylines founded")

      return klass.svg

   @classmethod
   def _create_legend_group(klass, floor):
      circle_radius = 7
      line_height   = 26
      all_rooms     = klass._get_all_rooms(floor)
      all_cats      = set()

      for r_id, room in all_rooms:
         polygon     = klass._create_polygon(room.get("polygon"))
         klass.max_x = max(klass.max_x, polygon.max_x())
         all_cats.add( room.get("cat_name", "Sconosciuto") )

      legend_group  = svgwrite.container.Group(id = "legend")
      x             = klass.max_x + 25
      y             = 25
      for cat_name in sorted(all_cats):
         cat_group  = svgwrite.container.Group(
            id = "L-"+klass._prepare_cat_name(cat_name)
         )
         cat_group.add(
            klass.svg.circle((x, y - circle_radius), circle_radius)
         )
         cat_group.add(
            klass.svg.text(cat_name, (x + circle_radius + 3, y) )
         )

         legend_group.add(cat_group)
         y += line_height

      return legend_group

   @classmethod
   def _add_style_to_svg(klass):
      """
      Compile the assets/svg.less file and return an svg Style object that
      contains the css formatting.

      Returns None
      """
      if not klass.css_style:
         klass.css_style = lesscpy.compile("assets/svg.less")

      klass.svg.add(klass.svg.style(klass.css_style))

   @classmethod
   def _create_lines_group(klass, lines, group_id):
      """
      Given a list of lines and a group name, creates and returns an
      svg group object containing drawings of all lines.
      """
      g = svgwrite.container.Group(id = group_id)

      for start, end in lines:
         klass.max_x = max(klass.max_x, start["x"], end["x"])
         g.add( klass.svg.line(
            start= klass._approximate_coordinates( start["x"], start["y"] ),
            end= klass._approximate_coordinates( end["x"], end["y"] )
            )
         )

      return g

   @classmethod
   def _create_rooms_group(klass, floor):
      """
      Creates an svg group with id "rooms" containing all identified and non
      identified rooms in floor, grouped by category, in the following
      format:

      g#rooms
         g#category_1
            g#R009
               <room drawing and text>
            g#R010
               <room drawing and text>
            [...]
         g#category_2
            g#R009
               <room drawing and text>
            g#R010
               <room drawing and text>
            [...]
         [...]
      """
      all_rooms            = klass._get_all_rooms(floor)
      rooms_group          = svgwrite.container.Group(id = "rooms")


      get_cat_name         = lambda room: room[1].get("cat_name", "Sconosciuto")
      all_rooms            = sorted(all_rooms, key = get_cat_name)
      rooms_by_cat         = groupby(all_rooms, key = get_cat_name)

      for cat_name, cat_rooms in rooms_by_cat:
         id_cat_name = klass._prepare_cat_name(cat_name)
         cat_group   = svgwrite.container.Group(id = id_cat_name)

         for r_id, room in cat_rooms:
            room_group = klass._create_room_group(
               r_id,
               room.get("room_name", ""),
               room.get("cat_name", "Sconosciuto"),
               klass._create_polygon(room.get("polygon"))
               )
            cat_group.add(room_group)

         rooms_group.add(cat_group)

      return rooms_group


   @classmethod
   def _create_rooms_labels_group(klass, floor):
      """
      Creates a group of texts where each one has the name of an identified
      room. The text element itself has as id attribute the room id.
      """
      rooms_labels_g = svgwrite.container.Group(id = "identified_rooms_labels")

      for r_id, room in floor["rooms"].items():
         if "polygon" not in room:
            continue

         center = klass._create_polygon(room["polygon"]).center_point
         room_name = room.get("room_name", "")

         rooms_labels_g.add(
            klass._get_centered_text(
               room_name, center.x, center.y, id_attr = "r_label_"+str(r_id)
            )
         )

      return rooms_labels_g

   @classmethod
   def _get_centered_text(klass, text, x, y, split_lines = True, id_attr = None, txttype = None, ):
      """
      Given a text string, x and y coordinates, returns an svg text object
      for that text while also centering horizontally.

      By defaul a text object is created, but it may also return other
      text types, like tspan for instance.
      """
      hor_char_offset = 5
      ver_line_offset = 18
      txttype = txttype or klass.svg.text

      if split_lines:
         # Espressione regolare che separa il testo in parole seguite da
         # congiunzioni o preposizioni
         tokens  = re.findall("(\w+(\s[a-zA-Z]{1,3}(\s|$))?)", text )
         phrases = [ r[0].strip() for r in tokens ] or [text]
      else:
         phrases = [text]

      # Centralizzazione verticale a seconda della quanità di righe
      y = y - (len(phrases) - 1)* (ver_line_offset / 2.4)
      first = txttype(
         phrases[0],
         (x - len(phrases[0]) * hor_char_offset, y),
         id = str(id_attr or "") or None
      )

      for i, phrase in enumerate(phrases[1:]):
         first.add(
            klass.svg.tspan(
               phrase,
               (x - len(phrase) * hor_char_offset, y + (i + 1) * ver_line_offset),
               id = str(id_attr or "") or None
            )
         )
      return first

   @classmethod
   def _get_all_rooms(klass, floor):
      """
      Returns a view of all the floor rooms, as a generator of tuples.
      The first element of the tuple is the room ID or None for unidentified
      rooms, while the second element is the room object itself.
      """
      unidentified_rooms   = floor.get("unidentified_rooms", [])
      unidentified_rooms   = (
         (None, room) for room in unidentified_rooms )
      rooms                = floor.get("rooms", {})
      room_items           = (
         (rid, room) for rid, room in rooms.items() if "polygon" in room
      )
      return chain(room_items, unidentified_rooms)

   @classmethod
   def _create_room_group(klass, r_id, r_name, cat_name, polygon):
      """
      Create an svg Group that contains room's elements: a polyline and a text.

      Arguments:
      - r_id: a string representing the room id;
      - room: a dictionary representing the room's informations.

      Returns:
      - an svg Group.
      """
      group       = svgwrite.container.Group(id = r_id)

      if polygon:
         points = klass._simplify_points(polygon)
         klass._draw_room(group, points, r_id)

      return group

   @classmethod
   def _prepare_cat_name(klass, cat_name):
      """
      Sanitizes a category_name and replaces special symbols/spaces with hyphens,
      so that it can be used as an svg id attributes. If cat_name is empty,
      the string "Sconosciuto" is returned.
      """
      if cat_name.strip():
         return re.sub("[^a-zA-Z]", "-", cat_name)

      return "Sconosciuto"


   @classmethod
   def _create_polygon(klass, poly):
      """
      Create a polygon from a room's polyline.

      Arguments:
      - poly: a dictionary representing the room's polygon informations.

      Returns:
      - a polygon object.
      """
      polygon  = Polygon.from_serializable(poly)
      polygon.absolutize()
      return polygon

   @classmethod
   def _draw_room(klass, group, points, r_id):
      """
      Add an svg polyline from a points list to a group.

      Arguments:
      - group: the svg Group we want update with the polyline;
      - points: a list representing the points of the polyline;

      Returns: None.
      """
      if r_id:
         poly  = klass.svg.polyline(
            (klass._approximate_coordinates(p[0], p[1]) for p in points),
            id = r_id,
            fill="rgb(255, 255, 255)"
         )
      else:
         poly  = klass.svg.polyline(
            (klass._approximate_coordinates(p[0], p[1]) for p in points),
            fill="rgb(255, 255, 255)"
         )
      group.add(poly)

   @classmethod
   def _simplify_points(klass, polygon, tol=2.0):
      """
      Applies Ramer–Douglas–Peucker algorithm to simplify a room polygon.
      """
      pts         = [ tuple(p) for p in polygon.points ]
      simplified  = rdp.rdp(pts, tol)

      return simplified

   @classmethod
   def _approximate_coordinates(klass, x, y):
      return ("{:.0f}".format(x), "{:.0f}".format(y))

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

