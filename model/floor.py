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
      self.n_rooms         = 0
      self.walls           = []
      self.windows         = []

      if rooms:
         for r in rooms:
            self.add_room(r)

      if wall_lines:
         for l in wall_lines:
            line = self.add_line(l)
            self.walls.append(line)

      if window_lines:
         for l in window_lines:
            line = self.add_line(l)
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
      self.rooms.append(room)
      self.n_rooms = self.n_rooms + 1

   def add_line(self, line):
      self.min_x  = min(self.min_x, line[0].x)
      self.min_y  = min(self.min_y, line[0].y)
      self.min_x  = min(self.min_x, line[1].x)
      self.min_y  = min(self.min_y, line[1].y)
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

   def normalize(self, scale_amount=.4):
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
