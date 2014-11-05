import unittest
from csv_data_updater import CSVDataUpdater

class CSVDataUpdaterTest(unittest.TestCase):

   def setUp(self):
      self.reader = CSVDataUpdater({
            "a": ["1", "2", "3"],
            "b": ["4", "5", "6"]
         })


   def test_header_inference(self):
      infer = self.reader.infer_csv_from_header

      self.assertEqual("b", infer({"4", "5", "6"}) )
      self.assertEqual("b", infer({"4", "2", "5", "6"}) )
      self.assertEqual("b", infer({"4", "5", "8", "6"}) )
      self.assertEqual("b", infer({"4", "5", "6", "HA"}) )
      self.assertEqual("b", infer({"BUGUE", "4", "5", "6", "HA"}) )

      self.assertEqual("a", infer({"1", "2", "3"}) )
      self.assertEqual("a", infer({"4", "2", "3", "1"}) )
      self.assertEqual("a", infer({"3", "1", "8", "2"}) )
      self.assertEqual("a", infer({"4", "5", "3", "6", "HA", "1", "2"}) )


      self.assertEqual(None, infer({"4", "7", "6"}) )
      self.assertEqual(None, infer({"4", "2", "1", "6"}) )
      self.assertEqual(None, infer({"3", "5", "8", "6"}) )
      self.assertEqual(None, infer({"1", "1", "6", "HA"}) )
      self.assertEqual(None, infer({"BUGUE", "4", "5", "HA"}) )

      self.assertEqual(None, infer({"1", "a", "3"}) )
      self.assertEqual(None, infer({"4", "b", "3", "1"}) )
      self.assertEqual(None, infer({"3", "1", "8", "c"}) )
      self.assertEqual(None, infer({"4", "5", "3", "HA", "pippo", "pluto"}) )


