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

         building = self.find_building_to_update(b)
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

         for ((b_id, f_id), floor_rooms) in rooms:
            if not(f_id and f_id.strip()):
               Logger.warning("Empty floor id in building: \"{}\". \"{}\" rooms discarded".format(b_id, len(list(floor_rooms))))
               continue

            # remove the attribute b_id from the rooms
            floor_rooms = map(self.sanitize_room, floor_rooms)

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
                  "f_id"   : self.sanitize_floor_id(f_id),
                  "rooms"  : list(floor_rooms)
               } )

         building and building.save()


   def sanitize_room(self, room):
      """Effettua una pulizia delle stanze prima di salvarle

      Di default rimuove la chiave b_id ridondante nel DB.
      Le sottoclassi devono assicurarsi di richiamare questa implementazione
      attraverso l'uso di super e di restituire un riferimento all'oggetto aggiornato"""

      # remove the attribute b_id from the room
      del room["b_id"]
      return room


   def sanitize_floor_id(self, floor_id):
      """Effettua una pulizia del floor_id prima di salvarlo

      Le sottoclassi devono assicurarsi di richiamare questa implementazione
      attraverso l'uso di super e di restituire un riferimento all'oggetto aggiornato"""
      return floor_id


   def find_building_to_update(self, building):
      b_id = building.get("b_id", "")

      return Building.find_or_create_by_id(b_id)
