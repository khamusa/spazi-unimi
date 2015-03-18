from tasks.data_merger  import DataMerger
import unittest, time

class DataMergerTest(unittest.TestCase):

   def setUp(self):
      self.db_building  = {
          "_id" : "21030",
          "edilizia" : {
              "lat" : "45.476098",
              "l_b_id" : "5703",
              "lon" : "9.227756",
              "address" : "Via Celoria, 2, Milano",
              "building_number": "3",
              "b_id" : "21030",
              "floors" : [
                  {
                      "f_id" : "R",
                      "rooms" : {}
                  }
              ]
          },
          "easyroom" : {
              "address" : "Via Celoria, 2, Milano, 20133",
              "n_floors" : "1",
              "building_name" : "Agraria Edificio 3",
              "b_id" : "21030",
              "floors" : [
                  {
                      "f_id" : "0",
                      "rooms" : {}
                  }
              ]
          }
      }

   def test_merge_building_name(self):
      """ Merge without edilizia data """
      merged = DataMerger._merge_building_name(edilizia=None, easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"Agraria Edificio 3")

      """ Merge without easyroom data """
      merged = DataMerger._merge_building_name(edilizia=self.db_building["edilizia"], easyroom=None)
      self.assertEqual(merged, "")

      """ Merge with edilizia and easyroom data """
      merged = DataMerger._merge_building_name(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"Agraria Edificio 3")

   def test_merge_building_address(self):
      """ Merge without edilizia data """
      merged = DataMerger._merge_building_address(easyroom=self.db_building["easyroom"])
      self.assertEqual(merged, "Via Celoria, 2, Milano, 20133")

      if not DataMerger.skip_geocoding:
         """ Merge without easyroom data """
         merged = DataMerger._merge_building_address(edilizia=self.db_building["edilizia"])
         self.assertEqual(merged, "Via Celoria, 2, Milano")

         """ Merge with edilizia and easyroom data """
         merged = DataMerger._merge_building_address(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
         self.assertEqual(merged, "Via Celoria, 2, Milano, 20133")

   def test_merge_building_l_b_id(self):
      """ Merge without edilizia data """
      merged = DataMerger._merge_building_l_b_id(easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"")

      """ Merge without easyroom data """
      merged = DataMerger._merge_building_l_b_id(edilizia=self.db_building["edilizia"])
      self.assertEqual(merged,"5703")

      """ Merge with edilizia and easyroom data """
      merged = DataMerger._merge_building_l_b_id(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"5703")

   def test_coordinates_are_valid(self):
      self.assertTrue(  DataMerger.coordinates_are_valid( { "lat" :  "45.1234"  , "lon" : "10.132" } ) )
      self.assertFalse( DataMerger.coordinates_are_valid( { "lat" :  "pippo"  , "lon" : "10.132" } ) )
      self.assertFalse( DataMerger.coordinates_are_valid( { "lat" :  "pippo"  , "lon" : "10.132" } ) )
      self.assertFalse( DataMerger.coordinates_are_valid( { "lat" :  "pippo"  , "lon" : "pluto" } ) )
      self.assertFalse( DataMerger.coordinates_are_valid( { "lat" :  "pippo" } ) )
      self.assertFalse( DataMerger.coordinates_are_valid( { "lon" :  "pippo" } ) )
      self.assertFalse( DataMerger.coordinates_are_valid( { "plut" :  "pippo" } ) )

   def test_merge_coordinates(self):
      """ Merge without easyroom data """
      coordinates = DataMerger._merge_building_coordinates(edilizia=self.db_building["edilizia"])
      self.assertEqual(coordinates,{"lat" : 45.476098, "lng" : 9.227756})

      """ Merge with edilizia and easyroom data """
      coordinates = DataMerger._merge_building_coordinates(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(coordinates,{"lat" : 45.476098, "lng" : 9.227756})

      if not DataMerger.skip_geocoding:
         """ Merge without edilizia data """
         coordinates = DataMerger._merge_building_coordinates(easyroom=self.db_building["easyroom"])
         self.assertEqual(coordinates,{"lat" : 45.476739, "lng" : 9.227256})

         """ Merge with edilizia and easyroom data ( edilizia has no coordinates ) """
         self.db_building["edilizia"].pop("lon")
         self.db_building["edilizia"].pop("lat")
         coordinates = DataMerger._merge_building_coordinates(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
         self.assertEqual(coordinates,{"lat" : 45.476739, "lng" : 9.227256})


   def test_merge_building(self):

      """ Merge without edilizia data """
      merged = DataMerger.merge_building(easyroom=self.db_building["easyroom"])

      if not DataMerger.skip_geocoding:
         self.assertEqual(merged["coordinates"],{ "type": "Point", "coordinates": [9.227256, 45.476739] })

      self.assertTrue("l_b_id" not in merged)
      self.assertEqual(merged["address"],self.db_building["easyroom"]["address"])
      self.assertEqual(merged["building_name"],self.db_building["easyroom"]["building_name"])

      """ Merge without easyroom data """
      merged = DataMerger.merge_building(edilizia=self.db_building["edilizia"])

      self.assertEqual(merged["coordinates"],
         { "type": "Point", "coordinates": [
            float(self.db_building["edilizia"]["lon"]),
            float(self.db_building["edilizia"]["lat"])
            ]
         })
      self.assertEqual(merged["l_b_id"], self.db_building["edilizia"]["l_b_id"])
      self.assertTrue("building_name" not in merged)

      if not DataMerger.skip_geocoding:
         self.assertEqual(merged["address"],"Via Celoria, 2, Milano")


      """ Merge with easyroom and edilizia data """
      merged = DataMerger.merge_building(edilizia=self.db_building["edilizia"],easyroom=self.db_building["easyroom"])

      self.assertEqual(merged["l_b_id"], self.db_building["edilizia"]["l_b_id"])
      self.assertEqual(merged["address"], self.db_building["easyroom"]["address"])
      self.assertEqual(merged["building_name"], self.db_building["easyroom"]["building_name"])
      self.assertEqual(merged["coordinates"],
         { "type": "Point", "coordinates": [
            float(self.db_building["edilizia"]["lon"]),
            float(self.db_building["edilizia"]["lat"])
            ]
         })
