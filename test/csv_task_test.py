import unittest
from tasks.csv_task import CSVTask
from tasks.task import FileUpdateException
from persistence.db import MongoDBPersistenceManager
from mock import MagicMock
from utils.logger import Logger

class CSVTaskTest(unittest.TestCase):

   def setUp(self):
      self.csv_task = CSVTask({ "csv_headers":{
            "edilizia":{
               "a": ["1", "2", "3"],
               "b": ["4", "5", "6"]
            },
            "easyroom":{
               "a": ["1", "2", "7"],
               "b": ["4", "5", "8"]
            }
         },
            "folders":{
               "data_csv_sources" : "folder"
               }
         }, MagicMock() )


   def test_header_inference(self):
      Logger.verbosity = 0
      infer = self.csv_task.infer_csv_from_header

      self.assertEqual( ("edilizia","b") , infer({"4", "5", "6"}) )
      self.assertEqual( ("edilizia","b") , infer({"4", "2", "5", "6"}) )

      self.assertEqual( ("easyroom","a") , infer({"1", "2", "7", "6"}) )
      self.assertEqual( ("easyroom","a") , infer({"2", "7", "1", "6" , "10"}) )

      self.assertEqual( ("easyroom","b") , infer({"8", "5", "4", "10"}) )

      self.assertEqual( ("edilizia","a") , infer({"1", "2", "22", "3"}) )

      self.assertEqual(None, infer({"1", "6" , "10"}))
      self.assertEqual(None, infer({"22", "10" , "33"}))
      self.assertEqual(None, infer({"1", "3", "10" }))

