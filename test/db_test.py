import unittest
from db.db import DB
from config_manager import ConfigManager

class DbTest(unittest.TestCase):

   def test_clientCreation(self) :
      config = ConfigManager("config.json")["db"]

      db = DB( config["url"], config["port"], config["db_name"])

