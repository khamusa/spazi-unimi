import unittest
import model.orm_attrs as orm_attrs

class ORMAttrsTest(unittest.TestCase):

   def setUp(self):
      self.attrs = orm_attrs.ORMAttrs(
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
            "particular" : False
         }
      )

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
      self.assertEqual(self.attrs.get_path("_id"), "32548")
      self.assertEqual(self.attrs.get_path("cat_name"), "ofelia")


   #################
   # TEST has_path #
   #################
   def test_has_path(self):
      attrs = self.attrs

      # Truths
      self.assertTrue(attrs.has_path("some"))
      self.assertTrue(attrs.has_path("some.really"))
      self.assertTrue(attrs.has_path("some.really.very"))
      self.assertTrue(attrs.has_path("some.really.very.deep.deep"))
      self.assertTrue(attrs.has_path("some.really.very.deep.deep"))

      # Falses
      self.assertFalse(attrs.has_path("soome"))
      self.assertFalse(attrs.has_path("some.reallities"))
      self.assertFalse(attrs.has_path("some.really.veryyyyy"))
      self.assertFalse(attrs.has_path("some.really.very.deeeeep.deep"))
      self.assertFalse(attrs.has_path("some.really.very.deep.deeeeeep"))

      self.assertTrue(attrs.has_path("particular"))
