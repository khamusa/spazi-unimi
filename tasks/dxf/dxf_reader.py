import dxfgrabber
import sys, os, re
import dxfgrabber.entities
from itertools             import chain
from model                 import Room
from model                 import Floor
from model.drawable        import Text
from model.drawable        import Point
from model.drawable        import Polygon
from dxfgrabber.entities   import LWPolyline, Polyline, MText
from tasks.floor_inference import FloorInference
from utils.logger          import Logger
from tasks.task            import FileUpdateException

class DxfReader():
   """
      Class to read the dxf file with the dxfgrabber.
   """

   # Todo: extract to external config file
   valid_poly_layers = ["RM$"]
   valid_text_layers = ["NLOCALI", "RM$TXT"]

   def __init__(self, filename):
      """
      Try reading a dxf file pointed by filename and save the floor in the
      respective attribute.

      Arguments:
      - filename: string rapresents the filename with path of the dxf file.

      Raise:
      - FileUpdateException in case of impossibility to identify building, floor
      or rooms.

      Initialise a DxfReader, try to read a dxf file and associate the texts
      found to the respective room. Call the FloorInference class to find a
      standard floor id, and save the results of the operations in the floor
      attribute as a Floor object.
      """

      self._filename = filename;
      self._basename = os.path.basename(filename)
      self.floor = None

      self._read_dxf(self._filename)
      self._extract_entities()


      b_id = self._get_b_id(self._basename)

      if not b_id:
         raise FileUpdateException("It was not possible to identify the building associated to the DXF file")

      f_id = FloorInference.get_identifier(
                     self._basename,
                     self._grabber
                  )

      if not f_id:
         raise FileUpdateException("It was not possible to identify the floor associated to the DXF file")

      self.floor = Floor(b_id, f_id, self._rooms, self._wall_polygons)
      if self.floor.n_rooms == 0:
         raise FileUpdateException("The floor read has no rooms: " + self._filename)
      self.floor.associate_room_texts(self._texts)
      self.floor.normalize(0.3)

   def _extract_entities(self):
      self._rooms = []
      self._texts = []
      wall_lines  = []

      for ent in self._grabber.entities:
         if self._is_valid_room(ent):
            self._rooms.append(
               Room(
                  Polygon.from_absolute_coordinates( [(p[0], -p[1]) for p in ent.points] )
               )
            )
         elif self._is_valid_text(ent):
            self._texts.append(
               Text(
                  ent.plain_text().strip(), Point(ent.insert[0], -ent.insert[1])
               )
            )
         elif self._is_valid_wall_line(ent):
            start          = Point(ent.start[0], -ent.start[1])
            end            = Point(ent.end[0], -ent.end[1])
            line           = (start, end)
            start._line    = line
            end._line      = line
            start._line_pos   = "start"
            end._line_pos     = "end"

            wall_lines.append( line )

      self._wall_polygons = self._process_wall_lines(wall_lines)

   def _process_wall_lines(self, lines):
      all_points = [ (l[0], l[1]) for l in lines ]
      all_points = sorted(chain(*all_points), key=lambda p: (p.x, p.y))

      for i, p1 in enumerate(all_points):

         for p2 in all_points[i+1:]:
            if abs(p1.x - p2.x) > 1:
               break

            if (p1._line is p2._line):
               continue

            if getattr(p2, "_matched", None):
               continue

            if abs(p1.y - p2.y) < 1:
               p1._matched = p2
               p2._matched = p1

      return self._group_wall_lines(lines)

   def _group_wall_lines(self, lines):
      polygons   = []
      matched_points       = set()

      for l in lines:
         if l[0] in matched_points or l[1] in matched_points:
            continue

         path_1 = []
         self._explore(l, path_1, matched_points)
         path_2 = []
         self._explore(l, path_2, matched_points)

         if(path_2):
            pass
            #print("Path not closed found")

         points = list(chain(reversed(path_2), path_1))
         if len(points) >= 3:
            points.append(points[0])
            # TODO: restituire questo valore in qualche modo al floor, che deve
            # normalizzarlo !
            polygons.append(Polygon.from_absolute_coordinates(points))

      return polygons

   def _explore(self, line, path, matched_points):
      next_point = getattr(line[1], "_matched", None)
      prev_point = getattr(line[0], "_matched", None)

      point_found = (
         next_point not in matched_points and next_point or
         prev_point not in matched_points and prev_point
         )

      if point_found:
         matched_points.add(point_found)
         path.append(point_found)
         self._explore(point_found._line, path, matched_points)


   def _is_valid_room(self, ent):
      """
      Method to validate a room entity.

      Arguments:
      - ent: an entity read from the dxf file.

      Returns: True or False.

      If ent is a valid polyline in the polylines layer returns True else
      returns False.
      """

      return type(ent) in [LWPolyline, Polyline] and ent.layer in self.valid_poly_layers

   def _is_valid_text(self, ent):
      """
      Method to validate a text entity.

      Arguments:
      - ent: an entity read from the dxf file.

      Returns: True or False.

      If ent is a text in the text layers returns True else return False.
      """

      if type(ent) not in [MText, dxfgrabber.entities.Text]:
         return False

      if ent.layer not in self.valid_text_layers:
         return False

      txt = ent.plain_text().strip()
      m1  = re.match("^[a-zA-Z\d]*\d+[a-zA-Z\d]*$", txt)
      m2  = re.match("^([a-zA-Z]{2,}\s*)+$", txt)

      if not(m1 or m2):
         return False

      return True

   def _is_valid_wall_line(self, ent):
      return ent.layer == "MURI" and type(ent) is dxfgrabber.entities.Line

   def _get_b_id(self, basename):
      """
      Method to extract the building id from the filename.

      Arguments:
      - basename: a string representing the name of the dxf file.

      Returns: a string.
      """

      b_id  = None
      rm    = re.match("(\d+)_([a-zA-Z0-9]+).*\.dxf", basename, re.I)

      if rm:
         b_id = rm.group(1)
      else:
         rm = re.match("(\d+)\.dxf", basename, re.I)
         if rm:
            b_id = rm.group(1)

      return b_id

   def _read_dxf(self, filename):
      """
         Read the dxf file with the dxf grabber.

         Arguments:
         - filename: representing the path and the name  of the dxf file.

         Returns: None.

         Raise: PermissionError, IsADirectoryError, FileNotFoundError or generic
         Exception in case of reading failure.

         Try to read the dxf file with the grabber.
      """

      try:
         self._grabber = dxfgrabber.readfile(filename)
      except PermissionError:
         Logger.error("Permission error: cannot read file " + filename)
         raise
      except IsADirectoryError:
         Logger.error("File is a directory error: cannot read file " + filename)
         raise
      except FileNotFoundError:
         Logger.error("File not found error: cannot read file " + filename)
         raise
      except Exception as e:
         Logger.error("Unknown exception on DXF file reading: " + str(e))
         raise
