import unittest
from persistence.db import *
from config_manager import ConfigManager
from mock import MagicMock

class DbTest(unittest.TestCase):

   def setUp(self) :
      self.db = MagicMock()
      self.pm = MongoDBPersistenceManager(db=self.db)

   def test_clientCreation(self) :
      config = ConfigManager("config/general.json")["db"]
      db = DB( config["url"], config["port"], config["db_name"])

   def test_roomcategory_save(self):
      args = { "cat_id" : "123" , "cat_name" : "room" }
      self.pm.insert_room_category( args )
      self.db[self.pm.ROOM_CATEGORIES].insert.assert_called_once_with( args )

   def test_insertroomcategories(self):
      args = [ "first", "second" ]
      self.pm.insert_room_category = MagicMock()
      self.pm.insert_room_categories( args )
      self.pm.insert_room_category.assert_any_call("first")
      self.pm.insert_room_category.assert_any_call("second")

   def test_cleancollection(self):
      self.pm.clean_collection(self.pm.ROOM_CATEGORIES)
      self.db[self.pm.ROOM_CATEGORIES].drop.assert_called_once_with()


   def test_room_save(self):
      args = {
               "b_id"      : "213",
               "address"   : "via Senato",
               "l_floor"   : "first",
               "r_id"      : "31331",
               "type_name" : "aula",
               "room_name" : "1231231",
               "capacity"  : "1"
            }

      self.pm.insert_room(args)
      self.db[self.pm.ROOMS].insert.assert_called_once_with(args)

   def test_insertrooms(self):
      args = ["first","second"]
      self.pm.insert_room  = MagicMock()
      self.pm.insert_rooms(args)
      self.pm.insert_room.assert_any_call("first")
      self.pm.insert_room.assert_any_call("second")


   def test_building_save(self):
      args = {
            "l_b_id"    : "123",
            "b_id"      : "1234",
            "address"   : "via Senato, Milano",
            "lat"       : "12341.12231",
            "lon"       : "123.23"
      }

      self.pm.insert_building(args)
      self.db[self.pm.BUILDINGS].insert.assert_called_once_with(args)


   def test_insertbuildings(self):
      args = ["first","second"]
      self.pm.insert_building = MagicMock()
      self.pm.insert_buildings(args)
      self.pm.insert_building.assert_any_call("first")
      self.pm.insert_building.assert_any_call("second")
