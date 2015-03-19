from .      import ODMModel
from utils  import myfunctools

class BuildingView(ODMModel):

   def create_from_building(building):
      identic_keys      = [
         "address", "building_number", "building_name", "l_b_id", "coordinates"
      ]
      merged_key        = building.get("merged")
      bv_attrs          = myfunctools.filter_keys(merged_key, identic_keys)
      bv_attrs["_id"]   = building["_id"]

      bv_attrs["floors"] = {
         f["f_id"] : BuildingView._prepare_floor_obj(f)
         for f in building.get_path("merged.floors")
      }

      return BuildingView(bv_attrs)

   @classmethod
   def _prepare_floor_obj(klass, floor):
      remove_polygon = lambda r: myfunctools.remove_keys(r, ["polygon"])
      rooms_dict = {
         r_id : remove_polygon(room)
         for r_id, room in floor.get("rooms", {}).items()
      }
      final_floor = { "rooms" : rooms_dict }

      services = set()
      for r in floor.get("unidentified_rooms", []):
         if "cat_name" in r:
            services.add(r["cat_name"])

      final_floor["available_services"] = list(services)
      return final_floor
