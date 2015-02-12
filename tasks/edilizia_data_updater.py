import re
from model              import RoomCategory
from .data_updater      import DataUpdater
from .floor_inference   import FloorInference
from model.building     import Building

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

   def sanitize_floor_id(self, l_floor):
      f_id = FloorInference.fid_from_string(l_floor, "suffix_regex")
      return super().sanitize_floor_id(f_id)

   def find_building_to_update(self, new_b):
      b_id     = new_b["b_id"]
      building = Building.find_or_create_by_id(b_id)

      # controllo di avere una mappatura tra b_id e l_b_id
      if not building.has_attr("merged") or building.attr("merged")["l_b_id"] is "":
         l_b_id   = new_b["l_b_id"]

         if not self._is_valid_b_id(l_b_id):
            return building

         to_merge = Building.find(l_b_id)

         if to_merge is not None:
            # abbiamo trovato un building corrispondente all'id legacy
            #building["dxf"] = to_merge["dxf"]
            building.attr("dxf", to_merge.attr("dxf"))
            to_merge.destroy()

      return building


