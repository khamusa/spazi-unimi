import time
from .            import Room
from .drawable    import Polygon
from itertools    import chain

class Floor:

   def __init__(self, b_id, f_id = None, rooms = None, wall_lines = None, window_lines = None):
      self.b_id            = b_id
      self.f_id            = f_id or ""
      self.rooms           = []
      self.min_x           = float("+inf")
      self.min_y           = float("+inf")
      self.max_x           = float("-inf")
      self.max_y           = float("-inf")
      self.max_output_size = 1024
      self.n_rooms         = 0
      self.walls           = []
      self.windows         = []

      if rooms:
         for r in rooms:
            self.add_room(r)

      if wall_lines:
         for l in wall_lines:
            line = self.control_line(l)
            self.walls.append(line)

      if window_lines:
         for l in window_lines:
            line = self.control_line(l)
            self.windows.append(line)

   def __eq__(self,other):
      return (
         self.rooms == other.rooms and
         self.b_id == other.b_id and
         self.f_id == other.f_id
      )


   def add_room(self, room):
      """Adds a room to current floor object"""
      minX, minY  = room.min_absolute_point()
      self.min_x  = min(self.min_x, minX)
      self.min_y  = min(self.min_y, minY)

      maxX, maxY  = room.max_absolute_point()
      self.max_x  = max(self.max_x, maxX)
      self.max_y  = max(self.max_y, maxY)

      self.rooms.append(room)
      self.n_rooms = self.n_rooms + 1

   def control_line(self, line):
      self.min_x  = min(self.min_x, line[0].x)
      self.min_y  = min(self.min_y, line[0].y)
      self.min_x  = min(self.min_x, line[1].x)
      self.min_y  = min(self.min_y, line[1].y)

      self.max_x  = max(self.max_x, line[0].x)
      self.max_y  = max(self.max_y, line[0].y)
      self.max_x  = max(self.max_x, line[1].x)
      self.max_y  = max(self.max_y, line[1].y)
      return line

   def associate_room_texts(self, texts):
      """Given a list of texts, associates each one with a room belonging to the current floor"""
      for t in texts:
         for r in self.rooms:
            if r.contains_text( t ):
               r.add_text(t)
               break

   def transform(self, scale_amount=1, traslate_x=0, traslate_y=0):
      for r in self.rooms:
         # L'ordine di queste operazioni di transformazione
         # è rilevante.
         r.traslate(traslate_x, traslate_y)
         r.scale(scale_amount)

      for start, end in chain(self.walls, self.windows):
         start.traslate(traslate_x, traslate_y)
         start.scale(scale_amount)
         end.traslate(traslate_x, traslate_y)
         end.scale(scale_amount)

   def calculate_scale_amount(self):
      scale_amount_x = self.max_output_size / abs(self.max_x - self.min_x)
      scale_amount_y = self.max_output_size / abs(self.max_y - self.min_y)
      return min(scale_amount_x, scale_amount_y)

   def normalize(self):
      scale_amount = self.calculate_scale_amount()
      self.transform(scale_amount=scale_amount, traslate_x = -self.min_x, traslate_y = -self.min_y)

   def to_serializable(self):
      return {
         "b_id"      : self.b_id,
         "f_id"      : self.f_id,
         "rooms"     : [ el.to_serializable() for el in self.rooms ],
         "walls"     : [
                           (start.to_serializable(), end.to_serializable())
                           for start, end in self.walls
                        ],
         "windows"   : [
                           (start.to_serializable(), end.to_serializable())
                           for start, end in self.windows
                        ]
      }

   def from_serializable(data):
      rooms = ( Room.from_serializable(r) for r in  data["rooms"] )
      walls = (
         (Point.from_serializable(start), Point.from_serializable(end))
         for start, end in data.get("walls", [])
         )
      windows = (
         (Point.from_serializable(start), Point.from_serializable(end))
         for start, end in data.get("windows", [])
         )

      return Floor( data["b_id"] , data["f_id"] , rooms, walls, windows )
