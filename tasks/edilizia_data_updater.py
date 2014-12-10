from utils.logger import Logger
import re
from model import Building

class EdiliziaDataUpdater:

   def perform_update(self, entities_type, content ):
      {
         "room_categories" : self.update_room_categories,
         "buildings"       : self.update_buildings,
         "rooms"           : self.update_rooms
      }[entities_type](content)


   def update_buildings(self, buildings):
      for b in buildings:
         b_id = b.get("b_id", "")
         if not self._is_valid_b_id(b_id):
            Logger.warning("Invalid building ID: \"{}\"".format(b_id))
            continue

         building = Building.find_or_create_by_id(b_id)
         building.attr( "edilizia", b )
         building.save()

   def _is_valid_b_id(self, b_id):
      return b_id and re.match("\d+", b_id)

   def update_room_categories(self, categories):
      pass

   def update_rooms(self,rooms):
      pass
