import unittest
from model.orm_model    import ORMModel, ORMAttrs
from persistence.db     import MongoDBPersistenceManager
from mock               import MagicMock

class ORMModelTest(unittest.TestCase):
   def setUp(self):
      self.orm = ORMModel( { "pippo" : "pluto", "mickey": "paperino" } )
      self.old_before_callbacks    = ORMModel.before_callbacks
      self.old_after_callbacks     = ORMModel.after_callbacks

      ORMModel.before_callbacks    = {}
      ORMModel.after_callbacks     = {}

   def tearDown(self):
      ORMModel.before_callbacks    = self.old_before_callbacks
      ORMModel.after_callbacks     = self.old_after_callbacks

   def test_collection_name(self):
      self.assertEqual(self.orm.collection_name(), 'ormmodel')
      self.assertEqual(ORMModel.collection_name(), 'ormmodel')

   def test_clean(self):
      pm = MongoDBPersistenceManager({
         "db": {
               "url"     : "localhost",
               "port"    : 27017,
               "db_name" : "campus_unimi_test"
            }
      })
      ORMModel.set_pm(pm)
      dic = {"_id" : "2323", "pippo" : "pluto"}
      orm = ORMModel(dic)
      orm.save()
      self.assertEqual(ORMModel._pm.get_collection("ormmodel").find_one({"_id" : "2323"}), dic)
      orm.clean()
      self.assertEqual(ORMModel._pm.get_collection("ormmodel").find_one({"_id" : "2323"}), None)

   def test_destroy(self):
      pm = MagicMock()
      ORMModel.set_pm(pm)
      dic = {"_id" : "2323", "pippo" : "pluto"}
      orm = ORMModel(dic)
      orm.destroy()
      pm.destroy_by_id.assert_called_once_with(orm.collection_name(), "2323")

   def test_class_callbacks_are_saved(self):
      ORMModel.listen("before_save", "pippo")
      ORMModel.listen("before_save", "pluto")
      ORMModel.listen("before_save", "sempronio")

      self.assertTrue("pippo" in ORMModel.before_callbacks["ORMModel"]["save"])
      self.assertTrue("pluto" in ORMModel.before_callbacks["ORMModel"]["save"])
      self.assertTrue("sempronio" in ORMModel.before_callbacks["ORMModel"]["save"])

      self.assertEqual(["pippo", "pluto", "sempronio"], ORMModel.before_callbacks["ORMModel"]["save"] )

      ORMModel.listen("after_save", "pippo")
      ORMModel.listen("after_save","pluto")
      ORMModel.listen("after_save", "sempronio")

      self.assertTrue("pippo" in ORMModel.after_callbacks["ORMModel"]["save"])
      self.assertTrue("pluto" in ORMModel.after_callbacks["ORMModel"]["save"])
      self.assertTrue("sempronio" in ORMModel.after_callbacks["ORMModel"]["save"])

      self.assertEqual(["pippo", "pluto", "sempronio"], ORMModel.after_callbacks["ORMModel"]["save"] )

   def test_class_callbacks_are_called(self):
      ORMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      orm            = ORMModel(dic)
      orm.pippo      = MagicMock()
      orm.pluto      = MagicMock()
      orm.sempronio  = MagicMock()

      ORMModel.listen("before_save", "sempronio")
      ORMModel.listen("before_save", "pippo")

      ORMModel.listen("after_save", "pluto")
      ORMModel.listen("after_save", "sempronio")

      orm.save()

      MagicMock.assert_called_once_with(orm.pippo, orm)
      MagicMock.assert_called_once_with(orm.pluto, orm)
      self.assertEqual(orm.sempronio.call_count, 2)

   def test_destroy_callbacks_are_called(self):
      ORMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      orm            = ORMModel(dic)
      pippo          = MagicMock()
      pluto          = MagicMock()
      sempronio      = MagicMock()

      ORMModel.listen("before_destroy", pippo)
      ORMModel.listen("before_destroy", sempronio)
      ORMModel.listen("after_destroy", sempronio)
      ORMModel.listen("after_destroy", pluto)

      orm.destroy()

      MagicMock.assert_called_once_with(pippo, orm)
      MagicMock.assert_called_once_with(pluto, orm)
      MagicMock.assert_any_call(sempronio, orm)

   def test_instance_callbacks_are_saved(self):

      ORMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      orm            = ORMModel(dic)
      pippo          = MagicMock()
      pluto          = MagicMock()
      sempronio      = MagicMock()

      orm.listen_once("before_save", "pippo")
      orm.listen_once("before_save", "pluto")
      orm.listen_once("before_save", "sempronio")
      self.assertEqual(
                        orm.before_callbacks_single["save"],
                        ["pippo", "pluto", "sempronio"]
                        )

      orm.listen_once("after_save", "pippo")
      orm.listen_once("after_save", "sempronio")
      self.assertEqual(
                        orm.after_callbacks_single["save"],
                        ["pippo", "sempronio"]
                        )

   def test_instance_callbacks_are_executed_once(self):

      ORMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      orm            = ORMModel(dic)
      orm.pippo      = MagicMock()
      orm.pluto      = MagicMock()
      sempronio      = MagicMock()

      orm.listen_once("before_save", "pippo")
      orm.listen_once("before_save", "pluto")
      orm.listen_once("before_save", sempronio)
      orm.save()

      MagicMock.assert_called_once_with(orm.pippo, orm)
      MagicMock.assert_called_once_with(orm.pluto, orm)
      MagicMock.assert_called_once_with(sempronio, orm)
      self.assertEqual(orm.before_callbacks_single["save"], [])

      orm.pippo.reset_mock()
      orm.pluto.reset_mock()
      sempronio.reset_mock()
      orm.listen_once("after_destroy", "pippo")
      orm.listen_once("after_destroy", sempronio)
      orm.destroy()

      MagicMock.assert_called_once_with(orm.pippo, orm)
      MagicMock.assert_called_once_with(sempronio, orm)
      self.assertEqual(orm.pluto.call_count, 0)
      self.assertEqual(orm.after_callbacks_single["destroy"], [])
