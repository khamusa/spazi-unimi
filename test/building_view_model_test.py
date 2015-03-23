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
                          "cat_name"      : "Aula Informatica"
                      }
                  },
                  "f_id"               : "-05",
                  "walls"              : [],
                  "windows"            : [],
                  "unidentified_rooms" : [
                     {
                        "cat_name"  : "WC",
                        "polygon"   : {}
                     },
                     {
                        "cat_name"  : "WC",
                        "polygon"   : {}
                     },
                     {
                        "cat_name"  : "Ufficio",
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
                          "cat_name"      : "Aula"
                      },
                      "R107" : {
                          "capacity"      : "12",
                          "equipments"    : [],
                          "polygon"       : {},
                          "room_name"     : "Aula 6",
                          "accessibility" : "",
                          "cat_name"      : "Aula"
                      },
                      "R013" : {
                          "capacity"      : "26",
                          "equipments"    : [],
                          "polygon"       : {},
                          "room_name"     : "Aula Delta",
                          "accessibility" : "",
                          "cat_name"      : "Aula Informatica"
                      },
                  },
                  "f_id"               : "03",
                  "walls"              : [],
                  "windows"            : [],
                  "unidentified_rooms" : [
                     {
                        "cat_name"  : "WC",
                        "polygon"   : {}
                     },
                     {
                        "cat_name"  : "Studio",
                        "polygon"   : {}
                     },
                     {
                        "cat_name"  : "Ufficio",
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
                        "cat_name"  : "Aula Informatica"
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
                        "cat_name"  : "Aula"
                     },
                     "R008" : {
                        "capacity"  : "208",
                        "room_name" : "Aula Sigma e Omega",
                        "l_floor"   : "R",
                        "cat_name"  : "Aula Informatica"
                     },
                     "R013" : {
                        "capacity"  : "26",
                        "room_name" : "Aula Delta",
                        "l_floor"   : "R",
                        "cat_name"  : "Aula Informatica"
                     },
                     "R100" : {
                        "capacity"  : "12",
                        "room_name" : "Aula 4",
                        "l_floor"   : "R",
                        "cat_name"  : "Aula"
                     },
                     "R048" : {
                        "capacity"  : "192",
                        "room_name" : "Aula Beta",
                        "l_floor"   : "R",
                        "cat_name"  : "Aula"
                     },
                     "R099" : {
                        "capacity"  : "16",
                        "room_name" : "Aula 5",
                        "l_floor"   : "R",
                        "cat_name"  : "Aula"
                     },
                     "R107" : {
                        "capacity"  : "12",
                        "room_name" : "Aula 6",
                        "l_floor"   : "R",
                        "cat_name"  : "Aula"
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

      merged_floors = (f["f_id"] for f in b.get_path("merged.floors"))

      for f_id in merged_floors:
         self.assertTrue(f_id in b_view.get("floors").keys())
         self.assertTrue("rooms" in b_view["floors"][f_id])
         self.assertTrue("floor_name" in b_view["floors"][f_id])
         self.assertEqual(
            b_view["floors"][f_id]["floor_name"],
            self.floor_dict[f_id]["floor_name"]
         )

         for room in b_view["floors"][f_id]["rooms"].values():
            self.assertTrue("polygon" not in room)
            self.assertTrue("capacity" in room)
            self.assertTrue("equipments" in room)
            self.assertTrue("room_name" in room)
            self.assertTrue("cat_name" in room)

         self.assertIn("available_services", b_view["floors"][f_id])

      available_services_1 = b_view["floors"]["-05"]["available_services"]
      available_services_2 = b_view["floors"]["03"]["available_services"]

      self.assertIn("WC", available_services_1)
      self.assertIn("Ufficio", available_services_1)
      self.assertIn("WC", available_services_2)
      self.assertIn("Studio", available_services_2)
      self.assertIn("Ufficio", available_services_2)

