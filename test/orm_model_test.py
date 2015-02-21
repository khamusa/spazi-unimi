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

   def test_id_assignment_gets_sanitized(self):
      orm = ORMModel({ "_id": "   123 "})
      self.assertEqual(orm["_id"], "123")

      orm.attrs({ "_id" : 13124 })
      self.assertEqual(orm["_id"], "13124")

      orm["_id"] = 444
      self.assertEqual(orm["_id"], "444")

   def test_attrs_get_and_set(self):
      self.assertEqual(self.orm["pippo"], "pluto")

      self.orm.attrs( { "pippo": "sempronio", "caio": "tizio"})
      self.assertEqual(self.orm["pippo"], "sempronio")
      self.assertEqual(self.orm["caio"], "tizio")

      self.assertEqual(self.orm["mickey"], "paperino")

   def test_has_attr(self):
      self.assertTrue("pippo"  in self.orm)
      self.assertTrue("mickey" in self.orm)
      self.assertFalse("1234"  in self.orm)

   def test_collection_name(self):
      self.assertEqual(self.orm.collection_name(), 'ormmodel')
      self.assertEqual(ORMModel.collection_name(), 'ormmodel')

   def test_attr_getter_method(self):
      self.assertTrue("pippuzzo" not in self.orm)
      self.assertEqual(self.orm["pippo"], "pluto")

   def test_attr_setter_method(self):
      self.orm["pippuzzo"] = "ciao"
      self.assertEqual(self.orm["pippuzzo"] ,"ciao")

   def test_set_changed(self):
      self.orm.set_changed(False)
      self.assertFalse(self.orm.is_changed())

      self.orm.set_changed(True)
      self.assertTrue(self.orm.is_changed())

      self.orm.set_changed(False)
      self.assertFalse(self.orm.is_changed())

   def test_is_changed(self):
      self.assertTrue(self.orm.is_changed())
      self.orm.set_changed(False)
      self.orm.attr("pippo", "ciao")
      self.assertTrue(self.orm.is_changed())

      self.orm.set_changed(False)
      self.orm["pippo"] = "ciao"
      self.assertFalse(self.orm.is_changed())

      self.orm.set_changed(False)
      self.orm["pippo"] = "ciao2"
      self.assertTrue(self.orm.is_changed())

   def test_external_id_handling(self):
      attrs = ORMAttrs({ "bid": 123, "pippo": 123 }, external_id = "bid")

      def verify_id(expected):
         self.assertTrue(attrs["bid"] is attrs["_id"])
         self.assertEqual(attrs["bid"], expected)
         self.assertEqual(attrs["pippo"], 123)

      # Test __getitem__
      verify_id("123")

      # Test __setitem__
      attrs["bid"]   = "PIUFACILE"
      verify_id("PIUFACILE")

      attrs["pippo"] = "Sporcizia"
      self.assertEqual(attrs["pippo"], "Sporcizia")

      # Test __contains__
      self.assertTrue("_id"   in attrs)
      self.assertTrue("bid"   in attrs)
      self.assertTrue("pippo" in attrs)
      self.assertFalse("piw!" in attrs)

      # Test get
      attrs["_id"] = 123
      self.assertEqual(attrs.get("_id"), "123")
      self.assertEqual(attrs.get("_id", "hahaha"), "123")
      self.assertEqual(attrs.get("_idzzzz"), None)
      self.assertEqual(attrs.get("_idbiz", "hahaha"), "hahaha")
      self.assertEqual(attrs.get("bid"), "123")

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
