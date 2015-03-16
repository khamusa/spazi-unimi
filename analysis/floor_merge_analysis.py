from collections  import Counter
from itertools    import chain

class FloorMergeAnalysis():
   general_count = Counter()

   @classmethod
   def analyse_edilizia_to_dxf(klass, building):
      return klass._analyse_building("edilizia", "dxf", building)

   @classmethod
   def analyse_easyroom_to_dxf(klass, building):
      return klass._analyse_building("easyroom", "dxf", building)

   @classmethod
   def analyse_easyroom_to_edilizia(klass, building):
      return klass._analyse_building("easyroom", "edilizia", building)

   @classmethod
   def analyse_edilizia_to_easyroom(klass, building):
      return klass._analyse_building("easyroom", "edilizia", building)

   @classmethod
   def _analyse_building(klass, source, target, building):
      target_rooms = ( f.get("rooms", {}) for f in building.get_path(target+".floors", []) )
      target_rooms = set( k for k in chain(*target_rooms) )

      result = [
         klass._analyse_floor(f, target_rooms)
         for f in building.get_path(source+".floors", [])
      ]

      return result

   @classmethod
   def _analyse_floor(klass, floor, target_rooms):
      f_id           = floor.get("f_id")
      count          = Counter()
      floor_rooms    = set(floor.get("rooms", {}).keys())

      which = {
         "identified"     : floor_rooms.intersection(target_rooms),
         "non_identified" : floor_rooms.difference(target_rooms)
      }

      stats = {
         "total_rooms"      : len(floor_rooms),
         "identified_rooms" : len(which["identified"]),
         "non_identified"   : len(which["non_identified"])
         }

      count.update(stats)
      return (f_id, count, which)
