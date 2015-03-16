from collections  import Counter
from itertools    import chain

class FloorMergeAnalysis():
   general_count = Counter()
   general_which = {
      "edilizia_easyroom.identified_rooms"      : set(),
      "edilizia_easyroom.non_identified_rooms"  : set(),
      "edilizia_dxf.identified_rooms"           : set(),
      "edilizia_dxf.non_identified_rooms"       : set(),
      "easyroom_edilizia.identified_rooms"      : set(),
      "easyroom_edilizia.non_identified_rooms"  : set(),
      "easyroom_dxf.identified_rooms"           : set(),
      "easyroom_dxf.non_identified_rooms"       : set()
   }

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
      return klass._analyse_building("edilizia", "easyroom", building)

   @classmethod
   def _analyse_building(klass, source, target, building):
      target_rooms = ( f.get("rooms", {}) for f in building.get_path(target+".floors", []) )
      target_rooms = set( k for k in chain(*target_rooms) )

      result = [
         klass._analyse_floor(f, target_rooms)
         for f in building.get_path(source+".floors", [])
      ]

      klass._update_general_stats(source, target, building, result)

      return result

   @classmethod
   def _analyse_floor(klass, floor, target_rooms):
      f_id           = floor.get("f_id")
      count          = Counter()
      floor_rooms    = set(floor.get("rooms", {}).keys())

      which = {
         "identified_rooms"       : floor_rooms.intersection(target_rooms),
         "non_identified_rooms"   : floor_rooms.difference(target_rooms)
      }

      stats = {
         "total_rooms"           : len(floor_rooms),
         "identified_rooms"      : len(which["identified_rooms"]),
         "non_identified_rooms"  : len(which["non_identified_rooms"])
         }

      count.update(stats)
      return (f_id, count, which)

   @classmethod
   def _update_general_stats(klass, source, target, building, result):
      prefix = source+"_"+target
      for _, count, which in result:
         klass.general_count.update(
            {
               prefix+".total_floors"           : 1,
               prefix+".total_rooms"            : count["total_rooms"],
               prefix+".identified_rooms"       : count["identified_rooms"],
               prefix+".non_identified_rooms"   : count["non_identified_rooms"]
            })

         klass.general_which[prefix+".identified_rooms"].update(
            building["_id"]+"#"+r_id.upper() for r_id in which["identified_rooms"]
            )

         klass.general_which[prefix+".non_identified_rooms"].update(
            building["_id"]+"#"+r_id.upper() for r_id in which["non_identified_rooms"]
         )
