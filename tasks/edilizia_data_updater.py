from utils.logger import Logger
import re, itertools
from model        import Building, RoomCategory
from operator     import attrgetter

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
         edilizia = building.attr("edilizia") or {}
         edilizia.update(b)
         building.attr("edilizia", edilizia )
         building.save()

   def _is_valid_b_id(self, b_id):
      return b_id and re.match("\d+", b_id)

   def update_room_categories(self, categories):
      RoomCategory.clean()
      for c in categories:
         cat = RoomCategory(c)
         cat.save()

   def update_rooms(self,rooms):
      keyfunc = lambda s: (s["b_id"], s["l_floor"])
      rooms.sort(key = keyfunc)
      rooms = itertools.groupby(rooms, key = keyfunc)
      building = None

      for ((b_id, floor), floor_rooms) in rooms:
         if not building or building.attr("b_id") != b_id:
            building and building.save()
            building = Building.find_or_create_by_id(b_id)
            edilizia = building.attr("edilizia") or {}
            edilizia["floors"] = []
            building.attr("edilizia", edilizia)

         edilizia["floors"].append( {
               "f_id"   : floor,
               "rooms"  : list(floor_rooms)
            } )

      building and building.save()
