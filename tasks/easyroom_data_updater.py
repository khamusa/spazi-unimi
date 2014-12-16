from utils.logger import Logger
import re, itertools
from model import Building

class EasyroomDataUpdater:

   def perform_update(self, entities_type, content ):
      {
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
         easyroom = building.attr("easyroom") or {}
         easyroom.update(b)
         building.attr("easyroom", easyroom )
         building.save()

   def _is_valid_b_id(self, b_id):
      return b_id and re.match("\d\d\d\d\d", b_id)

   def update_rooms(self,rooms):
      keyfunc = lambda s: (s["b_id"], s["floor"])
      rooms.sort(key = keyfunc)
      rooms = itertools.groupby(rooms, key = keyfunc)
      building = None

      for ((b_id, floor), floor_rooms) in rooms:
         if not building or building.attr("b_id") != b_id:
            building and building.save()
            building = Building.find_or_create_by_id(b_id)
            easyroom = building.attr("easyroom") or {}
            easyroom["floors"] = []
            building.attr("easyroom", easyroom)

         easyroom["floors"].append( {
               "f_id"   : floor,
               "rooms"  : list(floor_rooms)
            } )

      building and building.save()
