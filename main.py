from dxf_reader import DxfReader
from config_manager import ConfigManager
from persistence_manager import PersistenceManager
import sys
import svgwrite
import re
import os

class Main():
   def __init__(self, fname):
      self.fname = fname
      self._config = ConfigManager("config.json")
      self._persistence = PersistenceManager(self._config)

   def run(self):
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
   if len(sys.argv) > 1:
      fname = sys.argv[1]

      import time
      import random
      time_s = time.time()

      program = Main(fname)
      program.run()

      print("Total time", time.time() - time_s, "seconds")

   else:
      raise RuntimeError("Argument error: no file name.")
