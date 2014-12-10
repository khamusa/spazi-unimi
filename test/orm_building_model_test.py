import unittest
from model              import Building
from model              import ORMModel
from persistence.db     import MongoDBPersistenceManager

class ORMBuildingModelTest(unittest.TestCase):

   def setUp(self):
      self._pm = MongoDBPersistenceManager({
         "db": {
               "url"    : "localhost",
               "port"   : 27017,
               "db_name" : "campus_unimi_test"
            }
      })
      ORMModel.set_pm(self._pm)
      self._pm.clean_collection("building")


   def test_building_creation(self):
      b = Building({ "_id" : 123, "height" : "everest" })

      self.assertEqual(b.attrs()["b_id"], "123")
      self.assertEqual(b.attrs()["_id"], "123")
      self.assertEqual(b.attrs()["height"], "everest")

   def test_building_find(self):
      b = Building.find(12)
      self.assertEqual(b, None)

      self._pm.save("building", { "_id" : "123", "pluto" : 333 } )

      b = Building.find(123)
      self.assertEqual(b.attrs()["pluto"], 333)

      self.assertEqual( b.is_changed() , False )

   def test_find_if_building_not_exists(self):
      b = Building.find(12)
      self.assertEqual(b, None)

      b     = Building.find_or_create_by_bid(12)
      self.assertEqual(b.is_changed(), True )
      self.assertEqual(b.attr("_id"), "12" )
      self.assertEqual(b.attr("b_id"), "12" )








