from config_manager                                import ConfigManager
from persistence.db.mongo_db_persistence_manager   import MongoDBPersistenceManager
from model                                         import ODMModel, Building
from utils.logger                                  import Logger
from analysis.dxf_analysis                         import DXFAnalysis
from analysis.floor_merge_analysis                 import FloorMergeAnalysis
from analysis.building_id_analysis                 import BuildingIdAnalysis

persistence = MongoDBPersistenceManager(ConfigManager("config/general.json"))
ODMModel.set_pm( persistence )


def data_and_percent(value, total, num_padding = 3,):
   if(total > 0):
      return ("{:0>"+str(num_padding)+"} ({:>0.1f}%)").format(value, value/total*100.0)
   else:
      return ("{:0>"+str(num_padding)+"} ").format(value)

class GeneralReport:

   merge_tuples = [
            ("edilizia", "dxf"),
            ("edilizia", "easyroom"),
            ("easyroom", "dxf"),
            ("easyroom", "edilizia")
         ]

   @classmethod
   def report_building(klass, building):
      BuildingIdAnalysis.analyse_building_id(building)

      with Logger.info("Analysing "+str(building)):
         with Logger.info("DXF Data Analysis"):
            klass._print_dxf_analysis(building)

         no_data = set()
         for source, target in klass.merge_tuples:
            klass._print_merge_analysis(source, target, building)

            if not building.get_path(source+".floors"):
               no_data.add(source)

            if not building.get_path(target+".floors"):
               no_data.add(target)

         if no_data:
            Logger.info("Source doesn't exist or has no floor information:", ", ".join(no_data))

   @classmethod
   def _print_dxf_analysis(klass, building):
      dxf_info = DXFAnalysis.analyse_dxf_info(building)

      for f_id, count, which in dxf_info:
         total_rooms          = count["total_rooms"]
         identified_rooms     = data_and_percent(count["identified_rooms"], total_rooms)
         categorized_rooms    = data_and_percent(count["categorized_rooms"], total_rooms)
         no_info_rooms        = data_and_percent(count["no_info_rooms"], total_rooms)

         message  = "Floor {:5} | ".format(f_id)
         message += "Rooms: {:<4} | ".format(total_rooms)
         message += "With Id.: {:<12} | ".format(identified_rooms)
         message += "With Cat: {:<12} | ".format(categorized_rooms)
         message += "No info: {:<11} | ".format(no_info_rooms)
         message += "Wall objs: {:<4} | ".format(count["walls"])
         message += "Window objs: {:<4}".format(count["windows"])

         Logger.info(message)

   @classmethod
   def _print_merge_analysis(klass, source, target, building):

      method_name = "analyse_"+source+"_to_"+target
      merge_info  = getattr(FloorMergeAnalysis, method_name)(building)

      if not building.get_path(source+".floors"):
         return

      if not building.get_path(target+".floors"):
         return

      with Logger.info("{} -> {} Merge Analysis".format(source.upper(), target.upper())):
         for f_id, count, which in merge_info:
            total_rooms             = count["total_rooms"]
            identified_rooms        = data_and_percent(count["identified_rooms"], total_rooms)
            non_identified_rooms    = data_and_percent(count["non_identified_rooms"], total_rooms)

            message  = "Floor {:5} | ".format(f_id)
            message += "Rooms: {:<4} | ".format(total_rooms)
            message += "With Id.: {:<12} | ".format(identified_rooms)
            message += "No Id: {:<12}".format(non_identified_rooms)
            with Logger.info(message):
               if count["non_identified_rooms"]:
                  Logger.warning(
                     source,
                     "knows about room(s)",
                     ", ".join(which["non_identified_rooms"]),
                     "but", target, "does not"
                     )

   @classmethod
   def final_report(klass):
      Logger.info("#####################################")
      Logger.info("########### FINAL REPORTS ###########")
      Logger.info("#####################################")
      klass._final_building_id_report()
      klass._final_dxf_report()
      klass._final_merge_report()

   @classmethod
   def _final_building_id_report(klass):
      count = BuildingIdAnalysis.general_count
      Logger.info(
         "Total Buildings: ", count["total_buildings"]
         )
      Logger.info(
         "Buildings using legacy id: ", count["buildings_without_b_id"]
         )
      if count["buildings_without_b_id"]:
         Logger.info(
            "Legacy ids being used:", ", ".join(BuildingIdAnalysis.buildings_without_b_id)
            )

   @classmethod
   def _final_dxf_report(klass):
      with Logger.info("DXF Analysis"):
         count = DXFAnalysis.general_count
         total_floors         = count["dxf.total_floors"]
         matched_floors       = data_and_percent(count["dxf.matched_floors"], total_floors)
         total_rooms          = count["dxf.total_rooms"]
         identified_rooms     = data_and_percent(count["dxf.identified_rooms"], total_rooms)
         categorized_rooms    = data_and_percent(count["dxf.categorized_rooms"], total_rooms)
         no_info_rooms        = data_and_percent(count["dxf.no_info_rooms"], total_rooms)

         Logger.info("Total Floors        : {}".format(total_floors))
         Logger.info(
            "Matched Floors      : {:<14}".format(matched_floors),
            "(Floors with at least one room associated to other sources)"
            )
         Logger.info("Total Rooms         : {}".format(total_rooms))
         Logger.info(
            "Rooms Identified    : {:<14}".format(identified_rooms),
            "(there exists at least one data source with information about those rooms)"
            )
         Logger.info(
            "Rooms with Category : {}".format(categorized_rooms),
            "(unidentified rooms for which we can infer it's type)"
         )
         Logger.info("Rooms with no info  : {}".format(no_info_rooms))

   @classmethod
   def _final_merge_report(klass):
      with Logger.info("Merge Analysis"):
         count = FloorMergeAnalysis.general_count
         which = FloorMergeAnalysis.general_which

         for source, target in klass.merge_tuples:
            with Logger.info("Merged floor data from {} to {}".format(source, target)):
               prefix = source+"_"+target

               total_floors         = count[prefix+".total_floors"]
               identified_rooms     = len(which[prefix+".identified_rooms"])
               non_identified_rooms = len(which[prefix+".non_identified_rooms"])
               total_rooms          = identified_rooms + non_identified_rooms
               identified_rooms     = data_and_percent(identified_rooms, total_rooms)
               non_identified_rooms = data_and_percent(non_identified_rooms, total_rooms)

               Logger.info("Total floors analysed         : {}".format(total_floors))
               Logger.info("Total rooms found on {:<8} : {}".format(source, total_rooms))
               Logger.info("Found in both sources         : {}".format(identified_rooms))

               with Logger.info("Not found on {:<9}        : {}".format(target, non_identified_rooms)):
                  if which[prefix+".non_identified_rooms"]:
                     unident = sorted(which[prefix+".non_identified_rooms"])

                     while unident:
                        message = ""
                        for room_id in unident[:9]:
                           message += "{:<12}".format(room_id)

                        Logger.info(message)
                        unident = unident[9:]



for b in Building.where({}):
   GeneralReport.report_building(b)

GeneralReport.final_report()
