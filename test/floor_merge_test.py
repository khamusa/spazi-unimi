import unittest
from tasks.data_merger import DataMerger

class FloorMergeTest(unittest.TestCase):
   def test_floor_copy(self):
      floor       = {
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
