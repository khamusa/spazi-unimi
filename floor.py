

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
      top_left    = room.top_left_most_point()
      self.min_x  = min(self.min_x, top_left.x)
      self.min_y  = min(self.min_y, top_left.y)
      self.rooms.append(room)

   def associate_room_texts(self, texts):
      """Given a list of texts, associates each one with a room belonging to the current floor"""
      for t in texts:
         for r in self.rooms:
            if r.containsText( t ):
               r.add_text(t)
               break

   def normalize(self, scale_amount=1):
      print("Traslated of", self.min_x, self.min_y)
      for r in self.rooms:
         # OCCHIO ALL'ORDINE!!! :D
         r.traslate(-self.min_x, -self.min_y)
         r.scale(scale_amount)

   def scale(self, amount):
      """Scales the floor and it's rooms :D """
      for r in self.rooms:
         r.scale(amount)

   def center_at_origin(self):
      """Traslates the floor rooms in order to place the top-leftmost corner of the rooms at the origin"""
      self.traslate(-self.min_x, -self.min_y)

   def traslate(self, amount_x, amount_y):
      """Traslates the floor rooms by the given amount"""
      for r in self.rooms:
         r.traslate(amount_x, amount_y)
