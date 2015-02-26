import dxfgrabber
import sys, os, re
import dxfgrabber.entities
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

      def is_valid_room(ent):
         """
         Method to validate a room entity.

         Arguments:
         - ent: an entity read from the dxf file.

         Returns: True or False.

         If ent is a valid polyline in the polylines layer returns True else
         returns False.
         """

         return type(ent) in [LWPolyline, Polyline] and ent.layer in self.valid_poly_layers

      def is_valid_text(ent):
         """
         Method to validate a text entity.

         Arguments:
         - ent: an entity read from the dxf file.

         Returns: True or False.

         If ent is a text in the text layers returns True else return False.
         """

         if type(ent) not in [MText, dxfgrabber.entities.Text]:
            return False

         if re.match("^\s*[a-zA-Z\d]*\d+[a-zA-Z\d]*\s*$", ent.plain_text()) is None:
            return False

         return ent.layer in self.valid_text_layers

      rooms = (
               Room(
                  Polygon.from_absolute_coordinates( [(p[0], -p[1]) for p in ent.points] )
               ) for ent in self._grabber.entities if is_valid_room(ent)
            )

      texts = (
               Text(
                  ent.plain_text().strip(), Point(ent.insert[0], -ent.insert[1])
               ) for ent in self._grabber.entities if is_valid_text(ent)
            )

      b_id = self._get_b_id(self._basename)

      if not b_id:
         raise FileUpdateException("It was not possible to identify the building associated to the DXF file")

      f_id = FloorInference.get_identifier(
                     self._basename,
                     self._grabber
                  )

      if not f_id:
         raise FileUpdateException("It was not possible to identify the floor associated to the DXF file")

      self.floor = Floor(b_id, f_id, rooms)
      if self.floor.n_rooms == 0:
         raise FileUpdateException("The floor read has no rooms: " + self._filename)
      self.floor.associate_room_texts(texts)
      self.floor.normalize(0.3)

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
