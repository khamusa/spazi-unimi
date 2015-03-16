from collections import Counter
import re

class BuildingIdAnalysis():
   general_count           = Counter()
   buildings_without_b_id  = set()

   @classmethod
   def analyse_building_id(klass, building):
      b_id     = building.get_path("_id")
      l_b_id   = building.get_path("merged.l_b_id")
      klass.general_count.update({"total_buildings" : 1})

      if b_id == l_b_id and re.match("^\d{4}$", b_id):
         klass.general_count.update({"buildings_without_b_id" : 1})
         klass.buildings_without_b_id.add(b_id)

