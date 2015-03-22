import unittest
from model              import Building
from model.odm          import ODMModel
from persistence.db     import MongoDBPersistenceManager

class ODMBuildingModelTest(unittest.TestCase):

   def setUp(self):
      self._pm = MongoDBPersistenceManager({
         "db": {
               "url"    : "localhost",
               "port"   : 27017,
               "db_name" : "campus_unimi_test"
            }
      })
      ODMModel.set_pm(self._pm)
      self._pm.clean_collection("building")


   def test_building_creation(self):
      b = Building({ "_id" : 123, "height" : "everest" })

      self.assertEqual(b.attr("b_id"), "123")
      self.assertEqual(b.attr("_id"), "123")
      self.assertEqual(b.attr("height"), "everest")

   def test_building_find(self):
      b = Building.find(12)
      self.assertEqual(b, None)

      self._pm.save("building", { "_id" : "123", "pluto" : 333 } )

      b = Building.find(123)
      self.assertEqual(b.attr("pluto"), 333)

      self.assertEqual( b.is_changed() , False )

   def test_find_if_building_not_exists(self):
      b = Building.find(12)
      self.assertEqual(b, None)

      b = Building.find_or_create_by_id(12)
      self.assertEqual(b.is_changed(), True )
      self.assertEqual(b.attr("_id"), "12" )
      self.assertEqual(b.attr("b_id"), "12" )

   def test_find_and_update(self):
      b1 = Building.find_or_create_by_id(12)
      b1.attr("pippo", "paperino")
      b1.save()

      b2 = Building.find_or_create_by_id(12)

      self.assertEqual(b1, b2)








