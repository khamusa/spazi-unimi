from utils.logger import Logger

class EdiliziaDataUpdater(QualchePadre):

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

         persisted = Building.find_or_create_building(b_id, { "edilizia" : b })
         persisted.save()

   def _is_valid_b_id(self, b_id):
      return b_id and re.match("\d+", b_id)

   def update_room_categories(self, categories):
      pass

   def update_rooms(self,rooms):
      pass
