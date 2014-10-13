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
            Room(ent.points) for ent in self._grabber.entities \
            if type(ent) in [LWPolyline, Polyline] and ent.is_closed and ent.layer in self.valid_poly_layers
            
      # TODO: Controllare se ci sono casi di Mtext che restituiscano una lista
      # di testi alla chiamata di plain_text()
      self.texts = (RoomText(ent.plain_text(), Point(ent.insert) )            \
            for ent in self._grabber.entities if type(ent) in [MText, Text]
            )



if __name__ == '__main__':
   fname = (len(sys.argv) > 1) and sys.argv[1] or "assets/stanza_singola.DXF" 
   dx = DxfReader(fname)
   print(dx.rooms)
   print(list(dx.texts))

   
