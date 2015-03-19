import unittest
from model     import Building
from mock      import MagicMock, call
from datetime  import datetime

class BuildingModelTest(unittest.TestCase):
   def setUp(self):
      self.old_pm = Building._pm
      self.pm = MagicMock()
      Building.set_pm(self.pm)

   def test_remove_untouched_keys(self):
      batch_date = datetime.now()
      Building.remove_untouched_keys("edilizia", batch_date)

      query    = {
         "edilizia" : {"$exists": True},
         "edilizia.updated_at" : { "$lt" : batch_date }
      }
      action   = {
         "$unset" : {"edilizia" : ""},
         "$set"   : {"deleted_edilizia" : batch_date}
      }
      options  = {"multi" : True}
      self.pm.update.assert_called_once_with("building", query, action, options)

      self.pm.reset_mock()
      Building.remove_untouched_keys("easyroom", batch_date)

      query    = {
         "easyroom" : {"$exists": True},
         "easyroom.updated_at" : { "$lt" : batch_date }
      }
      action   = {
         "$unset" : {"easyroom" : ""},
         "$set"   : {"deleted_easyroom" : batch_date}
      }
      options  = {"multi" : True}
      self.pm.update.assert_called_once_with("building", query, action, options)

   def test_remove_deleted_buildings(self):
      building_collection = Building.collection_name()
      Building.remove_deleted_buildings()

      query    = {
         "$or" : [
            {
               "edilizia" : {"$exists": False},
               "deleted_easyroom" : { "$exists": True }
            },
            {
               "easyroom" : {"$exists": False},
               "deleted_edilizia" : { "$exists": True }
            }
         ]
      }
      options  = {"multi" : True}
      self.assertEqual(self.pm.remove.call_count, 2)

      valid_ids = Building._pm.get_collection_ids(building_collection)
      query_bv = {
         "_id" : {
            "$nin" : list(valid_ids)
         }
      }

      call1 = call(building_collection, query, options)
      call2 = call("buildingview", query_bv, options)
      self.pm.remove.assert_has_calls([call1, call2], any_order = True)

   def tearDown(self):
      Building.set_pm(self.old_pm)
