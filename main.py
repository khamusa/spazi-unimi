from dxf_reader import DxfReader
from config_manager import ConfigManager
from persistence_manager import PersistenceManager
import sys
import svgwrite
import re
import os
import random

class Main():
   def __init__(self, fname):
      self.fname = fname
      self._config = ConfigManager("config.json")
      self._persistence = PersistenceManager(self._config)

   def run_dxf(self):
      rm = re.match("(\w+)_(\w+)\.dxf", os.path.basename(self.fname))
      if rm is None:
         raise RuntimeError("File name format error.")

      dx = DxfReader(self.fname, rm.group(1), rm.group(2))
      svg = svgwrite.Drawing()

      for r in dx.floor.rooms:
         color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
         points   = svg.polyline( ( (p.x, p.y) for p in r.points ), fill=color, stroke="#666")

         svg.add(points)

         for t in r.texts:
            svg.add(svg.text(t.text, t.anchor_point))

      svg.filename = "assets/test.svg"
      svg.save()

      self._persistence.floor_write(dx.floor)


if __name__ == '__main__':
   import argparse

   parser = argparse.ArgumentParser(description = "Programma per l'aggiornamento dati del server Spazi Unimi.")

   parser.add_argument('command', metavar='op', type=str, choices=["csv", "dxf", "easy_rooms"],
                      help="Il commando da eseguire: dxf, csv, easy_rooms")

   parser.add_argument('files', metavar='file', type=str, nargs='*',
                      help='I file su cui lavorare, a seconda del comando scelto. Se il comando è easy_rooms, verrà trascurato.')

   args = parser.parse_args()



   def update_dxf(args):
      import time

      start_time = time.time()

      for fname in args.files:
         program = Main(fname)
         program.run_dxf()

      end_time = time.time() - start_time
      print("Total time     :", end_time , "seconds")
      print("Arithmetic mean:", end_time / len(args.files), "seconds")


   ops = {
      "dxf": update_dxf,
      "csv": print,
      "easy_rooms": print
   }

   ops[args.command](args)

