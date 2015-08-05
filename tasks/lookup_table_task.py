from utils.logger    import Logger
from model           import RoomCategory,Building,BuildingView
from utils           import ConfigManager
import os
import sqlite3

class LookupTableTask:
   _db_name = "rooms_lookup.sqlite"

   def __init__(self):
      self._config = ConfigManager("config/general.json")

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
      building_view = BuildingView.get_collection()

      Logger.success("Creating new db")
      db_connection = sqlite3.connection( self.db_path() )

      sql_create = "CREATE TABLE lookup("
      sql_create += "id INTEGER PRIMARY KEY"
      sql_create += "b_id VARCHAR(6),"
      sql_create += "building_name VARCHAR(100),"
      sql_create += "f_id VARCHAR(6),"
      sql_create += "floor_name VARCHAR(20),"
      sql_create += "r_id VARCHAR(10),"
      sql_create += "room_name VARCHAR(100))"
      db_connection.execute(sql_create)

      Logger.success("Begin inserts transaction")
      db_connection.execute('BEGIN TRANSACTION')

      for index,building in enumerate(building_view):
         for f_id,floor in enumerate(building['floors']):
            for room_id in floor['rooms']:
               sql_insert = "INSERT INTO lookup VALUES({},{},{},{},{})".format(
                  index,b['_id'],
                  building['building_name'],
                  floor['f_id'],
                  floor['floor_name'],
                  room_id,
                  floor['rooms'][room_id]['room_name'])

      db_connection.execute('COMMIT')






