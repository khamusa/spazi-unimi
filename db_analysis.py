from config_manager                                import ConfigManager
from persistence.db.mongo_db_persistence_manager   import MongoDBPersistenceManager
from utils.logger                                  import Logger
from model                                         import ORMModel, Building
from collections                                   import Counter
from itertools                                     import chain
import time

persistence = MongoDBPersistenceManager(ConfigManager("config/general.json"))
ORMModel.set_pm( persistence )
buildings = Building.where({})

def dxf_rooms_association(b, stats):
   dxf = b.get("dxf", None)
   if not dxf:
      Logger.info("No DXF data associated.")
   else:
      for dxf_f in dxf["floors"]:

         f_id              = dxf_f["f_id"]
         identified_rooms  = len(dxf_f["rooms"])
         unidentified      = len(dxf_f["unidentified_rooms"])
         categorized       = len( [ r for r in dxf_f["unidentified_rooms"] if "cat_name" in r ] )
         total_rooms       = identified_rooms + unidentified
         no_association    = unidentified - categorized

         stats["dxf"].update({ "Total Floors"            : 1 })
         stats["dxf"].update({ "Total Rooms"             : total_rooms })
         stats["dxf"].update({ "Identified Rooms"        : identified_rooms })
         stats["dxf"].update({ "Categorized Rooms"       : categorized })
         stats["dxf"].update({ "Rooms w/o information"   : unidentified - categorized })

         message  = "Floor {:7}".format(f_id)
         message += "Total rooms: {:<5}".format(total_rooms)
         message += "Identified Rooms: {:<12}".format(format_with_percentages(identified_rooms, total_rooms))
         message += "Categorized : {:<12}".format(format_with_percentages(categorized, total_rooms))
         message += "No Association: {:<12}".format(format_with_percentages(no_association, total_rooms))

         if(no_association/total_rooms < .3):
            Logger.info(message)
         else:
            Logger.warning(message)

def csv_to_dxf_percentages(source_ns, target_ns, b, stats):
   source_ns_attrs   = b.get(source_ns, {})

   target_rooms_ids     = [ f.get("rooms", {}).keys() for f in b.get(target_ns, {}).get("floors", []) ]
   target_rooms_ids     = set(chain(*target_rooms_ids))

   source_ns_stats               = stats[source_ns]
   source_ns_stats[b["b_id"]]    = {}
   building_stats                = source_ns_stats[b["b_id"]]
   source_ns_floors              = source_ns_attrs.get("floors", [])

   if not source_ns_attrs or not source_ns_floors:
      return

   with Logger.info(source_ns, "-> ", target_ns, "Room Mapping: "):
      for f in source_ns_floors:
         source_ns_stats[f["f_id"]] = Counter()
         floor_stats                = source_ns_stats[f["f_id"]]

         for r_id in f.get("rooms", []):
            floor_stats.update({ "Total Rooms" })

            if r_id in target_rooms_ids:
               floor_stats.update({ "Matched Rooms" })

         total_rooms = floor_stats["Total Rooms"]

         matched_rooms  = floor_stats["Matched Rooms"]
         no_association = total_rooms - matched_rooms
         source_ns_stats["totals"].update({ "Total Rooms": total_rooms})
         source_ns_stats["totals"].update({ "Matched Rooms": matched_rooms})

         message  = "Floor {:7}".format(f["f_id"])
         message += "CSV # of rooms: {:<5}".format(total_rooms)
         if total_rooms:
            message += "Matched with DXF: {:<12}".format(format_with_percentages(matched_rooms, total_rooms))
         else:
            message += "Matched with DXF: {:0<3}".format(matched_rooms)

         if (not total_rooms) or (no_association/total_rooms < .3):
            Logger.info(message)
         else:
            Logger.warning(message)

         source_ns_stats["totals"].update({ "Total Floors" })
         if floor_stats["Matched Rooms"]:
            source_ns_stats["totals"].update({ "Matched Floors (at least 1 room)" })

def format_with_percentages(value, total, num_padding = 3,):
      return ("{:0>"+str(num_padding)+"} ({:>.0f}%)").format(value, value/total*100.0)

stats             = {}
stats["general"]  = Counter()
stats["dxf"]      = Counter()
stats["edilizia"] = { "totals" : Counter() }
stats["easyroom"] = { "totals" : Counter() }

for b in buildings:
   stats["general"].update({ "Total Buildings" })
   name           = "merged" in b and b["merged"]["building_name"] or "No building name"
   l_b_id         = "merged" in b and " (l_bid: {})".format(b["merged"]["l_b_id"]) or ""
   intro_message  = "Analyzing building {:6}{} - {}".format(b["b_id"], l_b_id, name)

   with Logger.info(intro_message):
      dxf_rooms_association(b, stats)
      csv_to_dxf_percentages("edilizia", "dxf", b, stats)
      csv_to_dxf_percentages("easyroom", "dxf", b, stats)

Logger.info("Finished Building analysis")

with Logger.success("Final DXF Stats"):
   report   = [
         ("Total Buildings",        lambda k, s: s[k]),
         ("Total Floors",           lambda k, s: s[k]),
         ("Total Rooms",            lambda k, s: s[k]),
         ("Identified Rooms",       lambda k, s: format_with_percentages(s[k], s["Total Rooms"], 6) ),
         ("Rooms w/o information",  lambda k, s: format_with_percentages(s[k], s["Total Rooms"], 6) ),
         ("Categorized Rooms",      lambda k, s: format_with_percentages(s[k], s["Total Rooms"], 6) )
      ]
   maxlabel = max( (len(s) for s, f in report) ) + 1
   for k, f in report:
      label = ("{:<"+ str(maxlabel) +"}").format(k)
      value = f(k, stats["dxf"])
      Logger.info(label, ":", value)


for ns in ["edilizia", "easyroom"]:
   with Logger.success("Final", ns, "->DXF Stats"):
      report   = [
            ("Total Floors",                       lambda k, s: s[k]),
            ("Matched Floors (at least 1 room)",   lambda k, s: format_with_percentages(s[k], s["Total Floors"], 3) ),
            ("Total Rooms",                        lambda k, s: s[k]),
            ("Matched Rooms",                      lambda k, s: format_with_percentages(s[k], s["Total Rooms"], 3) )
         ]

      maxlabel = max( (len(s) for s, f in report) ) + 1
      for k, f in report:
         label = ("{:<"+ str(maxlabel) +"}").format(k)
         value = f(k, stats[ns]["totals"])
         Logger.info(label, ":", value)

