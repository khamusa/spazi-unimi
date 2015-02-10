import svgwrite, random
from .persistence_manager import PersistenceManager
from io import StringIO
import os

class SVGPersistenceDecorator(PersistenceManager):

   def __init__(self, config, persistence):
      self._cm        = config
      self._decorated = persistence

   def floor_write(self, floor):
      self.write_data(floor)
      self._decorated.floor_write(floor)

   def get_write_data(self, obj = None):
      svg = svgwrite.Drawing()
      for r in obj.rooms:
         color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
         points   = svg.polyline( ((p.x, p.y) for p in r.polygon.absolutized().points), fill=color, stroke="#666")

         svg.add(points)

         for t in r.texts:
            svg.add(svg.text(t.text, t.anchor_point))


      io = StringIO()
      svg.write(io)
      return io.getvalue()

   def get_base_write_path(self, obj = None):
      return os.path.join(
            self._cm["folders"]["data_svg_preprocessed_output"],
            obj.b_id
            )

   def get_filename_format(self, obj = None):
      return self._cm["filepaths"]["preprocessed_floor_format"].format(
         b_id           = obj.b_id,
         floor_name     = obj.floor_name
      )

   def get_file_extension(self, obj = None):
      return "svg"

