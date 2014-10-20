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
from point import Point
from dxfgrabber.entities import LWPolyline, Polyline, MText, Text

class DxfReader():
   # Todo: extract to external config file
   valid_poly_layers = ["RM$"]
   valid_text_layers = ["NLOCALI", "RM$TXT"]

   def __init__(self, filename):
      self._filename = filename;
      self._grabber = dxfgrabber.readfile(self._filename)

      self.rooms = [
            Room(ent.points).reflected_y() for ent in self._grabber.entities \
            if type(ent) in [LWPolyline, Polyline] and ent.layer in self.valid_poly_layers]

      # TODO: Controllare se ci sono casi di Mtext che restituiscano una lista
      # di testi alla chiamata di plain_text()
      texts = (RoomText(ent.plain_text(), Point(ent.insert) ).reflected_y()  \
            for ent in self._grabber.entities if type(ent) in [MText, Text] and ent.layer in self.valid_text_layers
            )

      for t in texts:
           for r in self.rooms:
                if r.containsText( t ):
                     r.addText(t)
                     break


if __name__ == '__main__':
   fname = (len(sys.argv) > 1) and sys.argv[1] or "assets/dxf/stanza_singola.dxf"

   import time
   import random
   time_s = time.time()
   dx = DxfReader(fname)

   minimum_x = float('+inf')
   minimum_y = float('+inf')
   for r in dx.rooms:
      r.scale(.4)
      minimum_x = min(minimum_x, r.top_left_most_point().x)
      minimum_y = min(minimum_y, r.top_left_most_point().y)

   svg = svgwrite.Drawing()

   for r in dx.rooms:
      r.traslate(-minimum_x, -minimum_y)

      color = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
      points   = svg.polyline( ( (p.x, p.y) for p in r.points ), fill=color,stroke="#666")

      svg.add(points)

      for t in r.texts:
         svg.add(svg.text(t.text, t.anchor_point))

   svg.filename = "assets/test.svg"
   svg.save()

   print("Total time", time.time() - time_s, "seconds")

