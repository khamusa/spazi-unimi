
from point import Point
class Floor:

   def __init__(self, building_name, floor_name = None, rooms = []):
      self.building_name   = building_name
      self.floor_name      = floor_name or ""
      self.rooms           = []
      self.min_x           = float("+inf")
      self.min_y           = float("+inf")

      for r in rooms:
         self.add_room(r)

   def add_room(self, room):
      """Adds a room to current floor object"""
      minX, minY   = room.offset_from_origin()
      self.min_x  = min(self.min_x, minX)
      self.min_y  = min(self.min_y, minY)
      self.rooms.append(room)

   def associate_room_texts(self, texts):
      """Given a list of texts, associates each one with a room belonging to the current floor"""
      for t in texts:
         for r in self.rooms:
            if r.containsText( t ):
               r.add_text(t)
               break

   def transform(self, scale_amount=1, traslate_x=0, traslate_y=0):
      for r in self.rooms:
         # L'ordine di queste operazioni di transformazione
         # è rilevante.
         r.traslate(traslate_x, traslate_y)
         r.scale(scale_amount)

   def normalize(self):
      self.transform(scale_amount = .4, traslate_x = -self.min_x, traslate_y = -self.min_y)
