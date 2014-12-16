import unittest
from tasks.csv_task  import CSVTask
from mock            import MagicMock
from tasks.task      import FileUpdateException

class CSVTaskTest(unittest.TestCase):

   def setUp(self):
      self.tsk = CSVTask({
            "csv_headers": {
               "edilizia": {
                  "a": ["1", "2", "3"],
                  "b": ["4", "5", "6"]
               },
               "easyroom" : {
                  "a": ["1", "2", "7"],
                  "b": ["4", "5", "8"]
               }
            },
            "folders": {
               "data_csv_sources" : "folder"
            }
         },
         MagicMock())


   def test_invalid_csv_header_exception_thrown(self):
      mocked_reader = MagicMock(service=None, entities_type=None)
      self.tsk._read_csv_file = MagicMock( return_value = mocked_reader )

      try:
         self.tsk.perform_update("pluto.csv")
         self.assertFalse(True, "Exception was not raised")
      except FileUpdateException as e:
         self.assertEqual(e.msg, "Invalid CSV header file")


   def test_empty_csv_content_exception_thrown(self):
      mocked_reader = MagicMock(
         service        = "Pippo",
         entities_type  = "pluto",
         content        = []
      )

      self.tsk._read_csv_file = MagicMock( return_value = mocked_reader )

      try:
         self.tsk.perform_update("pluto.csv")
         self.assertFalse(True, "Exception was not raised")
      except FileUpdateException as e:
         self.assertEqual(e.msg, "CSV file contains only header")


