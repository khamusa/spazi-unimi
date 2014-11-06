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

   def test_insertroomcategories(self):
      args = [ "first", "second" ]
      self.pm.insert_room_category = MagicMock()
      self.pm.clean_collection = MagicMock()
      self.pm.insert_room_categories( args )
      self.pm.clean_collection.assert_called_once_with("room_categories")
      self.pm.insert_room_category.assert_any_call("first")
      self.pm.insert_room_category.assert_any_call("second")

   def test_cleancollection(self):
      self.pm.clean_collection("room_categories")
      self.db["room_categories"].drop.assert_called_once_with()
