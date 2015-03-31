import unittest, json
from model import Building, BuildingView

class BuildingViewModelTest(unittest.TestCase):
   def setUp(self):
      config_file = "config/floor_inference.json"
      with open(config_file) as cf:
         self.floor_dict = json.load(cf)

      self.db_building  ={
         "_id"    : "33110",
         "merged" : {
            "floors" : [
               {
                  "rooms" : {
                      "S015" : {
                          "capacity"      : "20",
                          "equipments"    : [],
                          "polygon"       : {},
                          "room_name"     : "Aula Gamma",
                          "accessibility" : "",
                          "cat_id"        : "AUL03"
                      }
                  },
                  "f_id"               : "-05",
                  "walls"              : [],
                  "windows"            : [],
                  "unidentified_rooms" : [
                     {
                        "cat_id"    : "WC01",
                        "polygon"   : {}
                     },
                     {
                        "cat_id"    : "WC01",
                        "polygon"   : {}
                     },
                     {
                        "cat_id"    : "UFF01",
                        "polygon"   : {}
                     }
                  ]
              },
              {
                  "rooms" : {
                      "R057" : {
                          "capacity"      : "128",
                          "equipments"    : [],
                          "polygon"       : {},
                          "room_name"     : "Aula Alfa",
                          "accessibility" : "",
                          "cat_id"        : "AUL01"
                      },
                      "R107" : {
                          "capacity"      : "12",
                          "equipments"    : [],
                          "polygon"       : {},
                          "room_name"     : "Aula 6",
                          "accessibility" : "",
                          "cat_id"        : "AUL01"
                      },
                      "R013" : {
                          "capacity"      : "26",
                          "equipments"    : [],
                          "polygon"       : {},
                          "room_name"     : "Aula Delta",
                          "accessibility" : "",
                          "cat_id"        : "AUL03"
                      },
                  },
                  "f_id"               : "03",
                  "walls"              : [],
                  "windows"            : [],
                  "unidentified_rooms" : [
                     {
                        "cat_id"    : "WC01",
                        "polygon"   : {}
                     },
                     {
                        "cat_id"    : "STD01",
                        "polygon"   : {}
                     },
                     {
                        "cat_id"    : "UFF01",
                        "polygon"   : {}
                     }
                  ]
              },
            ],
            "building_name"   : "",
            "coordinates"     : {
              "coordinates"      : [ 9.214915, 45.454309],
              "type"             : "Point"
            },
            "l_b_id"          : "5830",
            "address"         : "Via Comelico, 39, Milano",
            "building_number" : "1"
         },
         "edilizia"  :{
            "lat"          : "45.454309",
            "lon"          : "9.214915",
            "updated_at"   : "",
            "floors" : [
               {
                  "rooms" : {
                     "S015" : {
                        "capacity"  : "20",
                        "room_name" : "Aula Gamma",
                        "l_floor"   : "S",
                        "cat_id"    : "AUL03"
                     }
                  },
                  "f_id" : "-05"
               },
               {
                  "rooms" : {
                     "R057" : {
                        "capacity"  : "128",
                        "room_name" : "Aula Alfa",
                        "l_floor"   : "R",
                        "cat_id"    : "AUL01"
                     },
                     "R008" : {
                        "capacity"  : "208",
                        "room_name" : "Aula Sigma e Omega",
                        "l_floor"   : "R",
                        "cat_id"    : "AUL03"
                     },
                     "R013" : {
                        "capacity"  : "26",
                        "room_name" : "Aula Delta",
                        "l_floor"   : "R",
                        "cat_id"    : "AUL03"
                     },
                     "R100" : {
                        "capacity"  : "12",
                        "room_name" : "Aula 4",
                        "l_floor"   : "R",
                        "cat_id"    : "AUL01"
                     },
                     "R048" : {
                        "capacity"  : "192",
                        "room_name" : "Aula Beta",
                        "l_floor"   : "R",
                        "cat_id"    : "AUL01"
                     },
                     "R099" : {
                        "capacity"  : "16",
                        "room_name" : "Aula 5",
                        "l_floor"   : "R",
                        "cat_id"    : "AUL01"
                     },
                     "R107" : {
                        "capacity"  : "12",
                        "room_name" : "Aula 6",
                        "l_floor"   : "R",
                        "cat_id"    : "AUL01"
                     }
                  },
               "f_id" : "03"
            }
         ],
         "b_id"      : "33110",
         "l_b_id"    : "5830",
         "address"   : "Milano - Via Comelico 39_Ed 1"
         }
      }

      self.building = Building(self.db_building)

   def test_create_from_building(self):
      b        = self.building
      b_view   = BuildingView.create_from_building(b)

      self.assertEqual(b_view.get_path("_id"), b.get_path("_id"))

      identic_keys = [
         "address", "building_number", "coordinates", "building_name", "l_b_id"
      ]
      for attr in identic_keys:
         self.assertEqual(b_view.get_path(attr), b.get_path("merged." + attr))

      for i, floor in enumerate(b_view.get_path("floors")):
         self.assertIn("rooms", floor)
         self.assertIn("floor_name", floor)

         self.assertEqual(
            floor["floor_name"],
            self.floor_dict[floor["f_id"]]["floor_name"]
         )

         for room in floor["rooms"].values():
            self.assertTrue("polygon" not in room)
            self.assertTrue("capacity" in room)
            self.assertTrue("equipments" in room)
            self.assertTrue("room_name" in room)
            self.assertTrue("cat_name" in room)
            self.assertTrue("cat_id" not in room)

         self.assertIn("available_services", floor)

      available_services_1 = b_view["floors"][0]["available_services"]
      available_services_2 = b_view["floors"][1]["available_services"]

      self.assertIn("Bagno", available_services_1)
      self.assertIn("Ufficio", available_services_1)
      self.assertIn("Bagno", available_services_2)
      self.assertIn("Studio", available_services_2)
      self.assertIn("Ufficio", available_services_2)

