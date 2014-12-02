"""
   TODO: SBAGLIATO! CORREGGERE QUESTO COMMENTO! xD
   Stampa in stdout informazioni estratte da file dxf
   Funziona con Python3, necessario installare dxfgrabber
   Per eseguire, spostarsi nella cartella python del repo e eseguire
      python3 dxf_info.py path_to_file

"""

import dxfgrabber
import sys, os
from model import Room
from model import Floor
from model.drawable import Text
from model.drawable import Point
from model.drawable import Polygon
from dxfgrabber.entities import LWPolyline, Polyline, MText
import dxfgrabber.entities

class DxfReader():
   # Todo: extract to external config file
   valid_poly_layers = ["RM$"]
   valid_text_layers = ["NLOCALI", "RM$TXT"]

   def __init__(self, filename):
      self._filename = filename;
      self._basename = os.path.basename(filename)
      self._grabber = dxfgrabber.readfile(self._filename)


      def is_valid_room(ent):
         return type(ent) in [LWPolyline, Polyline] and ent.layer in self.valid_poly_layers

      def is_valid_text(ent):
         return type(ent) in [MText, dxfgrabber.entities.Text] and ent.layer in self.valid_text_layers

      rooms = (
               Room(
                  Polygon.from_absolute_coordinates( [(p[0], -p[1]) for p in ent.points] )
               ) for ent in self._grabber.entities if is_valid_room(ent)
            )

      texts = (
               Text(
                  ent.plain_text(), Point(ent.insert[0], -ent.insert[1])
               ) for ent in self._grabber.entities if is_valid_text(ent)
            )

      floor_name = FloorInference.get_identifier(
                     self._basename,
                     self._grabber
                  )

      if not floor_name:
         Logger.error("It was not possible to identify the floor associated to the DXF file")
         return None

      building_name = self._get_building_name(self._basename)

      if not building_name:
         Logger.error("It was not possible to identify the building associated to the DXF file")
         return None

      self.floor = Floor(building_name, floor_name, rooms)
      self.floor.associate_room_texts(texts)
      self.floor.normalize(0.3)

      return self.floor

   def _get_building_name(self, basename):
      building_name = None
      rm = re.match("(\w+)_(\w+)\.dxf", basename, re.I)

      if rm:
         building_name = rm.group(1)
      else:
         rm = re.match("(.+)\.dxf", basename, re.I)
         if rm:
            building_name = rm.group(1)

      return building_name

