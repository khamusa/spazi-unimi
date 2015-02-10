from model              import Building
from utils.logger       import Logger
from tasks.data_merger  import DataMerger
import itertools

class DataUpdater():

   def update_buildings(self, buildings):
      namespace = self.get_namespace()
      for b in buildings:
         b_id = b.get("b_id", "")
         if not self._is_valid_b_id(b_id):
            Logger.warning("Invalid building ID: \"{}\"".format(b_id))
            continue

         building = Building.find_or_create_by_id(b_id)
         namespaced_attr = building.attr(namespace) or {}
         namespaced_attr.update(b)
         building.attr(namespace, namespaced_attr )

         edilizia = building.attr('edilizia')
         easyroom = building.attr('easyroom')

         building.attr('merged', DataMerger.merge_building(edilizia, easyroom))
         building.save()

   def update_rooms(self,rooms):
         namespace = self.get_namespace()
         floor_key = self.get_floor_key()

         # ordiniamo le stanze per edificio e per piano in modo da velocizzare l'algoritmo
         keyfunc = lambda s: (s["b_id"], s[floor_key])
         rooms.sort(key = keyfunc)
         rooms = itertools.groupby(rooms, key = keyfunc)
         building = None

         # remove the attribute b_id from the room
         def remove_b_id(room):
            del room["b_id"]
            return room


         for ((b_id, floor), floor_rooms) in rooms:

            # remove the attribute b_id from the rooms
            floor_rooms = map(remove_b_id, floor_rooms)

            if not self._is_valid_b_id(b_id):
               Logger.warning("Invalid building ID: \"{}\"".format(b_id))
               continue

            if not building or building.attr("b_id") != b_id:
               building and building.save()
               building = Building.find_or_create_by_id(b_id)
               namespaced_attr = building.attr(namespace) or {}
               namespaced_attr["floors"] = []
               building.attr(namespace, namespaced_attr)

            namespaced_attr["floors"].append( {
                  "f_id"   : floor,
                  "rooms"  : list(floor_rooms)
               } )

         building and building.save()
