from model.odm_model    import ODMModel
from persistence.db     import MongoDBPersistenceManager
from mock               import MagicMock
import unittest

class ODMModelTest(unittest.TestCase):
   def setUp(self):
      self.odm = ODMModel( { "pippo" : "pluto", "mickey": "paperino" } )
      self.old_before_callbacks    = ODMModel.before_callbacks
      self.old_after_callbacks     = ODMModel.after_callbacks

      ODMModel.before_callbacks    = {}
      ODMModel.after_callbacks     = {}

   def tearDown(self):
      ODMModel.before_callbacks    = self.old_before_callbacks
      ODMModel.after_callbacks     = self.old_after_callbacks

   def test_collection_name(self):
      self.assertEqual(self.odm.collection_name(), 'odmmodel')
      self.assertEqual(ODMModel.collection_name(), 'odmmodel')

   def test_clean(self):
      pm = MongoDBPersistenceManager({
         "db": {
               "url"     : "localhost",
               "port"    : 27017,
               "db_name" : "campus_unimi_test"
            }
      })
      ODMModel.set_pm(pm)
      dic = {"_id" : "2323", "pippo" : "pluto"}
      odm = ODMModel(dic)
      odm.save()
      self.assertEqual(ODMModel._pm.get_collection("odmmodel").find_one({"_id" : "2323"}), dic)
      odm.clean()
      self.assertEqual(ODMModel._pm.get_collection("odmmodel").find_one({"_id" : "2323"}), None)

   def test_destroy(self):
      pm = MagicMock()
      ODMModel.set_pm(pm)
      dic = {"_id" : "2323", "pippo" : "pluto"}
      odm = ODMModel(dic)
      odm.destroy()
      pm.destroy_by_id.assert_called_once_with(odm.collection_name(), "2323")

   def test_class_callbacks_are_saved(self):
      ODMModel.listen("before_save", "pippo")
      ODMModel.listen("before_save", "pluto")
      ODMModel.listen("before_save", "sempronio")

      self.assertTrue("pippo" in ODMModel.before_callbacks["ODMModel"]["save"])
      self.assertTrue("pluto" in ODMModel.before_callbacks["ODMModel"]["save"])
      self.assertTrue("sempronio" in ODMModel.before_callbacks["ODMModel"]["save"])

      self.assertEqual(["pippo", "pluto", "sempronio"], ODMModel.before_callbacks["ODMModel"]["save"] )

      ODMModel.listen("after_save", "pippo")
      ODMModel.listen("after_save","pluto")
      ODMModel.listen("after_save", "sempronio")

      self.assertTrue("pippo" in ODMModel.after_callbacks["ODMModel"]["save"])
      self.assertTrue("pluto" in ODMModel.after_callbacks["ODMModel"]["save"])
      self.assertTrue("sempronio" in ODMModel.after_callbacks["ODMModel"]["save"])

      self.assertEqual(["pippo", "pluto", "sempronio"], ODMModel.after_callbacks["ODMModel"]["save"] )

   def test_class_callbacks_are_called(self):
      ODMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      odm            = ODMModel(dic)
      odm.pippo      = MagicMock()
      odm.pluto      = MagicMock()
      odm.sempronio  = MagicMock()

      ODMModel.listen("before_save", "sempronio")
      ODMModel.listen("before_save", "pippo")

      ODMModel.listen("after_save", "pluto")
      ODMModel.listen("after_save", "sempronio")

      odm.save()

      MagicMock.assert_called_once_with(odm.pippo, odm)
      MagicMock.assert_called_once_with(odm.pluto, odm)
      self.assertEqual(odm.sempronio.call_count, 2)

   def test_destroy_callbacks_are_called(self):
      ODMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      odm            = ODMModel(dic)
      pippo          = MagicMock()
      pluto          = MagicMock()
      sempronio      = MagicMock()

      ODMModel.listen("before_destroy", pippo)
      ODMModel.listen("before_destroy", sempronio)
      ODMModel.listen("after_destroy", sempronio)
      ODMModel.listen("after_destroy", pluto)

      odm.destroy()

      MagicMock.assert_called_once_with(pippo, odm)
      MagicMock.assert_called_once_with(pluto, odm)
      MagicMock.assert_any_call(sempronio, odm)

   def test_instance_callbacks_are_saved(self):

      ODMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      odm            = ODMModel(dic)
      pippo          = MagicMock()
      pluto          = MagicMock()
      sempronio      = MagicMock()

      odm.listen_once("before_save", "pippo")
      odm.listen_once("before_save", "pluto")
      odm.listen_once("before_save", "sempronio")
      self.assertEqual(
                        odm.before_callbacks_single["save"],
                        ["pippo", "pluto", "sempronio"]
                        )

      odm.listen_once("after_save", "pippo")
      odm.listen_once("after_save", "sempronio")
      self.assertEqual(
                        odm.after_callbacks_single["save"],
                        ["pippo", "sempronio"]
                        )

   def test_instance_callbacks_are_executed_once(self):

      ODMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      odm            = ODMModel(dic)
      odm.pippo      = MagicMock()
      odm.pluto      = MagicMock()
      sempronio      = MagicMock()

      odm.listen_once("before_save", "pippo")
      odm.listen_once("before_save", "pluto")
      odm.listen_once("before_save", sempronio)
      odm.save()

      MagicMock.assert_called_once_with(odm.pippo, odm)
      MagicMock.assert_called_once_with(odm.pluto, odm)
      MagicMock.assert_called_once_with(sempronio, odm)
      self.assertEqual(odm.before_callbacks_single["save"], [])

      odm.pippo.reset_mock()
      odm.pluto.reset_mock()
      sempronio.reset_mock()
      odm.listen_once("after_destroy", "pippo")
      odm.listen_once("after_destroy", sempronio)
      odm.destroy()

      MagicMock.assert_called_once_with(odm.pippo, odm)
      MagicMock.assert_called_once_with(sempronio, odm)
      self.assertEqual(odm.pluto.call_count, 0)
      self.assertEqual(odm.after_callbacks_single["destroy"], [])
