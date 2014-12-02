"""
   TODO: SBAGLIATO! CORREGGERE QUESTO COMMENTO! xD
   Stampa in stdout informazioni estratte da file dxf
   Funziona con Python3, necessario installare dxfgrabber
   Per eseguire, spostarsi nella cartella python del repo e eseguire
      python3 dxf_info.py path_to_file

"""

import dxfgrabber
import sys
from model import Room
from model import Floor
from model.drawable import Text
from model.drawable import Point
from model.drawable import Polygon
from dxfgrabber.entities import LWPolyline, Polyline, MText
import dxfgrabber.entities
from utils.logger import Logger

class DxfReader():
   # Todo: extract to external config file
   valid_poly_layers = ["RM$"]
   valid_text_layers = ["NLOCALI", "RM$TXT"]

   def __init__(self, filename, building_name, floor_name):
      self._filename = filename;
      self._read_dxf(self._filename)

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

      self.floor = Floor(building_name, floor_name, rooms)
      if self.floor.n_rooms == 0:
         Logger.error("The floor read has no rooms: " + self._filename)
         raise RuntimeError("Floor read has no rooms")
      self.floor.associate_room_texts(texts)
      self.floor.normalize(0.3)


   def _read_dxf(self, filename):
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

