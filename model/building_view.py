from .odm   import ODMModel
from .      import Building
from utils  import myfunctools
import json

class BuildingView(ODMModel):
   config_file = "config/floor_inference.json"
   with open(config_file) as cf:
      floor_dict = json.load(cf)

   def create_from_building(building):
      identic_keys      = [
         "address", "building_number", "building_name", "l_b_id", "coordinates"
      ]
      merged_key        = building.get("merged", {})
      bv_attrs          = myfunctools.filter_keys(merged_key, identic_keys)
      bv_attrs["_id"]   = building["_id"]

      bv_attrs["floors"] = {
         f["f_id"] : BuildingView._prepare_floor_obj(f)
         for f in building.get_path("merged.floors", [])
      }

      return BuildingView(bv_attrs)

   @classmethod
   def _prepare_floor_obj(klass, floor):
      remove_polygon = lambda r: myfunctools.remove_keys(r, ["polygon"])
      rooms_dict     = {
         r_id : remove_polygon(room)
         for r_id, room in floor.get("rooms", {}).items()
      }
      final_floor    = { "rooms" : rooms_dict }

      services       = set()
      for r in floor.get("unidentified_rooms", []):
         if "cat_name" in r:
            services.add(r["cat_name"])

      final_floor["available_services"] = list(services)

      f_id        = floor.get("f_id", "")
      floor_info  = klass.floor_dict.get(f_id, None)

      if floor_info:
         final_floor["floor_name"] = floor_info["floor_name"]

      return final_floor

   @classmethod
   def remove_deleted_buildings(klass):
      """
      Listener to be excuted after Building.remove_deleted_buildings. Intended to
      ensure that BuildingView documents are also removed after Building objects.
      """
      valid_ids   = klass._pm.get_collection_ids(Building.collection_name())
      options     = {"multi" : True}
      query       = {
         "_id" : {
            "$nin" : list(valid_ids)
         }
      }

      klass._pm.remove(BuildingView.collection_name(), query, options)
