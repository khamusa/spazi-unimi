from dxf_reader import DxfReader
from config_manager import ConfigManager
from persistence_manager import PersistenceManager
import sys
import svgwrite
import re
import os
import random
import time

class Main():
   def __init__(self):
      self._config      = ConfigManager("config.json")
      self._persistence = PersistenceManager(self._config)

   def run_command(self, command, files):
      start_time = time.time()

      if len(files):
         for filename in files:
            getattr(self, "run_"+command)(filename)
      else:
         getattr(self, "run_"+command)()

      end_time = time.time() - start_time
      print("Total time     :", end_time , "seconds")

      if len(files):
         print("Arithmetic mean:", end_time / len(files), "seconds")


   def run_dxf(self, filename):
      rm = re.match("(\w+)_(\w+)\.dxf", os.path.basename(filename))
      if rm is None:
         raise RuntimeError("File name format error.")

      dx = DxfReader(filename, rm.group(1), rm.group(2))
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

   def run_csv(self, filename):
      print("CSV Not implemented yet.")

   def run_easy_rooms(self):
      print("Easy Rooms Not implemented yet.")

if __name__ == '__main__':
   import argparse

   parser = argparse.ArgumentParser(description = "Programma per l'aggiornamento dati del server Spazi Unimi.")

   # TODO: verificare che se viene scelto csv e dxf, files non sia lista vuota.
   # Similarmente se viene chiamato easy_rooms, files dev'essere vuoto
   parser.add_argument('command', metavar='op', type=str, choices=["csv", "dxf", "easy_rooms"],
                      help="Il commando da eseguire: dxf, csv, easy_rooms")

   parser.add_argument('files', metavar='file', type=str, nargs='*',
                      help='I file su cui lavorare, a seconda del comando scelto. Se il comando è easy_rooms, verrà trascurato.')

   args = parser.parse_args()

   program = Main()
   program.run_command(args.command, args.files)
