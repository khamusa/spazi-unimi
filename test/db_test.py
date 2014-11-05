import unittest
from db.db import Db
from config_manager import ConfigManager

class DbTest(unittest.TestCase):

   def test_clientCreation(self) :
      config = ConfigManager("config.json")["db"]

      db = Db( config["url"], config["port"], config["db_name"])
      
