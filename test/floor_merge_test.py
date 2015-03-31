from tasks.mergers import DataMerger
from mock          import MagicMock
import unittest

class FloorMergeTest(unittest.TestCase):
   def setUp(self):
      self.floor = {
            "f_id"  : "1",
            "rooms" : {
               "R001" : {
                  "polygon"      : {},
                  "pippo"        : False,
                  "cat_id"       : "AUL01",
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
                  "cat_id"       : "AUL03",
                  "pluto"        : [],
                  "texts"        : []
               }
            ]
         }

   def test_match_and_merge_floors_returns_copy(self):
      base_floors = [self.floor, self.floor]

      merged_floors = DataMerger._match_and_merge_floors(base_floors, [])

      self.assertFalse(merged_floors is base_floors)
      self.assertFalse(merged_floors[0] is base_floors[0])
      self.assertFalse(merged_floors[1] is base_floors[1])

   def test_match_and_merge_floors_calls_match_and_merge_a_floor(self):
      # call arguments
      base_floors                = [self.floor, self.floor]
      unmatched_floors           = [MagicMock(), MagicMock(), MagicMock()]

      # Mock the method to be called
      old_method                 = DataMerger._match_and_merge_a_floor
      method_mock                = MagicMock(return_value=[])
      DataMerger._match_and_merge_a_floor = method_mock

      # Call the main method
      merged_floors = DataMerger._match_and_merge_floors(
         base_floors,
         unmatched_floors
      )

      # Ensure sub-method has been called
      self.assertEqual(method_mock.call_count, 3)
      self.assertEqual(method_mock.call_args_list[0][0][1], unmatched_floors[0])
      self.assertEqual(method_mock.call_args_list[1][0][1], unmatched_floors[1])
      self.assertEqual(method_mock.call_args_list[2][0][1], unmatched_floors[2])

      # Teardown, resetting original tested method
      DataMerger._match_and_merge_a_floor = old_method

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
      self.assertEqual(room1["cat_id"], copy_room1["cat_id"])
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
      self.assertEqual(unidentified1["cat_id"], unidentified_copy1["cat_id"])
      self.assertTrue("pippo" not in unidentified_copy1)
      self.assertTrue("pluto" not in unidentified_copy1)

   def test_match_and_merge_a_floor(self):
      base_floors = [
         {
            "room_ids"  : set(["R001", "R002", "R003"])
         },
         {
            "room_ids"  : set(["1001", "1002", "1003"])
         },
         {
            "room_ids"  : set(["2001", "2002", "2003"])
         }
      ]
      unmatched_floor = {
         "room_ids" : set(["R001", "R002", "R003", "1003", "2001", "2002", "R401"])
      }

      old_merge_room_method              = DataMerger._merge_rooms_into_floor
      DataMerger._merge_rooms_into_floor = MagicMock()

      mapping = DataMerger._match_and_merge_a_floor(base_floors, unmatched_floor)

      # verifico la correttezza del mapping restituito
      self.assertEqual(mapping[0], (set(["R001", "R002", "R003"]), base_floors[0]) )
      self.assertEqual(mapping[1], (set(["2001", "2002"]),         base_floors[2]) )
      self.assertEqual(mapping[2], (set(["1003"]),                 base_floors[1]) )

      # Controllo che il set di unmatched floor contenga solo la stanza che non
      # viene matchata
      self.assertEqual(unmatched_floor["room_ids"], set(["R401"]))

      # Controllo che merge_rooms_into_floor sia chiamato tre volte e che
      # l'ultimo parametro passato sia sempre il set di r_id matchati
      self.assertEqual(DataMerger._merge_rooms_into_floor.call_count, 3)

      merge_rooms_args = DataMerger._merge_rooms_into_floor.call_args_list
      self.assertEqual(merge_rooms_args[0][0][2], set(["R001", "R002", "R003"]))
      self.assertEqual(merge_rooms_args[1][0][2], set(["1003"]))
      self.assertEqual(merge_rooms_args[2][0][2], set(["2001", "2002"]))

      DataMerger._merge_rooms_into_floor = old_merge_room_method

   def test_merge_specified_rooms_from_two_floors_into_one(self):
      base_floor                    = self.floor
      base_floor["rooms"]["R002"]   = {}
      unmatched_floor   = {
         "f_id"  : "333",
         "rooms" : {
            "R001" : {
               "cat_id"     : "Pippo",
               "room_name"    : "Aula 777"
            },
            "R002" : {
               "cat_id"     : "Aula Nuova",
               "capacity"     : "22"
            },
            "R003" : {}
         }
      }

      old_r01 = base_floor["rooms"]["R001"]
      old_r02 = base_floor["rooms"]["R002"]

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

      self.assertFalse(r01 is old_r01)
      self.assertFalse(r02 is old_r02)

      # Ensure priority has been kept on a per-attribute basis
      cat_id = unmatched_floor["rooms"]["R001"]["cat_id"]
      self.assertEqual(r01["cat_id"], cat_id)
      self.assertEqual(r01["room_name"], old_r01["room_name"])
      self.assertEqual(r02["cat_id"], "Aula Nuova")
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
         "cat_id"     : "AUL02",
         "polygon"      : {
            "anchor_point" : [],
            "points"       : []
         },
         "texts"        : []
      }

      edil_room = {
         "room_name"    : "Aula 01 ed",
         "capacity"     : "44",
         "cat_id"       : "AUL01",
         "l_floor"      :"T"
      }

      easy_room = {
         "room_name"    : "Aula 01 easy",
         "cat_id"       : "AUL03",
         "capacity"     : "45",
         "accessibility": True,
         "equipments"   : "PC/Lavagna/Wi-fi",
         "l_floor"      : "T"
      }

      # Test del merge di una stanza dxf e di un edilizia
      result = DataMerger.merge_room(dxf_room, {})

      self.assertEqual(result["room_name"], "")
      self.assertEqual(result["capacity"], "")
      self.assertEqual(result["cat_id"], dxf_room["cat_id"])
      self.assertEqual(result["accessibility"], "")
      self.assertEqual(result["equipments"], [])
      self.assertEqual(result["polygon"], dxf_room["polygon"])
      self.assertFalse("texts" in result)
      self.assertFalse("l_floor" in result)

      # Test del merge di una stanza dxf e di un edilizia
      result = DataMerger.merge_room(dxf_room, edil_room)

      self.assertEqual(result["room_name"], edil_room["room_name"])
      self.assertEqual(result["capacity"], edil_room["capacity"])
      self.assertEqual(result["cat_id"], "AUL01")
      self.assertEqual(result["accessibility"], "")
      self.assertEqual(result["equipments"], [])
      self.assertEqual(result["polygon"], dxf_room["polygon"])
      self.assertFalse("texts" in result)
      self.assertFalse("l_floor" in result)

      # Test del merge di una stanza dxf e di un easyroom
      result = DataMerger.merge_room(dxf_room, easy_room)

      self.assertEqual(result["room_name"], easy_room["room_name"])
      self.assertEqual(result["capacity"], easy_room["capacity"])
      self.assertEqual(result["cat_id"], "AUL03")
      self.assertEqual(result["accessibility"], easy_room["accessibility"])
      self.assertEqual(result["equipments"], easy_room["equipments"].split("/"))
      self.assertEqual(result["polygon"], dxf_room["polygon"])
      self.assertFalse("texts" in result)
      self.assertFalse("l_floor" in result)

      # Test del merge di una stanza edilizia e di un easyroom
      result = DataMerger.merge_room(edil_room, easy_room)

      self.assertEqual(result["room_name"], edil_room["room_name"])
      self.assertEqual(result["capacity"], edil_room["capacity"])
      self.assertEqual(result["cat_id"], "AUL03")
      self.assertEqual(result["accessibility"], easy_room["accessibility"])
      self.assertEqual(result["equipments"], easy_room["equipments"].split("/"))
      self.assertFalse("polygon" in result)
      self.assertFalse("texts" in result)
      self.assertFalse("l_floor" in result)
