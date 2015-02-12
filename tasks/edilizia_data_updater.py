import re
from model              import RoomCategory
from .data_updater      import DataUpdater
from .floor_inference   import FloorInference
from model.building     import Building

class EdiliziaDataUpdater(DataUpdater):
   """
   Responsible for handling data updates from source "Edilizia"
   """

   def perform_update(self, entities_type, content ):
      """
      Main entry point, responsible for deciding what procedure to execute
      according to entities_type variable. Behaves as a simple dispatcher.

      Returns None.
      """
      {
         "room_categories" : self.update_room_categories,
         "buildings"       : self.update_buildings,
         "rooms"           : self.update_rooms
      }[entities_type](content)

   def update_room_categories(self, categories):
      """
      Main method responsible for updating room categories collection on database.
      """

      RoomCategory.clean()
      for c in categories:
         cat = RoomCategory(c)
         cat.save()

   def get_namespace(self):
      """
      The namespace simbolizes the part of document to be updated on database.

      Return value: a string representing the namespace.

      Hook method used by parent DataUpdater class.
      """
      return "edilizia"

   def _is_valid_b_id(self, b_id):
      """
      Determines wether or not b_id is a valid building identifier according to
      the current data source policies.

      Return value: True o False

      Hook method used by parent DataUpdater class
      """
      return b_id and re.match("\d+", b_id)

   def get_floor_key(self):
      """
      Returns a string representing the key to be used as floor identifier by
      this data source.

      Hook method used by parent DataUpdater class
      """
      return "l_floor"

   def sanitize_floor_id(self, l_floor):
      """
      Intended to clean up floor_ids before insertion on database.

      Arguments:
      - l_floor: the original floor_id string to be sanitized.

      Returns a string representing the sanitized version of the floor_id.

      This implementation acquires the floor id from the legacy floor id
      contained in l_floor, by requesting the service to FloorInference.
      """
      f_id = FloorInference.fid_from_string(l_floor, "suffix_regex")
      return super().sanitize_floor_id(f_id)

   def find_building_to_update(self, building_dict):
      """
      Finds on database or create a Buiding object to be updated with
      information contained by building_dict

      Arguments:
      - building_dict: a dictionary containing the new values to be inserted
      on the building.

      Returns a Building object.

      This implementation ensures that documents saved with the legacy building
      id gets incorporated into the current building object, before actually
      returning it.

      If no legacy building is present in Database, the default behaviour is
      ensured: it either returns an existing Building object or creates a new
      one.
      """

      b_id     = building_dict["b_id"]
      building = Building.find_or_create_by_id(b_id)

      # controllo di avere una mappatura tra b_id e l_b_id
      if not building.has_attr("merged") or building.attr("merged")["l_b_id"] is "":
         l_b_id   = building_dict["l_b_id"]

         if not self._is_valid_b_id(l_b_id):
            return building

         to_merge = Building.find(l_b_id)

         if to_merge is not None:
            # abbiamo trovato un building corrispondente all'id legacy
            #building["dxf"] = to_merge["dxf"]
            building.attr("dxf", to_merge.attr("dxf"))
            to_merge.destroy()

      return building


