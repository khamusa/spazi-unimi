"""
   Stampa in stdout informazioni estratte da file dxf
   Funziona con Python3, necessario installare dxfgrabber
   Per eseguire, spostarsi nella cartella python del repo e eseguire
      python3 dxf_info.py path_to_file

"""

import dxfgrabber
import sys
from dxfgrabber.entities import *

class DxfGrabberExtractor():
   # Todo: extract to external config file
   valid_poly_layers = ["RM$"]
   valid_text_layers = ["NLOCALI", "RM$TXT"]

   def __init__(self, filename):
      self._filename = filename;
      self._grabber = dxfgrabber.readfile(self._filename)

      self.rooms = [
            ent for ent in self._grabber.entities \
            if type(ent) in [LWPolyline, Polyline] and ent.is_closed and ent.layer in self.valid_poly_layers
            ]

      self.texts = (ent for ent in self._grabber.entities if type(ent) in [MText, Text])

   def get_info(self):
      """Displays comprehensive information about the dxf file being processed."""

      # General information
      # DXF file version
      header = "Dxf version: {version}\n\nCe ne sono {entity_count} entita' su {layer_count} layers.".\
            format(  version=self._grabber.dxfversion, 
                     entity_count=len(self._grabber.entities), 
                     layer_count=len(self._grabber.layers)
                  )

      # List the layers found on file
      layers = "\n\n"
      for lay in self._grabber.layers:
         layers = layers + "\n  {}".format(lay.name)      

      def sanitize_coords(coords):
         (x, y, z) = coords
         return (int(x), int(y), int(z))

      entities = "\n\n  - Polylines:\n"
      for entity in self._polys:        
         entities = entities + "     Points: {}\n".format(DxfGrabberExtractor.sanitize_polypoints(entity.points))
         entities = entities + "      Layer: {}\n".format(entity.layer)
        

      entities = entities + "\n\n  - Texts:\n"
      for entity in self.texts:   
         entities = entities + "     Testo: '{}'\n".format(entity.plain_text())
         entities = entities + "      coords: {}\n".format(sanitize_coords(entity.insert))
         entities = entities + "      Layer: {}\n".format(entity.layer)


      return header + layers + entities
            


fname = (len(sys.argv) > 1) and sys.argv[1] or "../src/stanza_singola.DXF" 

dx = DxfGrabberExtractor(fname)
print(dx.get_info())
dx.try_svg()

   
