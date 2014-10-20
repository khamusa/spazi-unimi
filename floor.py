

class Floor:

   def __init__(self, building_name, floor_name):
      self.building_name   = building_name
      self.floor_name      = floor_name
      self.rooms           = []

   def add_room(self, room):
      self.rooms.append(room)
