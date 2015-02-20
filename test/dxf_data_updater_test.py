from mock                        import MagicMock
from tasks.dxf_data_updater      import DXFDataUpdater
from model                       import Building, RoomCategory
import unittest

class DXFDataUpdaterTest(unittest.TestCase):
   """
   Test the room merging procedures of DXFDataUpdater, i.e, the ability of
   associating DXF rooms with other souces rooms.
   """
   def setUp(self):
      # Usato come parametro nelle chiamate
      self.db_building  = {
          "dxf" : {
            "floors" : [
               {
               "f_id" : "-0.5",
               "rooms": {},
               "unidentified_rooms" : [
                     { # Room 1, matcha con easyroom
                        "texts": [
                           { "text": "StanzaMatchata" },
                           { "text": "R003" },
                           { "text": "AUL01" }
                        ]
                     },
                     { # Room 2
                        "texts": [
                           { "text": "StanzaNonMatchata" },
                           { "text": "R00p3" },
                           { "text": "WC01" }
                        ]
                     }
                     ,
                     { # Room 3, matcha con edilizia
                        "texts": [
                           { "text": "AUL03" },
                           { "text": "StanzaMatchata" },
                           { "text": "R002" }
                        ]
                     }
                  ]
               },
               {
               "f_id" : "0.5",
               "rooms": {},
               "unidentified_rooms" : [
                     { # Room 1, matcha con easyroom
                        "texts": [
                           { "text": "StanzaMatchata" },
                           { "text": "R023" },
                           { "text": "AUL01" }
                        ]
                     },
                     { # Room 2
                        "texts": [
                           { "text": "StanzaNonMatchata" },
                           { "text": "R00p3" },
                           { "text": "WC01" }
                        ]
                     }
                     ,
                     { # Room 3, matcha con edilizia
                        "texts": [
                           { "text": "AUL03" },
                           { "text": "StanzaMatchata" },
                           { "text": "R022" }
                        ]
                     }
                  ]
               },
            ]
          },
          "edilizia" : {
            "floors": [
               {
                  "f_id"  : "0",
                  "rooms" : {
                     "PippoPelato" : {},
                     "R002": {},
                     "PippoPelato2": {}
                  }
               },
               {
                  "f_id"  : "0.5",
                  "rooms" : {
                     "PippoPelato": {},
                     "PippoPelato2": {},
                     "R022": {}
                  }
               }
            ]
          },
          "easyroom" : {
            "floors": [
               {
                  "f_id"  : "0",
                  "rooms" : {
                     "PippoSdentato": {},
                     "PippoSdentato2": {},
                     "R003": {}
                  }
               },
               {
                  "f_id"  : "1",
                  "rooms" : {
                     "PippoSdentato": {},
                     "PippoSdentato2": {},
                     "R023": {}
                  }
               }
            ]
          }
      }

      # usato come parametro di comparazione per il successo dell'esecuzione
      # rappresenta ciò che ce ne aspettiamo alla fine dell'update su entrambe
      # sorgenti dati: edilizia e easyroom
      self.final_rooms = {
         # Room 1, matcha con easyroom
         "R003": {
            "texts": [
               { "text": "StanzaMatchata" },
               { "text": "R003" },
               { "text": "AUL01" }
            ]
         },
         # Room 3, matcha con edilizia
         "R002": {
            "texts": [
               { "text": "AUL03" },
               { "text": "StanzaMatchata" },
               { "text": "R002" }
            ]
         },
         # Room 1, matcha con easyroom
         "R023" : {
            "texts": [
               { "text": "StanzaMatchata" },
               { "text": "R023" },
               { "text": "AUL01" }
            ]
         },
         # Room 3, matcha con edilizia
         "R022" : {
            "texts": [
               { "text": "AUL03" },
               { "text": "StanzaMatchata" },
               { "text": "R022" }
            ]
         }
      }
      self.building     = Building(self.db_building)

      self.room_categories = [
         RoomCategory({
            "_id": "AUL01",
            "cat_name": "Aula"
         }),
         RoomCategory({
            "_id": "AUL03",
            "cat_name": "Aula Informatica"
         }),
         RoomCategory({
            "_id": "WC01",
            "cat_name": "Bagno"
         })
      ]

   def test_resolve_rooms_id_floor_by_floor_edilizia(self):
      """Test r_id resolving with edilizia data, one floor at a time"""


      floor = self.db_building["dxf"]["floors"][0]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "edilizia"
      )

      self.assertEqual(floor["rooms"]["R002"], self.final_rooms["R002"])


      floor = self.db_building["dxf"]["floors"][1]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "edilizia"
      )

      self.assertEqual(floor["rooms"]["R022"], self.final_rooms["R022"])
      self.assertTrue("R023" not in floor["rooms"])
      self.assertTrue("R003" not in floor["rooms"])

   def test_resolve_rooms_id_floor_by_floor_easyroom(self):
      """Test r_id resolving with easyroom data, one floor at a time"""

      floor = self.db_building["dxf"]["floors"][0]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "easyroom"
      )

      self.assertEqual(floor["rooms"]["R003"], self.final_rooms["R003"])


      floor = self.db_building["dxf"]["floors"][1]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "easyroom"
      )

      self.assertEqual(floor["rooms"]["R023"], self.final_rooms["R023"])
      self.assertTrue("R022" not in floor["rooms"])
      self.assertTrue("R002" not in floor["rooms"])


   def test_resolve_rooms_id_all_at_once(self):
      """Test r_id resolving with all sources and for all floors"""

      floor_0 = self.db_building["dxf"]["floors"][0]
      floor_1 = self.db_building["dxf"]["floors"][1]
      room_00 = floor_0["unidentified_rooms"][0]
      room_02 = floor_0["unidentified_rooms"][2]
      room_10 = floor_1["unidentified_rooms"][0]
      room_12 = floor_1["unidentified_rooms"][2]

      DXFDataUpdater.resolve_rooms_id(
         self.building,
         None,
         None
      )

      self.assertEqual(floor_1["rooms"]["R023"], self.final_rooms["R023"])
      self.assertEqual(floor_1["rooms"]["R022"], self.final_rooms["R022"])
      self.assertEqual(floor_0["rooms"]["R002"], self.final_rooms["R002"])
      self.assertEqual(floor_0["rooms"]["R003"], self.final_rooms["R003"])
      self.assertTrue(room_00 not in floor_0["unidentified_rooms"])
      self.assertTrue(room_02 not in floor_0["unidentified_rooms"])
      self.assertTrue(room_10 not in floor_1["unidentified_rooms"])
      self.assertTrue(room_12 not in floor_1["unidentified_rooms"])


   def test_resolve_room_categories(self):

      RoomCategory.where = MagicMock(return_value= self.room_categories)

      # Richiamo resolve_rooms_id per testare che le category vengano matchate
      # sia sul dizionario rooms sia sulla lista uniidentified_rooms
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         None,
         None
      )

      DXFDataUpdater.resolve_room_categories(self.building, None)

      floor_0 = self.db_building["dxf"]["floors"][0]
      floor_1 = self.db_building["dxf"]["floors"][1]

      self.assertEqual(floor_1["rooms"]["R023"]["cat_name"], "Aula")
      self.assertEqual(floor_1["rooms"]["R022"]["cat_name"], "Aula Informatica")
      self.assertEqual(floor_1["unidentified_rooms"][0]["cat_name"], "Bagno")
      self.assertEqual(floor_0["rooms"]["R002"]["cat_name"], "Aula Informatica")
      self.assertEqual(floor_0["rooms"]["R003"]["cat_name"], "Aula")
      self.assertEqual(floor_0["unidentified_rooms"][0]["cat_name"], "Bagno")
