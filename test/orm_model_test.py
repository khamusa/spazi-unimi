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
      self.assertEqual(orm.attrs()["_id"], "123")

      orm.attrs({ "_id" : 13124 })
      self.assertEqual(orm.attrs()["_id"], "13124")

   def test_attrs_get_and_set(self):
      self.assertEqual(self.orm.attrs()["pippo"], "pluto")

      self.orm.attrs( { "pippo": "sempronio", "caio": "tizio"})
      self.assertEqual(self.orm.attrs()["pippo"], "sempronio")
      self.assertEqual(self.orm.attrs()["caio"], "tizio")

      self.assertEqual(self.orm.attrs()["mickey"], "paperino")

   def test_has_attr(self):
      self.assertTrue(self.orm.has_attr("pippo"))
      self.assertTrue(self.orm.has_attr("mickey"))
      self.assertFalse(self.orm.has_attr("1234"))

   def test_collection_name(self):
      self.assertEqual(self.orm.collection_name(), 'ormmodel')
      self.assertEqual(ORMModel.collection_name(), 'ormmodel')

   def test_attr_getter_method(self):
      self.assertEqual(self.orm.attr("pippuzzo"), None)
      self.assertEqual(self.orm.attr("pippo"), "pluto")

   def test_attr_setter_method(self):
      self.orm.attr("pippuzzo","ciao")
      self.assertEqual(self.orm.attr("pippuzzo") ,"ciao")

   def test_is_changed(self):
      self.assertEqual(self.orm.is_changed(), True)
      self.orm.set_changed(False)
      self.orm.attr("pippo","ciao")
      self.assertEqual(self.orm.is_changed(), True)


   def test_external_id_handling(self):
      attrs = ORMAttrs({ "bid": 123, "pippo": 123 }, external_id = "bid")

      def verify_id(expected):
         self.assertTrue(attrs["bid"] is attrs["_id"])
         self.assertEqual(attrs["bid"], expected)
         self.assertEqual(attrs["pippo"], 123)

      # Test __getitem__
      verify_id("123")

      # Test __setitem__
      attrs["bid"] = "PIUFACILE"
      verify_id("PIUFACILE")
      attrs["pippo"] = "Sporcizia"
      self.assertEqual(attrs["pippo"], "Sporcizia")

      # Test __contains__
      self.assertTrue("_id" in attrs)
      self.assertTrue("bid" in attrs)
      self.assertTrue("pippo" in attrs)
      self.assertFalse("pippow!" in attrs)

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

   def test_save_callbacks_are_saved(self):
      ORMModel.before_save("pippo")
      ORMModel.before_save("pluto")
      ORMModel.before_save("sempronio")

      self.assertTrue("pippo" in ORMModel.before_callbacks["ORMModel"])
      self.assertTrue("pluto" in ORMModel.before_callbacks["ORMModel"])
      self.assertTrue("sempronio" in ORMModel.before_callbacks["ORMModel"])

      self.assertEqual(["pippo", "pluto", "sempronio"], ORMModel.before_callbacks["ORMModel"] )

      ORMModel.after_save("pippo")
      ORMModel.after_save("pluto")
      ORMModel.after_save("sempronio")

      self.assertTrue("pippo" in ORMModel.after_callbacks["ORMModel"])
      self.assertTrue("pluto" in ORMModel.after_callbacks["ORMModel"])
      self.assertTrue("sempronio" in ORMModel.after_callbacks["ORMModel"])

      self.assertEqual(["pippo", "pluto", "sempronio"], ORMModel.after_callbacks["ORMModel"] )

   def test_save_callbacks_are_called(self):
      ORMModel.set_pm(MagicMock())

      dic            = {"_id" : "2323", "pippo" : "pluto"}
      orm            = ORMModel(dic)
      orm.pippo      = MagicMock()
      orm.pluto      = MagicMock()
      orm.sempronio  = MagicMock()

      ORMModel.before_save("pippo")
      ORMModel.before_save("sempronio")

      ORMModel.after_save("pluto")
      ORMModel.after_save("sempronio")

      orm.save()

      orm.pippo.assert_called_once()
      orm.pluto.assert_called_once()
      orm.sempronio.assert_any_call()
