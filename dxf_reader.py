"""
   Stampa in stdout informazioni estratte da file dxf
   Funziona con Python3, necessario installare dxfgrabber
   Per eseguire, spostarsi nella cartella python del repo e eseguire
      python3 dxf_info.py path_to_file

"""

import dxfgrabber
import sys
from model.drawable import DrawableRoom
from model.drawable import DrawableText
from model.drawable import DrawableFloor
from model.drawable import DrawablePoint
from dxfgrabber.entities import LWPolyline, Polyline, MText, Text

class DxfReader():
   # Todo: extract to external config file
   valid_poly_layers = ["RM$"]
   valid_text_layers = ["NLOCALI", "RM$TXT"]

   def __init__(self, filename, building_name, floor_name):
      self._filename = filename;
      self._grabber = dxfgrabber.readfile(self._filename)

      def is_valid_room(ent):
         return type(ent) in [LWPolyline, Polyline] and ent.layer in self.valid_poly_layers

      def is_valid_text(ent):
         return type(ent) in [MText, Text] and ent.layer in self.valid_text_layers

      rooms = (
            DrawableRoom( (p[0], -p[1]) for p in ent.points ) for ent in self._grabber.entities \
            if is_valid_room(ent)
            )

      texts = (
            DrawableText(ent.plain_text(), DrawablePoint(ent.insert[0], -ent.insert[1]) ) \
            for ent in self._grabber.entities
            if is_valid_text(ent)
            )

      self.floor = DrawableFloor(building_name, floor_name, rooms)
      self.floor.associate_room_texts(texts)
      self.floor.normalize(0.3)
