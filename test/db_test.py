from persistence.db  import *
from config_manager  import ConfigManager
from mock            import MagicMock
import unittest

class DbTest(unittest.TestCase):

   def setUp(self) :
      self.db = MagicMock()
      self.pm = MongoDBPersistenceManager(db=self.db)

   def test_clientCreation(self) :
      config = ConfigManager("config/general.json")["db"]
      db = DB( config["url"], config["port"], config["db_name"])

   def test_cleancollection(self):
      self.pm.clean_collection("building")
      self.db["building"].drop.assert_called_once_with()
