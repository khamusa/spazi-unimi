from persistence.db      import MongoDBPersistenceManager
from model.odm           import ODMModel
from model.building      import Building
from itertools           import chain
from tasks.data_updaters import EasyroomDataUpdater, EdiliziaDataUpdater
import unittest

class RoomDataUpdaterTest(unittest.TestCase):

   def setUp(self):
      pm = MongoDBPersistenceManager({
         "db": {
               "url"     : "localhost",
               "port"    : 27017,
               "db_name" : "campus_unimi_test"
            }
      })

      ODMModel.set_pm(pm)

      self.edil_rooms = [
         {
            'room_name' : 'Aula Seminari',
            'cat_name'  : 'Aula',
            'r_id'      : 'T-065',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : 'T'
         },
         {
            'room_name' : 'Aula Pippo',
            'cat_name'  : 'Aula',
            'r_id'      : 'T066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : 'T'
         },
         {
            'room_name' : 'Aula Pippo Sdentato',
            'cat_name'  : 'Aula',
            'r_id'      : '1066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '1'
         }
      ]

      self.easy_rooms = [
         {
            'room_name' : 'Aula Seminari',
            'cat_name'  : 'Aula',
            'r_id'      : '21030#T-065',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '0'
         },
         {
            'room_name' : 'Aula Pippo',
            'cat_name'  : 'Aula',
            'r_id'      : '21030#T066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '0'
         },
         {
            'room_name' : 'Aula Pippo Sdentato',
            'cat_name'  : 'Aula',
            'r_id'      : '21030#1066',
            'b_id'      : '21030',
            'capacity'  : '52',
            'l_floor'   : '10'
         }
      ]

      pm.clean_collection("building")
      self.edil_up      = EdiliziaDataUpdater()
      self.easy_up      = EasyroomDataUpdater()
      Building.__str__  = lambda x: ""

   def retrieve_test_building(self):
      b = Building.find( "21030" )
      return b

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
      self.assertEqual(second_floor["f_id"], "10")

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
