import re
from model           import RoomCategory
from .data_updater   import DataUpdater

class EdiliziaDataUpdater(DataUpdater):

   def perform_update(self, entities_type, content ):
      {
         "room_categories" : self.update_room_categories,
         "buildings"       : self.update_buildings,
         "rooms"           : self.update_rooms
      }[entities_type](content)

   def get_namespace(self):
      """Hook method used by parent DataUpdater class"""
      return "edilizia"

   def _is_valid_b_id(self, b_id):
      """Hook method used by parent DataUpdater class"""
      return b_id and re.match("\d+", b_id)

   def get_floor_key(self):
      """Hook method used by parent DataUpdater class"""
      return "l_floor"

   def update_room_categories(self, categories):
      RoomCategory.clean()
      for c in categories:
         cat = RoomCategory(c)
         cat.save()
