from config_manager                                import ConfigManager
from persistence.db.mongo_db_persistence_manager   import MongoDBPersistenceManager
from model                                         import ODMModel, Building
from utils.logger                                  import Logger
from analysis.dxf_analysis import DXFAnalysis
from analysis.floor_merge_analysis import FloorMergeAnalysis

persistence = MongoDBPersistenceManager(ConfigManager("config/general.json"))
ODMModel.set_pm( persistence )


def data_and_percent(value, total, num_padding = 3,):
   if(total > 0):
      return ("{:0>"+str(num_padding)+"} ({:>0.1f}%)").format(value, value/total*100.0)
   else:
      return ("{:0>"+str(num_padding)+"} ").format(value)

class GeneralReport:


   @classmethod
   def report_building(klass, building):
      with Logger.info("Analysing "+str(building)):
         with Logger.info("DXF Data Analysis"):
            klass._print_dxf_analysis(building)

         source_target = [
            ("edilizia", "dxf"),
            ("easyroom", "dxf"),
            ("easyroom", "edilizia"),
            ("edilizia", "easyroom")
         ]

         no_data = set()
         for source, target in source_target:
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
                     "Non identified:",
                     ", ".join(which["non_identified_rooms"])
                     )

   @classmethod
   def final_report(klass):
      pass

for b in Building.where({}):
   GeneralReport.report_building(b)

GeneralReport.final_report()
