import unittest
from tasks.data_merger  import DataMerger
from mock               import MagicMock

class FloorMergeTest(unittest.TestCase):
   def setUp(self):
      self.floor = {
            "f_id"  : "1",
            "rooms" : {
               "R001" : {
                  "polygon"      : {},
                  "pippo"        : False,
                  "cat_name"     : "Aula",
                  "room_name"    : "Aula 01",
                  "pluto"        : [],
                  "equipments"   : [],
                  "accessibility": True,
                  "capacity"     : "22"
               }
            },
            "unidentified_rooms" : [
               {
                  "polygon"      : {},
                  "pippo"        : False,
                  "cat_name"     : "Aula Seminari",
                  "pluto"        : [],
                  "texts"        : []
               }
            ]
         }

   def test_floor_copy(self):
      floor = self.floor
      copy_floor  = DataMerger._floor_copy(floor)

      # Il floor restituito deve essere una copia e avere stesso f_id
      self.assertFalse(floor is copy_floor)
      self.assertEqual(floor["f_id"], copy_floor["f_id"])

      # Le stanze devono essere copie e i valori dei campi non filtrati devono
      # corrispondere
      room1       = floor["rooms"]["R001"]
      copy_room1  = copy_floor["rooms"]["R001"]
      self.assertFalse(room1 is copy_room1)
      self.assertEqual(room1["polygon"], copy_room1["polygon"])
      self.assertEqual(room1["cat_name"], copy_room1["cat_name"])
      self.assertEqual(room1["room_name"], copy_room1["room_name"])
      self.assertEqual(room1["equipments"], copy_room1["equipments"])
      self.assertEqual(room1["accessibility"], copy_room1["accessibility"])
      self.assertEqual(room1["capacity"], copy_room1["capacity"])
      self.assertTrue("pippo" not in copy_room1)
      self.assertTrue("pluto" not in copy_room1)

      # Le stanze non matchate devono essere copie e contenere i campi non
      # filtrati con i valori corrispondenti
      unidentified1       = floor["unidentified_rooms"][0]
      unidentified_copy1  = copy_floor["unidentified_rooms"][0]
      self.assertFalse(unidentified1 is unidentified_copy1)
      self.assertEqual(unidentified1["polygon"], unidentified_copy1["polygon"])
      self.assertEqual(unidentified1["cat_name"], unidentified_copy1["cat_name"])
      self.assertTrue("pippo" not in unidentified_copy1)
      self.assertTrue("pluto" not in unidentified_copy1)


   def test_merge_specified_rooms_from_two_floors_into_one(self):
      base_floor                    = self.floor
      base_floor["rooms"]["R002"]   = {}
      unmatched_floor   = {
         "f_id"  : "333",
         "rooms" : {
            "R001" : {
               "cat_name"     : "Pippo",
               "room_name"    : "Aula 777"
            },
            "R002" : {
               "cat_name"     : "Aula Nuova",
               "capacity"     : "22"
            },
            "R003" : {}
         }
      }
      DataMerger._merge_rooms_into_floor(
         base_floor,
         unmatched_floor,
         set(["R001", "R002"])
      )
      self.assertEqual(base_floor["f_id"], "1")
      self.assertTrue("R001" in base_floor["rooms"])
      self.assertTrue("R002" in base_floor["rooms"])
      self.assertFalse("R003" in base_floor["rooms"])

      r01 = base_floor["rooms"]["R001"]
      r02 = base_floor["rooms"]["R002"]

      # Ensure priority has been kept on a per-attribute basis
      self.assertEqual(r01["cat_name"], "Aula")
      self.assertEqual(r01["room_name"], "Aula 01")
      self.assertEqual(r02["cat_name"], "Aula Nuova")
      self.assertEqual(r02["capacity"], "22")

      old_merge_room_method = DataMerger.merge_room
      DataMerger.merge_room = MagicMock()
      DataMerger._merge_rooms_into_floor(
         base_floor,
         unmatched_floor,
         set(["R001", "R002"])
      )

      self.assertEqual(DataMerger.merge_room.call_count, 2)
      DataMerger.merge_room = old_merge_room_method

   def test_merge_room(self):

      dxf_room = {
         "cat_name"     : "Aula",
         "polygon"      : {
            "anchor_point" : [],
            "points"       : []
         },
         "texts"        : []
      }

      edil_room = {
         "room_name"    : "Aula 01 ed",
         "capacity"     : "44",
         "cat_name"     : "Aula Edil",
         "l_floor"      :"T"
      }

      easy_room = {
         "room_name"    : "Aula 01 easy",
         "capacity"     : "45",
         "accessibility": True,
         "equipments"   : "PC/Lavagna/Wi-fi",
         "l_floor"      : "T"
      }

      # Test del merge di una stanza dxf e di un edilizia
      result = DataMerger.merge_room(dxf_room, edil_room)

      self.assertEqual(result["room_name"], edil_room["room_name"])
      self.assertEqual(result["capacity"], edil_room["capacity"])
      self.assertEqual(result["cat_name"], dxf_room["cat_name"])
      self.assertEqual(result["accessibility"], "")
      self.assertEqual(result["equipments"], [])
      self.assertEqual(result["polygon"], dxf_room["polygon"])
      self.assertFalse("texts" in result)
      self.assertFalse("l_floor" in result)

      # Test del merge di una stanza dxf e di un easyroom
      result = DataMerger.merge_room(dxf_room, easy_room)

      self.assertEqual(result["room_name"], easy_room["room_name"])
      self.assertEqual(result["capacity"], easy_room["capacity"])
      self.assertEqual(result["cat_name"], dxf_room["cat_name"])
      self.assertEqual(result["accessibility"], easy_room["accessibility"])
      self.assertEqual(result["equipments"], easy_room["equipments"].split("/"))
      self.assertEqual(result["polygon"], dxf_room["polygon"])
      self.assertFalse("texts" in result)
      self.assertFalse("l_floor" in result)

      # Test del merge di una stanza edilizia e di un easyroom
      result = DataMerger.merge_room(edil_room, easy_room)

      self.assertEqual(result["room_name"], edil_room["room_name"])
      self.assertEqual(result["capacity"], edil_room["capacity"])
      self.assertEqual(result["cat_name"], edil_room["cat_name"])
      self.assertEqual(result["accessibility"], easy_room["accessibility"])
      self.assertEqual(result["equipments"], easy_room["equipments"].split("/"))
      self.assertFalse("polygon" in result)
      self.assertFalse("texts" in result)
      self.assertFalse("l_floor" in result)
