from utils.logger    import Logger
from model           import RoomCategory,Building,BuildingView
from model.odm       import ODMModel
from utils           import ConfigManager
from persistence     import MongoDBPersistenceManager
import os
import sqlite3

class LookupTableTask:
   _db_name = "rooms_lookup.sqlite"

   def __init__(self):
      self._config            = ConfigManager("config/general.json")
      self._data_persistence  = MongoDBPersistenceManager(self._config)
      ODMModel.set_pm( self._data_persistence )
      BuildingView.setup_collection()

   def db_path(self):
      return os.path.join(self._config["folders"]["data_lookup_table"],LookupTableTask._db_name)

   def db_name(self):
      return LookupTableTask._db_name

   def _delete_old_db(self):
      try:
         os.remove(self.db_path())
      except IOError:
         pass

   def client_should_update_db(self,client_timestamp,db_updated_at=None):
      if not db_updated_at:
         db_updated_at = os.path.getctime( self.db_path() )

      return db_updated_at>client_timestamp

   def perform_update(self):
      Logger.success("Delete old db")
      self._delete_old_db()

      Logger.success("Retrieving building view collection from persistence")
      buildings      = list(BuildingView.get_collection().find({'building_name':{'$exists':True}}))

      Logger.success("Creating new db")
      db_connection = sqlite3.connect( self.db_path() )

      sql_create = "CREATE TABLE lookup("
      sql_create += "id INTEGER PRIMARY KEY,"
      sql_create += "b_id VARCHAR(6),"
      sql_create += "building_name VARCHAR(100),"
      sql_create += "f_id VARCHAR(6),"
      sql_create += "floor_name VARCHAR(20),"
      sql_create += "r_id VARCHAR(10),"
      sql_create += "room_name VARCHAR(100))"
      db_connection.execute(sql_create)

      Logger.success("Begin transaction")

      index = 0
      for building in buildings:
         for f_id,floor in enumerate(building['floors']):
            for room_id in floor['rooms']:
               sql_insert = 'INSERT INTO lookup VALUES({},"{}","{}","{}","{}","{}","{}")'.format(
                  index,
                  building['_id'],
                  building['building_name'],
                  floor['f_id'],
                  floor['floor_name'],
                  room_id,
                  floor['rooms'][room_id]['room_name'])
               db_connection.execute(sql_insert)
               index +=1
      db_connection.commit()
      Logger.success("End transaction")
      Logger.success("{0} entries".format(index))






