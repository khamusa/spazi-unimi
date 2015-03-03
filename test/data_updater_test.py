import unittest
from persistence.db              import MongoDBPersistenceManager
from model.orm_model             import ORMModel
from model.building              import Building
from mock                        import MagicMock
from itertools                   import chain
from datetime                    import datetime, timedelta
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

      self.edil_rooms = [
         {
            'room_name' : 'Aula Seminari',
            'cat_name' : 'Aula',
            'r_id'      : 'T-065',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : 'T'
         },
         {
            'room_name' : 'Aula Pippo',
            'cat_name' : 'Aula',
            'r_id'      : 'T066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : 'T'
         },
         {
            'room_name' : 'Aula Pippo Sdentato',
            'cat_name' : 'Aula',
            'r_id'      : '1066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '1'
         }
      ]

      self.easy_rooms = [
         {
            'room_name' : 'Aula Seminari',
            'cat_name' : 'Aula',
            'r_id'      : '21030#T-065',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '0'
         },
         {
            'room_name' : 'Aula Pippo',
            'cat_name' : 'Aula',
            'r_id'      : '21030#T066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '0'
         },
         {
            'room_name' : 'Aula Pippo Sdentato',
            'cat_name' : 'Aula',
            'r_id'      : '21030#1066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '1'
         }
      ]

      pm.clean_collection("building")
      self.edil_up      = EdiliziaDataUpdater()
      self.easy_up      = EasyroomDataUpdater()
      self.dxf_updater  = DXFDataUpdater()


   ########################################
   # Building id <= => Legacy Building Id #
   ########################################
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
      b = self.retrieve_test_building()

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

   def retrieve_test_building(self):
      b = Building.find( self.db_building["_id"] )

      if not b:
         return None

      if "dxf" in b and "floors" in b["dxf"]:
         for f in b["dxf"]["floors"]:
               if "updated_at" in f:
                  del f["updated_at"]

      return b

   def validate_single_document(self, namespaces=None):
      """Valida che ci sia un documento che contiene tutte le info"""
      b = self.retrieve_test_building()

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

   ####################################################################
   # When updating building data the updated_at field must be changed #
   ####################################################################
   def test_updated_at(self):
      self.add_edil_data()
      b = self.retrieve_test_building()

      self.assertEqual(b["edilizia"]["updated_at"], b["updated_at"])
      self.assertTrue("easyroom" not in b)

      self.add_easy_data()
      b = self.retrieve_test_building()

      self.assertEqual(b["easyroom"]["updated_at"], b["updated_at"])
      self.assertTrue(b["easyroom"]["updated_at"] > b["edilizia"]["updated_at"])

   ##################
   # Room Updating  #
   ##################
   def test_edilizia_floor_normalization(self):
      self.edil_up.update_rooms(self.edil_rooms)

      b = self.retrieve_test_building()
      self.assertTrue("edilizia" in b)

      first_floor    = b["edilizia"]["floors"][0]
      second_floor   = b["edilizia"]["floors"][1]
      self.assertEqual(first_floor["f_id"], "0")
      self.assertEqual(second_floor["f_id"], "1")

   def test_valid_rooms_get_saved(self):
      self.edil_up.update_rooms(self.edil_rooms)

      b = self.retrieve_test_building()
      self.assertTrue("edilizia" in b)

      first_floor    = b["edilizia"]["floors"][0]
      second_floor   = b["edilizia"]["floors"][1]
      self.assertTrue("T-065" not in first_floor["rooms"])
      self.assertTrue("T-065" not in second_floor["rooms"])

      self.assertTrue("T066" in first_floor["rooms"])
      self.assertTrue("T066" not in second_floor["rooms"])

      self.assertTrue("1066" not in first_floor["rooms"])
      self.assertTrue("1066" in second_floor["rooms"])

   def test_edil_sanitize_room(self):
      self.edil_up.update_rooms(self.edil_rooms)

      b = self.retrieve_test_building()
      self.assertTrue("edilizia" in b)

      first_floor    = b["edilizia"]["floors"][0]
      second_floor   = b["edilizia"]["floors"][1]
      all_rooms      = chain(
                              first_floor["rooms"].items(),
                              second_floor["rooms"].items()
                              )

      for r_id, room in all_rooms:
         self.assertTrue("b_id" not in room)

   def test_easy_sanitize_room(self):
      self.easy_up.update_rooms(self.easy_rooms)

      b = self.retrieve_test_building()
      self.assertTrue("easyroom" in b)

      first_floor    = b["easyroom"]["floors"][0]
      second_floor   = b["easyroom"]["floors"][1]
      all_rooms      = chain(
                              first_floor["rooms"].items(),
                              second_floor["rooms"].items()
                              )

      for r_id, room in all_rooms:
         self.assertTrue("b_id" not in room)

      self.assertTrue("21030#T-065" not in first_floor["rooms"])
      self.assertTrue("21030#T-065" not in second_floor["rooms"])
      self.assertTrue("T-065" not in first_floor["rooms"])
      self.assertTrue("T-065" not in second_floor["rooms"])

      self.assertTrue("T066" in first_floor["rooms"])
      self.assertTrue("T066" not in second_floor["rooms"])

      self.assertTrue("1066" not in first_floor["rooms"])
      self.assertTrue("1066" in second_floor["rooms"])

   def test_call_of_remove_untouched_keys(self):
      mock_obj    = MagicMock(return_value=(0, []))
      Building.remove_untouched_keys = mock_obj
      base_date   = datetime.now()

      self.edil_up.update_buildings([self.db_building["edilizia"]])
      self.assertEqual(mock_obj.call_count, 1)
      args = mock_obj.call_args_list[0][0]
      self.assertEqual(args[0], "edilizia")
      self.assertTrue( base_date <= args[1] <= datetime.now() )

      mock_obj.reset_mock()
      self.easy_up.update_buildings([self.db_building["easyroom"]])
      self.assertEqual(mock_obj.call_count, 1)
      args = mock_obj.call_args_list[0][0]
      self.assertEqual(args[0], "easyroom")
      self.assertTrue( base_date <= args[1] <= datetime.now() )

   def test_call_of_remove_deleted_buildings(self):
      mock_obj    = MagicMock(return_value=(1, [ Building({"_id": "123"}) ]))
      Building.remove_untouched_keys = mock_obj
      mock_obj    = MagicMock(return_value=(1, [ Building({"_id": "123"}) ]))
      Building.remove_deleted_buildings = mock_obj

      self.edil_up.update_buildings([self.db_building["edilizia"]])
      mock_obj.assert_called_once_with()

      mock_obj.reset_mock()
      self.easy_up.update_buildings([self.db_building["easyroom"]])
      mock_obj.assert_called_once_with()

