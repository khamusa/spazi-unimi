import unittest
from persistence.db              import MongoDBPersistenceManager
from model.orm_model             import ORMModel
from model.building              import Building
from mock                        import MagicMock

from tasks.dxf_data_updater      import DXFDataUpdater
from tasks.easyroom_data_updater import EasyroomDataUpdater
from tasks.edilizia_data_updater import EdiliziaDataUpdater

pm = MongoDBPersistenceManager({
   "db": {
         "url"     : "localhost",
         "port"    : 27017,
         "db_name" : "campus_unimi_test"
      }
})
ORMModel.set_pm(pm)

class DataUpdaterTest(unittest.TestCase):

   def setUp(self):
      self.db_building  = {
          "_id" : "21030",
          "dxf" : {
            "l_b_id" : "5703",
            "floors" : [
               { "f_id" : "-0.5", "rooms": {}, "unidentified_rooms": [] },
            ]
          },
          "edilizia" : {
              "l_b_id"     : "5703",
              "b_id"       : "21030",
              "lat"        : "",
              "lon"        : "",
              "address"    : ""
          },
          "easyroom" : {
              "b_id"       : "21030",
              "address"    : "Via Celoria"
          }
      }

      pm.clean_collection("building")
      self.edil_up      = EdiliziaDataUpdater()
      self.easy_up      = EasyroomDataUpdater()
      self.dxf_updater  = DXFDataUpdater()

   def test_b_id_to_l_b_id_resolution_case_1(self):
      """Caso 1 - Dati inseriti nell'ordine DXF(l_b_id) -> Edilizia -> Easyroom"""

      # A)
      self.add_dxf_data()
      self.add_edil_data()
      self.validate_single_document(["dxf", "edilizia"])

      # B)
      self.add_easy_data()
      self.validate_single_document()

   def test_b_id_to_l_b_id_resolution_case_2(self):
      """Caso 1 - Dati inseriti nell'ordine DXF(l_b_id) -> Easyroom -> Edilizia"""

      # A)
      self.add_dxf_data()
      self.add_easy_data()

      # Adesso devono esistere DUE documenti relativi allo stesso building,
      # uno con l_b_id e un altro con b_id
      b1 = Building.find(self.db_building["easyroom"]["b_id"])
      b2 = Building.find(self.db_building["dxf"]["l_b_id"])

      self.assertTrue(b1 and b2)
      self.assertTrue(b1.has_attr("easyroom"))
      self.assertTrue(b2.has_attr("dxf"))

      # B)
      self.add_edil_data()
      self.validate_single_document()


   def test_b_id_to_l_b_id_resolution_case_3(self):
      """Caso 1 - Dati inseriti nell'ordine Edilizia -> DXF(l_b_id) -> Easyroom"""

      # A)
      self.add_edil_data()
      self.add_dxf_data()

      # B)
      self.add_easy_data()
      self.validate_single_document()

   def add_dxf_data(self):
      b = Building.find( self.db_building["_id"] )

      if b:
         self.assertIsNotNone(b)
         floor_mock = MagicMock()
         floor_mock.to_serializable = MagicMock(return_value={ "b_id": "123", "f_id": "-0.5", "rooms": [] })
         self.dxf_updater.save_floor( b, floor_mock )
         self.validate_single_document(["dxf", "edilizia"])
      else:
         b = Building( {"_id" : self.db_building["dxf"]["l_b_id"] })
         b.attr("dxf", { "floors": self.db_building["dxf"]["floors"] })
         b.save()

   def add_edil_data(self):
      self.edil_up.update_buildings( [self.db_building["edilizia"]] )

   def add_easy_data(self):
      self.easy_up.update_buildings( [self.db_building["easyroom"]] )

   def validate_single_document(self, namespaces=None):
      """Valida che ci sia un documento che contiene tutte le info"""
      b = Building.find( self.db_building["_id"] )

      if namespaces is None or ("edilizia" in namespaces):
         self.assertTrue( b.has_attr("edilizia") )
         self.assertEqual( b.attr("edilizia")["l_b_id"], "5703" )

      if namespaces is None or ("dxf" in namespaces):
         self.assertEqual(b.attr("dxf")["floors"], self.db_building["dxf"]["floors"])
         self.assertEqual( b.attr("dxf")["floors"][0]["f_id"], "-0.5" )

      if namespaces is None or ("easyroom" in namespaces):
         self.assertTrue( b.has_attr("easyroom") )
         self.assertEqual( b.attr("easyroom")["address"], "Via Celoria" )

      # Non dev'esserci un documento con legacy building id
      self.assertIsNone( Building.find(self.db_building["dxf"]["l_b_id"]) )

   def test_updated_at(self):
      self.add_edil_data()
      b = Building.find( self.db_building["_id"] )

      self.assertEqual(b["edilizia"]["updated_at"], b["updated_at"])
      self.assertTrue("easyroom" not in b)

      self.add_easy_data()
      b = Building.find( self.db_building["_id"] )

      self.assertEqual(b["easyroom"]["updated_at"], b["updated_at"])
      self.assertTrue(b["easyroom"]["updated_at"] > b["edilizia"]["updated_at"])

