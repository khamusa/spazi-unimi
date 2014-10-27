"""
   Stampa in stdout informazioni estratte da file dxf
   Funziona con Python3, necessario installare dxfgrabber
   Per eseguire, spostarsi nella cartella python del repo e eseguire
      python3 dxf_info.py path_to_file

"""

import dxfgrabber
import sys
from room import Room
from room_text import RoomText
from floor import Floor
from point import Point
from dxfgrabber.entities import LWPolyline, Polyline, MText, Text

class DxfReader():
   # Todo: extract to external config file
   valid_poly_layers = ["RM$"]
   valid_text_layers = ["NLOCALI", "RM$TXT"]

   def __init__(self, filename):
      self._filename = filename;
      self._grabber = dxfgrabber.readfile(self._filename)

      def is_valid_room(ent):
         return type(ent) in [LWPolyline, Polyline] and ent.layer in self.valid_poly_layers

      def is_valid_text(ent):
         return type(ent) in [MText, Text] and ent.layer in self.valid_text_layers

      rooms = (
            Room( (p[0], -p[1]) for p in ent.points ) for ent in self._grabber.entities \
            if is_valid_room(ent)
            )

      texts = (
            RoomText(ent.plain_text(), Point(ent.insert[0], -ent.insert[1]) ) \
            for ent in self._grabber.entities
            if is_valid_text(ent)
            )

      self.floor = Floor(filename, rooms = rooms)
      self.floor.associate_room_texts(texts)
      self.floor.normalize(0.3)
