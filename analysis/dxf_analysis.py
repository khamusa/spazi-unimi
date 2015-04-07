from collections import Counter

class DXFAnalysis():
   general_count = Counter()

   @classmethod
   def analyse_dxf_info(klass, building):
      """
      Analyse the dxf informations of a building an return a list of
      informations for every floor in the building.

      Arguments:
      - building: a Building object that contains the db informations.

      Returns:
      - a list of informations for every floor.
      """
      results        = []
      for floor in building.get_path("dxf.floors", []):
         floor_info  = klass._analyse_dxf_floor(floor)
         results.append(floor_info)

      return results

   @classmethod
   def _analyse_dxf_floor(klass, floor):
      """
      Analyse a dxf floor and return a floor id, a count of rooms, walls and
      windows and a set of the room ids identified.

      Arguments:
      - floor: dictionary that representing the informations of a building's
      floor.

      Returns:
      - a string that representing the floor id;
      - a Counter object that contains a count of total rooms, identified rooms,
         categorized rooms, no_info rooms, walls entities and windows entities;
      - a set of strings that representing the ids of identified rooms.
      """
      count       = Counter()
      identified  = set(floor.get("rooms", {}).keys())
      count.update({"identified_rooms" : len(identified)})
      count.update({"walls"            : len(floor.get("walls", []))})
      count.update({"windows"          : len(floor.get("windows", []))})

      for room in floor.get("unidentified_rooms", []):
         if "cat_id" in room:
            count.update({"categorized_rooms" : 1})
         else:
            count.update({"no_info_rooms" : 1})

      total =  count["identified_rooms"] + count["categorized_rooms"] + count["no_info_rooms"]

      count.update({"total_rooms" : total})
      f_id  = floor.get("f_id", "")

      klass._update_general_stats(count)

      return (f_id, count, {"identified" : identified})

   @classmethod
   def _update_general_stats(klass, floor_count):
      klass.general_count.update({
         "dxf.total_rooms"       : floor_count["total_rooms"],
         "dxf.identified_rooms"  : floor_count["identified_rooms"],
         "dxf.categorized_rooms" : floor_count["categorized_rooms"],
         "dxf.no_info_rooms"     : floor_count["no_info_rooms"],
         "dxf.total_floors"      : 1
      })

      if floor_count["identified_rooms"]:
         klass.general_count.update({"dxf.matched_floors" : 1})
