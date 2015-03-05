from mock                              import MagicMock, patch
from tasks.dxf_room_cats_resolver      import DXFRoomCatsResolver
from model                             import Building, RoomCategory
import unittest

class DXFRoomCatsResolverTest(unittest.TestCase):
   """
   Test the room merging procedures of DXFRoomCatsResolver, i.e, the ability of
   associating DXF rooms with other souces rooms.
   """
   def setUp(self):

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

      self.room_cats_where_mock = MagicMock(return_value= self.room_categories)

      with patch("__main__.RoomCategory.where", self.room_cats_where_mock):
         self.cats        = DXFRoomCatsResolver.get_room_categories_dict()
         self.cats_names  = DXFRoomCatsResolver.get_room_categories_names_dict(self.cats)

   def generate_rooms_with_text(self, t):
      """
      Auxiliary test method, generates a list of rooms containing the supplied
      text
      """
      r1 = {
         "texts": [
            { "text" : "R002"},
            { "text" : " "+t+" " },
            { "text" : "0,00"},
            { "text" : "sporcizia a caso" }
         ]
      }

      r2 = {
         "texts": [
            { "text" : "R003"},
            { "text" : "0,00"},
            { "text" : "sporcizia a caso" },
            { "text" : " "+t }
         ]
      }

      r3 = {
         "texts": [
            { "text" : t+" " },
            { "text" : "R003"},
            { "text" : "0,00"},
            { "text" : "sporcizia a caso" }
         ]
      }
      return [r1, r2, r3]


   ###################################################
   # Tests for resolve_room_categories (entry point) #
   ###################################################
   def test_resolve_room_categories(self):
      a_floor = MagicMock()

      should_be_called  = MagicMock(return_value = True)
      cats              = MagicMock(return_value = "cats_result")
      cats_names        = MagicMock(return_value = "cats_names")
      class_ns          = "__main__.DXFRoomCatsResolver"

      with patch(class_ns+".get_room_categories_dict", cats):
         with patch(class_ns+".get_room_categories_names_dict", cats_names):
            with patch(class_ns+"._resolve_room_categories_for_floor", should_be_called):
               # Chiamata 1 - un solo floor, passato come parametro
               r = DXFRoomCatsResolver.resolve_room_categories(MagicMock(), a_floor)

               self.assertEqual(r, 1)
               MagicMock.assert_called_once_with(cats)
               MagicMock.assert_called_once_with(cats_names, "cats_result")

               MagicMock.assert_called_once_with(
                  should_be_called,
                  a_floor,
                  "cats_result",
                  "cats_names"
               )

               MagicMock.reset_mock(should_be_called)
               b = {
                  "dxf": { "floors": ["firstfloor", "secondfloor", "thirdfloor"] }
               }
               r = DXFRoomCatsResolver.resolve_room_categories(b)

               for f in b["dxf"]["floors"]:
                  MagicMock.assert_any_call(
                     should_be_called,
                     f,
                     "cats_result",
                     "cats_names"
               )

               self.assertEqual(r, 3)

   ######################################
   # _resolve_room_categories_for_floor #
   ######################################
   def test_resolve_room_categories_for_floor(self):
      floor_dict = {
               "rooms" : { "a": "A", "b": "B", "c": "C" },
               "unidentified_rooms" : [1, 2, 3, 4]
            }

      should_be_called = MagicMock(return_value = 4)
      chain_mock       = MagicMock(return_value = [1, 2, 3, 4, "A", "B", "C"])

      with patch("tasks.dxf_room_cats_resolver.chain", chain_mock):
         with patch("__main__.DXFRoomCatsResolver._resolve_categories_for_rooms", should_be_called):

            r = DXFRoomCatsResolver._resolve_room_categories_for_floor(
               floor_dict,
               "cats",
               "cats_names"
            )

            MagicMock.assert_called_once_with(
               should_be_called,
               [1, 2, 3, 4, "A", "B", "C"],
               "cats",
               "cats_names"
               )

            self.assertEqual(r, 4)

   ###########################################
   # Tests for _resolve_categories_for_rooms #
   ###########################################
   def test_resolve_categories_for_rooms(self):

      should_be_called  = MagicMock(return_value = True)
      all_rooms         = self.generate_rooms_with_text("Some text")
      with patch("__main__.DXFRoomCatsResolver._resolve_category_for_room", should_be_called):
         r = DXFRoomCatsResolver._resolve_categories_for_rooms(
            all_rooms,
            self.cats,
            self.cats_names
         )

         # 3 matches
         self.assertEqual(r, 3)

         for r in all_rooms:
            MagicMock.assert_any_call(
               should_be_called,
               r,
               self.cats,
               self.cats_names
            )

         self.assertEqual(should_be_called.call_count, len(all_rooms))

      # Now we ensure it counts correctly the amount of rooms matched
      should_be_called  = MagicMock(side_effect = [True, False, False])
      with patch("__main__.DXFRoomCatsResolver._resolve_category_for_room", should_be_called):
         r = DXFRoomCatsResolver._resolve_categories_for_rooms(
            all_rooms,
            self.cats,
            self.cats_names
         )

         # 1 match
         self.assertEqual(r, 1)

   ########################################
   # Tests for _resolve_category_for_room #
   ########################################

   def test_resolve_category_for_room_matches_correctly(self):

      for t in ["AUL01", "aul01", "aula", " aula", "aula ", " AULA "]:
         for r in self.generate_rooms_with_text(t):
            m = DXFRoomCatsResolver._resolve_category_for_room(r, self.cats, self.cats_names)
            self.assertTrue(m)
            self.assertEqual(r["cat_name"], "Aula")

      for t in ["WC01", "bAGNO", "bagno ", " wc01", " wc01", " BaGnO "]:
         for r in self.generate_rooms_with_text(t):
            m = DXFRoomCatsResolver._resolve_category_for_room(r, self.cats, self.cats_names)
            self.assertTrue(m)
            self.assertEqual(r["cat_name"], "Bagno")

   def test_resolve_category_for_room_does_not_match(self):
      should_not_match = [
         "AULs01", "aul001", "aulas", " l'aula", "aulai ", " AAULA ",
         "WC011", "baAGNO", "B bagno ", " w c01", " wc001", " BaGnOs "
      ]

      for t in should_not_match:
         for r in self.generate_rooms_with_text(t):
            m = DXFRoomCatsResolver._resolve_category_for_room(r, self.cats, self.cats_names)
            self.assertFalse(m)
            self.assertTrue("cat_name" not in r)


   def test_cat_id_has_higher_priority_on_resolution(self):

      # Dovrà matchare "Aula" anche se le stanze contengono "Bagno" e "Aula Informatica"
      for t in ["AUL01", "aul01", "  aul01"]:
         for r in self.generate_rooms_with_text(t):
            r["texts"].append({ "text": "BAgno" })
            r["texts"].insert(0, { "text": "Aula Informatica" })

            m = DXFRoomCatsResolver._resolve_category_for_room(r, self.cats, self.cats_names)
            self.assertTrue(m)
            self.assertEqual(r["cat_name"], "Aula")

      # Dovrà matchare "Bagno" anche se le stanze contengono "Aula" e "Aula Informatica"
      for t in ["WC01", " wc01 ", "  wC01  "]:
         for r in self.generate_rooms_with_text(t):
            r["texts"].append({ "text": "Aula" })
            r["texts"].insert(0, { "text": "Aula Informatica" })

            m = DXFRoomCatsResolver._resolve_category_for_room(r, self.cats, self.cats_names)
            self.assertTrue(m)
            self.assertEqual(r["cat_name"], "Bagno")


   #######################
   # Other methods tests #
   #######################

   def test_get_room_categories_dict(self):
      with patch("__main__.RoomCategory.where", self.room_cats_where_mock):
         cats_dict = DXFRoomCatsResolver.get_room_categories_dict()
         self.assertTrue("AUL01" in cats_dict)
         self.assertTrue("AUL03" in cats_dict)
         self.assertTrue("WC01" in cats_dict)

         self.assertEqual(cats_dict["AUL01"], "Aula")
         self.assertEqual(cats_dict["AUL03"], "Aula Informatica")
         self.assertEqual(cats_dict["WC01"], "Bagno")

         self.assertEqual(len(cats_dict.keys()), 3)


   def test_get_room_categories_names_dict(self):
      with patch("__main__.RoomCategory.where", self.room_cats_where_mock):
         cats_dict   = DXFRoomCatsResolver.get_room_categories_dict()
         cats_names  = DXFRoomCatsResolver.get_room_categories_names_dict(cats_dict)

         self.assertTrue("AULA" in cats_names)
         self.assertTrue("AULA INFORMATICA" in cats_names)
         self.assertTrue("BAGNO" in cats_names)

         self.assertEqual(cats_names["AULA"], "Aula")
         self.assertEqual(cats_names["AULA INFORMATICA"], "Aula Informatica")
         self.assertEqual(cats_names["BAGNO"], "Bagno")

         self.assertEqual(len(cats_names.keys()), 3)
