"""
   Stampa in stdout informazioni estratte da file dxf
   Funziona con Python3, necessario installare dxfgrabber
   Per eseguire, spostarsi nella cartella python del repo e eseguire
      python3 dxf_info.py path_to_file

"""

import dxfgrabber
import sys
import svgwrite
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
            Room(ent.points).reflected_y() for ent in self._grabber.entities \
            if is_valid_room(ent)
            )

      texts = (
            RoomText(ent.plain_text(), Point(ent.insert[0], -ent.insert[1]) ) \
            for ent in self._grabber.entities
            if is_valid_text(ent)
            )

      self.floor = Floor(filename, rooms = rooms)
      self.floor.associate_room_texts(texts)
      self.floor.normalize()

if __name__ == '__main__':
   fname = (len(sys.argv) > 1) and sys.argv[1] or "assets/dxf/stanza_singola.dxf"

   import time
   import random
   time_s = time.time()

   dx = DxfReader(fname)
   svg = svgwrite.Drawing()

   for r in dx.floor.rooms:
      color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
      points   = svg.polyline( ( (p.x, p.y) for p in r.points ), fill=color, stroke="#666")

      svg.add(points)

      for t in r.texts:
         svg.add(svg.text(t.text, t.anchor_point))

   svg.filename = "assets/test.svg"
   svg.save()

   print("Total time", time.time() - time_s, "seconds")

