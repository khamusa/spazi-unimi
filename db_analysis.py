from config_manager                                import ConfigManager
from persistence.db.mongo_db_persistence_manager   import MongoDBPersistenceManager
from model                                         import ODMModel, Building
from analysis.dxf_analysis                         import DXFAnalysis

persistence = MongoDBPersistenceManager(ConfigManager("config/general.json"))
ODMModel.set_pm( persistence )

for b in Building.where({}):
   info = DXFAnalysis.analyse_dxf_info(b)
   print(str(b))
   for i in info:
      print(i)
