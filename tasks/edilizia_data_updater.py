from model                          import RoomCategory
from .building_data_updater         import BuildingDataUpdater
from .room_data_updater             import RoomDataUpdater
from .floor_inference               import FloorInference
from model.building                 import Building
from tasks.data_merger              import DataMerger
from tasks.dxf_room_ids_resolver    import DXFRoomIdsResolver
from tasks.dxf_room_cats_resolver   import DXFRoomCatsResolver

class EdiliziaDataUpdater(BuildingDataUpdater, RoomDataUpdater):
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
         cat.attr("_id", cat.attr("_id").upper())
         cat.save()

      for building in Building.where({}):
         DXFRoomCatsResolver.resolve_room_categories(building, None)
         building.save()

   def get_namespace(self):
      """
      The namespace simbolizes the part of document to be updated on database.

      Return value: a string representing the namespace.

      Hook method used by parent DataUpdater class.
      """
      return "edilizia"

   def sanitize_and_validate_floor(self, floor_id, floor_rooms):
      """
      Intended to clean up and validating floor_ids before insertion on database.
      It must also Log in case the floor is invalid.

      Arguments:
      - floor_id: the original floor_id string to be sanitized.
      - floor_rooms: a list of dictionaries representing the floor rooms.

      Returns a string representing the sanitized version of the floor_id.

      It is a good practice for subclasses to call this parent superclass.
      """
      f_id = FloorInference.fid_from_string(floor_id, "suffix_regex")
      return super().sanitize_and_validate_floor(f_id, floor_rooms)

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

      # controllo di non avere una mappatura tra b_id e l_b_id
      if "merged" not in building or not building["merged"].get("l_b_id", None):
         l_b_id   = building_dict["l_b_id"]

         if not Building.is_valid_bid(l_b_id):
            return building

         to_merge = Building.find(l_b_id)

         if to_merge is not None:
            # abbiamo trovato un building corrispondente all'id legacy
            #building["dxf"] = to_merge["dxf"]

            building.attr("dxf", to_merge.attr("dxf"))

            def before_callback(b):
               DXFRoomIdsResolver.resolve_rooms_id(b, None, "edilizia")
               # Ensure floor merging is performed AFTER DXF Room_id resolution
               merged            = b.attributes_for_source("merged")
               merged["floors"]  = DataMerger.merge_floors(
                  b.get("edilizia"),
                  b.get("easyroom"),
                  b.get("dxf")
               )

            building.listen_once("before_save", before_callback)
            building.listen_once("after_save", lambda b: to_merge.destroy() )

      return building


