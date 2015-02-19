from mock                        import MagicMock
from tasks.dxf_data_updater      import DXFDataUpdater
from model                       import Building
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
               "rooms" : [
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
               "rooms" : [
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
      self.final_rooms = [
         [
            { # Room 1, matcha con easyroom
               "r_id" : "R003",
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
               "r_id" : "R002",
               "texts": [
                  { "text": "AUL03" },
                  { "text": "StanzaMatchata" },
                  { "text": "R002" }
               ]
            }
         ],

         [
            { # Room 1, matcha con easyroom
               "r_id" : "R023",
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
               "r_id" : "R022",
               "texts": [
                  { "text": "AUL03" },
                  { "text": "StanzaMatchata" },
                  { "text": "R022" }
               ]
            }
         ]
      ]
      self.building     = Building(self.db_building)

   def test_resolve_rooms_id_floor_by_floor_edilizia(self):
      """Test r_id resolving with edilizia data, one floor at a time"""


      floor = self.db_building["dxf"]["floors"][0]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "edilizia"
      )

      self.assertEqual(floor["rooms"][2], self.final_rooms[0][2])


      floor = self.db_building["dxf"]["floors"][1]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "edilizia"
      )

      self.assertEqual(floor["rooms"][2], self.final_rooms[1][2])
      self.assertNotEqual(floor["rooms"][0], self.final_rooms[0][0])
      self.assertNotEqual(floor["rooms"][0], self.final_rooms[1][0])

   def test_resolve_rooms_id_floor_by_floor_easyroom(self):
      """Test r_id resolving with easyroom data, one floor at a time"""

      floor = self.db_building["dxf"]["floors"][0]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "easyroom"
      )

      self.assertEqual(floor["rooms"][0], self.final_rooms[0][0])


      floor = self.db_building["dxf"]["floors"][1]
      DXFDataUpdater.resolve_rooms_id(
         self.building,
         floor,
         "easyroom"
      )

      self.assertEqual(floor["rooms"][0], self.final_rooms[1][0])
      self.assertNotEqual(floor["rooms"][2], self.final_rooms[0][2])
      self.assertNotEqual(floor["rooms"][2], self.final_rooms[1][2])

   def test_resolve_rooms_id_all_at_once(self):
      """Test r_id resolving with all sources and for all floors"""

      DXFDataUpdater.resolve_rooms_id(
         self.building,
         None,
         None
      )

      f0_rooms = self.db_building["dxf"]["floors"][0]["rooms"]
      f1_rooms = self.db_building["dxf"]["floors"][1]["rooms"]
      self.assertEqual(f0_rooms, self.final_rooms[0])
      self.assertEqual(f1_rooms, self.final_rooms[1])

