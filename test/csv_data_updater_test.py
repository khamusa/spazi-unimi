import unittest
from tasks.csv_data_updater import CSVDataUpdater, InvalidCSVHeaderError
from mock import MagicMock

class CSVDataUpdaterTest(unittest.TestCase):

   def setUp(self):
      self.csv_updater = CSVDataUpdater({
            "a": ["1", "2", "3"],
            "b": ["4", "5", "6"]
         }, MagicMock())


   def test_header_inference(self):
      infer = self.csv_updater.infer_csv_from_header

      self.assertEqual("b", infer({"4", "5", "6"}) )
      self.assertEqual("b", infer({"4", "2", "5", "6"}) )
      self.assertEqual("b", infer({"4", "5", "8", "6"}) )
      self.assertEqual("b", infer({"4", "5", "6", "HA"}) )
      self.assertEqual("b", infer({"BUGUE", "4", "5", "6", "HA"}) )

      self.assertEqual("a", infer({"1", "2", "3"}) )
      self.assertEqual("a", infer({"4", "2", "3", "1"}) )
      self.assertEqual("a", infer({"3", "1", "8", "2"}) )
      self.assertEqual("a", infer({"4", "5", "3", "HA", "1", "2"}) )


      self.assertEqual(None, infer({"4", "7", "6"}) )
      self.assertEqual(None, infer({"4", "2", "1", "6"}) )
      self.assertEqual(None, infer({"3", "5", "8", "6"}) )
      self.assertEqual(None, infer({"1", "1", "6", "HA"}) )
      self.assertEqual(None, infer({"BUGUE", "4", "5", "HA"}) )

      self.assertEqual(None, infer({"1", "a", "3"}) )
      self.assertEqual(None, infer({"4", "b", "3", "1"}) )
      self.assertEqual(None, infer({"3", "1", "8", "c"}) )
      self.assertEqual(None, infer({"4", "5", "3", "HA", "pippo", "pluto"}) )


   def test_update_categories_calls_persistence_manager_correctly(self):
      cat = ["first", "second"]
      self.csv_updater.update_room_categories(cat)
      self.csv_updater._pm.insert_room_categories.assert_called_once_with(cat)

   def test_perform_update_calls_correct_update_method_for_room_categories(self):
      readerMock = MagicMock(return_value = MagicMock(content = "pippo"))
      self.csv_updater.infer_csv_from_header = MagicMock(return_value = "room_categories")
      self.csv_updater.update_room_categories = MagicMock()
      self.csv_updater.perform_update("Test.csv", reader_class = readerMock)
      self.csv_updater.update_room_categories.assert_called_once_with("pippo")

   def test_perform_update_raises_exception_on_unknown_csv_type(self):
      readerMock = MagicMock()
      self.csv_updater.infer_csv_from_header = MagicMock(return_value = None)
      with self.assertRaises(InvalidCSVHeaderError):
         self.csv_updater.perform_update("Test.csv", reader_class = readerMock)


   def test_update_buildings_calls_persistence_manager_correctly(self):
      buildings = [{"first":1}, {"second":2}]
      self.csv_updater.add_origin = MagicMock(return_value=buildings)
      self.csv_updater.update_buildings(buildings)
      self.csv_updater._pm.insert_buildings.assert_called_once_with(buildings)

   def test_perform_update_calls_correct_update_method_for_buildings(self):
      readerMock = MagicMock(return_value = MagicMock(content = "pippo"))
      self.csv_updater.infer_csv_from_header = MagicMock(return_value = "buildings")
      self.csv_updater.update_buildings = MagicMock()
      self.csv_updater.perform_update("Test.csv", reader_class = readerMock)
      self.csv_updater.update_buildings.assert_called_once_with("pippo")

   def test_update_rooms_calls_persistence_manager_correctly(self):
      rooms = ["first", "second"]
      self.csv_updater.add_origin = MagicMock(return_value=rooms)
      self.csv_updater.update_rooms(rooms)
      self.csv_updater._pm.insert_rooms.assert_called_once_with(rooms)

   def test_perform_update_calls_correct_update_method_for_rooms(self):
      readerMock = MagicMock(return_value = MagicMock(content = "pippo"))
      self.csv_updater.infer_csv_from_header = MagicMock(return_value = "rooms")
      self.csv_updater.update_rooms = MagicMock()
      self.csv_updater.perform_update("Test.csv", reader_class = readerMock)
      self.csv_updater.update_rooms.assert_called_once_with("pippo")

   def test_prepare_origin(self):
      items = self.csv_updater.add_origin([ { "key1":1 , "key2":"pippo" } , { "key1":1 , "key2":"pluto" } ])
      self.assertEqual(list(items),[ { "key1":1 , "key2":"pippo" , "origin":"csv" } , { "key1":1 , "key2":"pluto" , "origin":"csv"} ])
