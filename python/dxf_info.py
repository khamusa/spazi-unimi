"""
   Stampa in stdout informazioni estratte da file dxf
   Funziona con Python3, necessario installare dxfgrabber
   Per eseguire, spostarsi nella cartella python del repo e eseguire
      python3 dxf_info.py path_to_file

"""

import dxfgrabber
import sys


fname = (len(sys.argv) > 1) and sys.argv[1] or "../src/stanza_singola.DXF" 
print("Looking for file {}".format(fname))

dxf = dxfgrabber.readfile(fname)
print("DXF version: {}".format(dxf.dxfversion))
header_var_count = len(dxf.header) # dict of dxf header vars
layer_count = len(dxf.layers) # collection of layer definitions
print("\n\n Ho trovato {} layers:".format(layer_count))
for lay in dxf.layers:
   print("  {}".format(lay.name))

entitiy_count = len(dxf.entities) # list like collection of entities
print("\n\n Ho trovato {} entita':".format(entitiy_count))


def sanitize_polypoints(polypoints):
   return [(int(newx), int(newy)) for newx, newy in polypoints]

def sanitize_coords(coords):
   (x, y, z) = coords
   return (int(x), int(y), int(z))

for entity in dxf.entities:
      """ MText sono multiline texts, mentre Text sono testi normali """
      if type(entity) != dxfgrabber.entities.LWPolyline:
         print("  - Testo: '{}'".format(entity.plain_text()))
         print("     coords: {}".format(sanitize_coords(entity.insert)))
      else:
         print("  - Polyline: ")
         print("     Points: {}".format(sanitize_polypoints(entity.points)))
      print("     Layer: {}".format(entity.layer))
