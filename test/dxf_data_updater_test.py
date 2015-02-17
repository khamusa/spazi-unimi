from mock                        import MagicMock
from tasks.dxf_data_updater      import DXFDataUpdater
from model                       import Building
import unittest

class DXFDataUpdaterTest(unittest.TestCase):
   def setUp(self):
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
                  "rooms" : [
                     { "r_id": "PippoPelato" },
                     { "r_id": "R002" },
                     { "r_id": "PippoPelato2" }

                  ]
               },
               {
                  "f_id"  : "0.5",
                  "rooms" : [
                     { "r_id": "PippoPelato" },
                     { "r_id": "PippoPelato2" },
                     { "r_id": "R022" }

                  ]
               }
            ]
          },
          "easyroom" : {
            "floors": [
               {
                  "f_id"  : "0",
                  "rooms" : [
                     { "r_id": "PippoSdentato" },
                     { "r_id": "PippoSdentato2" },
                     { "r_id": "R003" }
                  ]
               },
               {
                  "f_id"  : "1",
                  "rooms" : [
                     { "r_id": "PippoSdentato" },
                     { "r_id": "PippoSdentato2" },
                     { "r_id": "R023" }
                  ]
               }
            ]
          }
      }

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

      self.dxf_updater  = DXFDataUpdater()
      self.building     = Building(self.db_building)

   def test_resolve_rooms_id_floor_by_floor_edilizia(self):
      """Test resolving with edilizia data, one floor at a time"""

      floor = self.db_building["dxf"]["floors"][0]
      self.dxf_updater.resolve_rooms_id(
         self.building,
         floor,
         "edilizia"
      )

      self.assertEqual(floor["rooms"][2], self.final_rooms[0][2])


      floor = self.db_building["dxf"]["floors"][1]
      self.dxf_updater.resolve_rooms_id(
         self.building,
         floor,
         "edilizia"
      )

      self.assertEqual(floor["rooms"][2], self.final_rooms[1][2])


   def test_resolve_rooms_id_floor_by_floor_easyroom(self):
      """Test resolving with easyroom data, one floor at a time"""

      floor = self.db_building["dxf"]["floors"][0]
      self.dxf_updater.resolve_rooms_id(
         self.building,
         floor,
         "easyroom"
      )

      self.assertEqual(floor["rooms"][0], self.final_rooms[0][0])


      floor = self.db_building["dxf"]["floors"][1]
      self.dxf_updater.resolve_rooms_id(
         self.building,
         floor,
         "easyroom"
      )

      self.assertEqual(floor["rooms"][0], self.final_rooms[1][0])

   def test_resolve_rooms_id_all_at_once(self):
      """Test resolving with all sources and for all floors"""

      self.dxf_updater.resolve_rooms_id(
         self.building,
         None,
         None
      )

      f0_rooms = self.db_building["dxf"]["floors"][0]["rooms"]
      f1_rooms = self.db_building["dxf"]["floors"][1]["rooms"]
      self.assertEqual(f0_rooms, self.final_rooms[0])
      self.assertEqual(f1_rooms, self.final_rooms[1])

