import unittest
import model.odm_attrs as odm_attrs

class ODMAttrsTest(unittest.TestCase):

   def setUp(self):
      self.attrs = odm_attrs.ODMAttrs(
         {
            "_id": "32548",
            "some": {
               "really": {
                  "very": {
                     "deep": {
                        "deep": "Structure",
                     }
                  }
               },
               "no_deep" : "Yes"
            },
            "cat_name": "ofelia",
            "another": {
               "structure" : "not so deep",
               "deep": {
                  "structure" : "slightly deeper"
               }
            },
            "particular" : False,
            "pippo" : "pluto",
            "mickey": "paperino"
         }
      )

   ###########################
   # Testing method get_path #
   ###########################

   def test_get_path_against__getitem__(self):
      attrs = self.attrs

      # Test basic get_path against __getitem__ implementation
      self.assertEqual(attrs.get_path("some"), attrs["some"])

      self.assertEqual(
         attrs.get_path("some.really"),
         attrs["some"]["really"]
      )
      self.assertEqual(
         attrs.get_path("some.really.very"),
         attrs["some"]["really"]["very"]
      )
      self.assertEqual(
         attrs.get_path("some.really.very.deep.deep"),
         attrs["some"]["really"]["very"]["deep"]["deep"]
      )
      self.assertEqual(
         attrs.get_path("some.really.very.deep.deep"),
         "Structure"
      )

   def test_build_path_when_not_found(self):
      attrs = self.attrs

      self.assertEqual(attrs.get_path("new_attr", 123, build=True), 123)
      self.assertEqual(attrs["new_attr"], 123)

      self.assertEqual(attrs.get_path("some.error_new", {}, build=True), {})
      self.assertEqual(attrs["some"]["error_new"], {})

      self.assertEqual(attrs.get_path("some.really.new", "n", build=True), "n")
      self.assertEqual(attrs["some"]["really"]["new"], "n")

      self.assertEqual(attrs.get_path("new.nested.deep.struct", 9, build=True), 9)
      self.assertEqual(attrs["new"]["nested"]["deep"]["struct"], 9)

      # (default) If build is not True, ensure keys don't get added
      self.assertEqual(attrs.get_path("new_attr2", 123), 123)
      self.assertTrue("new_attr2" not in attrs)

      self.assertEqual(attrs.get_path("some.error_new", {}), {})
      self.assertTrue("error_new2" not in attrs["some"])

      # Explicitly false
      self.assertEqual(attrs.get_path("some.really.new", "n", build=False), "n")
      self.assertTrue("new2" not in attrs["some"]["really"])

      # After all, the original values must have been preserved
      self.assertEqual(
         attrs.get_path("some.really.very.deep.deep"),
         "Structure"
      )

   def test_get_path_when_not_found(self):
      # 1- single level
      attrs = self.attrs
      self.assertEqual(attrs.get_path("_isd"), None)
      self.assertEqual(attrs.get_path("some.error"), None)
      self.assertEqual(attrs.get_path("some.really.wrong"), None)
      self.assertEqual(attrs.get_path("some.really.very.deep.fail"), None)
      self.assertEqual(attrs.get_path("some.really.very.fail.deep"), None)
      self.assertEqual(attrs.get_path("some.really.fail.fail.deep"), None)
      self.assertEqual(attrs.get_path("some.fail.very.fail.deep"), None)
      self.assertEqual(attrs.get_path("fail.fail.fail.fail.deep"), None)
      self.assertEqual(attrs.get_path("fail.really.very.fail.deep"), None)

   def test_get_path_with_default_value(self):
      # 1- single level
      attrs = self.attrs
      self.assertEqual(attrs.get_path("_isd", 1), 1)
      self.assertEqual(attrs.get_path("some.error", 2), 2)
      self.assertEqual(attrs.get_path("some.really.wrong", 3), 3)
      self.assertEqual(attrs.get_path("some.really.very.deep.fail", 4), 4)
      self.assertEqual(attrs.get_path("some.really.very.fail.deep", 5), 5)
      self.assertEqual(attrs.get_path("some.really.fail.fail.deep", 6), 6)
      self.assertEqual(attrs.get_path("some.fail.very.fail.deep", 7), 7)
      self.assertEqual(attrs.get_path("fail.fail.fail.fail.deep", 8), 8)
      self.assertEqual(attrs.get_path("fail.really.very.fail.deep", 9), 9)

   def test_get_path_on_single_level_paths(self):
      attrs = self.attrs
      self.assertEqual(attrs.get_path("_id"), "32548")
      self.assertEqual(attrs.get_path("cat_name"), "ofelia")

   def test_get_path_with_list_notation(self):
      attrs = self.attrs
      self.assertEqual(attrs.get_path(["_id"]), "32548")
      self.assertEqual(attrs.get_path(["cat_name"]), "ofelia")

      # Unexisting without defaults
      self.assertEqual(attrs.get_path(["some", (1, 2)]), None)
      self.assertEqual(attrs.get_path(["some", 77, "wrong"]), None)

      # With defaults
      self.assertEqual(attrs.get_path([777, "fail", 456, "fail", "deep"], 8), 8)
      self.assertEqual(attrs.get_path(["fail", "really", "very", 935, "deep"], 9), 9)

      # With build
      self.assertEqual(attrs.get_path(["new_attr"], 123, build=True), 123)
      self.assertEqual(attrs["new_attr"], 123)

      self.assertEqual(attrs.get_path(["some", 478], {}, build=True), {})
      self.assertEqual(attrs["some"][478], {})

   #################
   # TEST has_path #
   #################
   def test_has_path(self):
      attrs = self.attrs

      # Truths
      self.assertTrue(attrs.has_path(["some"]))
      self.assertTrue(attrs.has_path(["some", "really"]))
      self.assertTrue(attrs.has_path(["some", "really", "very"]))
      self.assertTrue(attrs.has_path("some.really.very.deep.deep"))
      self.assertTrue(attrs.has_path("some.really.very.deep.deep"))

      # Falses
      self.assertFalse(attrs.has_path(["soome"]))
      self.assertFalse(attrs.has_path(["some", "reallities"]))
      self.assertFalse(attrs.has_path("some.really.veryyyyy"))
      self.assertFalse(attrs.has_path("some.really.very.deeeeep.deep"))
      self.assertFalse(attrs.has_path("some.really.very.deep.deeeeeep"))

      self.assertTrue(attrs.has_path("particular"))

   ####################
   # TEST id handling #
   ####################
   def test_id_assignment_gets_sanitized(self):
      odm = odm_attrs.ODMAttrs({ "_id": "   123 "})
      self.assertEqual(odm["_id"], "123")

      odm.attrs({ "_id" : 13124 })
      self.assertEqual(odm["_id"], "13124")

      odm["_id"] = 444
      self.assertEqual(odm["_id"], "444")

   def test_external_id_handling(self):
      attrs = odm_attrs.ODMAttrs({ "bid": 123, "pippo": 123 }, external_id = "bid")

      def verify_id(expected):
         self.assertTrue(attrs["bid"] is attrs["_id"])
         self.assertEqual(attrs["bid"], expected)
         self.assertEqual(attrs["pippo"], 123)

      # Test __getitem__
      verify_id("123")

      # Test __setitem__
      attrs["bid"]   = "PIUFACILE"
      verify_id("PIUFACILE")

      attrs["pippo"] = "Sporcizia"
      self.assertEqual(attrs["pippo"], "Sporcizia")

      # Test __contains__
      self.assertTrue("_id"   in attrs)
      self.assertTrue("bid"   in attrs)
      self.assertTrue("pippo" in attrs)
      self.assertFalse("piw!" in attrs)

      # Test get
      attrs["_id"] = 123
      self.assertEqual(attrs.get("_id"), "123")
      self.assertEqual(attrs.get("_id", "hahaha"), "123")
      self.assertEqual(attrs.get("_idzzzz"), None)
      self.assertEqual(attrs.get("_idbiz", "hahaha"), "hahaha")
      self.assertEqual(attrs.get("bid"), "123")

   #############################################
   # TEST attrs interface (get, set, contains) #
   #############################################

   def test_attrs_get_and_set(self):
      self.assertEqual(self.attrs["pippo"], "pluto")

      self.attrs.attrs( { "pippo": "sempronio", "caio": "tizio"})
      self.assertEqual(self.attrs["pippo"], "sempronio")
      self.assertEqual(self.attrs["caio"], "tizio")

      self.assertEqual(self.attrs["mickey"], "paperino")

   def test_has_attr(self):
      self.assertTrue("pippo"  in self.attrs)
      self.assertTrue("mickey" in self.attrs)
      self.assertFalse("1234"  in self.attrs)

   def test_attr_getter_method(self):
      self.assertTrue("pippuzzo" not in self.attrs)
      self.assertEqual(self.attrs["pippo"], "pluto")

   def test_attr_setter_method(self):
      self.attrs["pippuzzo"] = "ciao"
      self.assertEqual(self.attrs["pippuzzo"] ,"ciao")

   ###############################
   # TEST changed state handling #
   ###############################

   def test_set_changed(self):
      self.attrs.set_changed(False)
      self.assertFalse(self.attrs.is_changed())

      self.attrs.set_changed(True)
      self.assertTrue(self.attrs.is_changed())

      self.attrs.set_changed(False)
      self.assertFalse(self.attrs.is_changed())

   def test_is_changed(self):
      self.assertTrue(self.attrs.is_changed())
      self.attrs.set_changed(False)
      self.attrs.attr("pippo", "ciao")
      self.assertTrue(self.attrs.is_changed())

      self.attrs.set_changed(False)
      self.attrs["pippo"] = "ciao"
      self.assertFalse(self.attrs.is_changed())

      self.attrs.set_changed(False)
      self.attrs["pippo"] = "ciao2"
      self.assertTrue(self.attrs.is_changed())
