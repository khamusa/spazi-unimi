import unittest
from db.db import DB
from config_manager import ConfigManager
from mock import MagicMock
from db.db_persistence_manager import DBPersistenceManager

class DbTest(unittest.TestCase):

   def setUp(self) :
      self.db = MagicMock()
      self.pm = DBPersistenceManager(db=self.db)

   def test_clientCreation(self) :
      config = ConfigManager("config.json")["db"]
      db = DB( config["url"], config["port"], config["db_name"])

   def test_roomcategory_save(self):
      args = { "cat_id" : "123" , "cat_name" : "room" }
      self.pm.insert_room_category( args )
      self.db["room_categories"].insert.assert_called_once_with( args )
