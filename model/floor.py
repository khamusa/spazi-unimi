import time
from . import Room

class Floor:

   def __init__(self, b_id, f_id = None, rooms = []):
      self.b_id            = b_id
      self.f_id            = f_id or ""
      self.rooms           = []
      self.min_x           = float("+inf")
      self.min_y           = float("+inf")
      self.n_rooms         = 0

      for r in rooms:
         self.add_room(r)

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

   def normalize(self, scale_amount=.4):
      self.transform(scale_amount=scale_amount, traslate_x = -self.min_x, traslate_y = -self.min_y)

   def to_serializable(self):
      return {
         "b_id"            : self.b_id,
         "f_id"            : self.f_id,
         "date"            : time.strftime("%m/%d/%Y"),
         "payload"         : {
                                 "n_rooms": len(self.rooms),
                                 "rooms"  : [ el.to_serializable() for el in self.rooms ]
                              }
      }

   def from_serializable(data):
      rooms = ( Room.from_serializable(r) for r in  data["payload"]["rooms"])
      return Floor( data["b_id"] , data["f_id"] , rooms  )
