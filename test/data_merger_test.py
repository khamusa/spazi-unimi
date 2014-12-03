import unittest
import time
from mock import MagicMock
from tasks.data_merger import DataMerger
from tasks.data_merger import InvalidMergeStrategy

class DataMergerTest(unittest.TestCase):

   def setUp(self):
      self.dm           = DataMerger()
      self.db_building  = {
      "b_id"      : "1234" ,
      "l_b_id"    : "1456" ,
      "payload"   : {
            "edilizia"  : { "address":"Milano - Via Celoria 2_Ed 27","lat":"45.476450","lon":"9.233717","building_name":"Dip. Informatica"},
            "easyroom"  : { "address":"Via Celoria, 2, Milano, 20133", "venue":"Dip. Informatica"}
         }
      }

   def test_use_merge_strategy_for_file(self):
      self.dm.merge_building = MagicMock()
      self.dm.merge("building",{"building":"values"},{"building":"values"})
      self.dm.merge_building.assert_called_once_with({"building":"values"},{"building":"values"})

   def test_raise_exception_no_merge_strategy(self):
      self.assertRaises(InvalidMergeStrategy,self.dm.merge,"pippo",{"building":"values"},{"building":"values"})

   def test_merge_building_name(self):
      edilizia_data = {"building_name":"Dipartimento Informatica","address":"via Celoria"}
      easyroom_data = {"venue":"Not a nice name","address":"Via Celoria 13,Milano"}

      name = self.dm.merge_building_name(edilizia=edilizia_data,easyroom=easyroom_data)
      self.assertEqual(name,"Dipartimento Informatica")

      edilizia_data["building_name"] = "Dip. Informatica"
      name = self.dm.merge_building_name(edilizia=edilizia_data,easyroom=easyroom_data)
      self.assertEqual(name,"Dip. Informatica")

      edilizia_data["building_name"]   = "Informatica"
      easyroom_data["venue"]           = "Good name"
      name = self.dm.merge_building_name(edilizia=edilizia_data,easyroom=easyroom_data)
      self.assertEqual(name,"Good name")

      edilizia_data["building_name"]   = "Informatica"
      easyroom_data["venue"]           = "Milano"
      name = self.dm.merge_building_name(edilizia=edilizia_data,easyroom=easyroom_data)
      self.assertEqual(name,"Informatica")

      edilizia_data["building_name"]   = "Informatica"
      easyroom_data["venue"]           = "Dipartimento di Informatica"
      name = self.dm.merge_building_name(edilizia=edilizia_data,easyroom=easyroom_data)
      self.assertEqual(name,"Dipartimento di Informatica")


   def test_coordinates_helper(self):
      self.assertEqual(self.dm.coordinates_are_valid({ "lat" : "34.2" , "lon" : "33.1" }),True)
      self.assertEqual(self.dm.coordinates_are_valid({ "lon" : "33.1" }),False)
      self.assertEqual(self.dm.coordinates_are_valid({ "lat" : "pippo" , "lon" : "33.1" }),False)
      self.assertEqual(self.dm.coordinates_are_valid({ "lat" : "22.1" , "lon" : "pippo" }),False)
      self.assertEqual(self.dm.coordinates_are_valid({ "pippo" : 23 }),False)
      self.assertEqual(self.dm.coordinates_are_valid({ "name" : "ciao" , "lat" : "23.1" , "lon" : "123.2" }),True)

   def test_merge_valid_coordinates(self):
      edilizia_data = self.db_building["payload"]["edilizia"]
      easyroom_data = self.db_building["payload"]["easyroom"]
      coords        = self.dm.merge_coordinates(edilizia=edilizia_data,easyroom=easyroom_data)

      self.assertEqual(coords,{"lat":45.47645,"lng":9.23372})

   def test_merge_invalid_coordinates(self):
      """ Edilizia data without coordinates """
      edilizia_data = self.db_building["payload"]["edilizia"]
      edilizia_data.pop("lon",None);
      edilizia_data.pop("lat",None);

      easyroom_data = self.db_building["payload"]["easyroom"]
      coords        = self.dm.merge_coordinates(edilizia=edilizia_data,easyroom=easyroom_data)

      self.assertEqual(coords,{"lat":45.47674,"lng":9.22726})

   def test_merge_invalid_coordinates2(self):
      """ Edilizia data without coordinates """

      edilizia_data = self.db_building["payload"]["edilizia"]
      edilizia_data.pop("lon",None);
      edilizia_data.pop("lat",None);

      easyroom_data              = self.db_building["payload"]["easyroom"]
      easyroom_data["address"]   = "via festa del perdono 2, milano"

      coords        = self.dm.merge_coordinates(edilizia=edilizia_data,easyroom=easyroom_data)
      self.assertEqual(coords,{"lat":45.46186,"lng":9.19498})

   def test_merge_address(self):
      edilizia_data  = self.db_building["payload"]["edilizia"]
      easyroom_data  = self.db_building["payload"]["easyroom"]

      self.assertEqual(self.dm.merge_address(edilizia_data,easyroom_data),"Via Celoria, 2, Milano, 20133")

   def test_merge_address_fecthed_from_geocoder(self):
      edilizia_data  = self.db_building["payload"]["edilizia"]
      easyroom_data  = self.db_building["payload"]["easyroom"]
      easyroom_data.pop("address",None);

      self.assertEqual(self.dm.merge_address(edilizia_data,easyroom_data),"Via Giovanni Celoria, 20133 Milano, Italy")

   
   def test_merge_building_with_edilizia_and_easyroom_data(self):
      edilizia_data  = {
         "l_b_id"       : 987,
         "b_id"         : 32210,
         "address"      : "Milano - Via Balzaretti 2_Ed 27",
         "lat"          : "45.477180",
         "lon"          : "9.220888",
         "building_name":"Dip. Informatica"
      }
      easyroom_data  = {
         "b_id"      : 32210,
         "venue"     : "Balzaretti",
         "address"   : "Via Giuseppe Balzaretti, 9 20133 Milano"
      }

      result         = {
         "b_id"      : 32210,
         "l_b_id"    : 987,
         "date"      : time.strftime("%Y-%m-%d"),
         "payload"   : {
            "edilizia" : {
               "address"         : edilizia_data["address"],
               "lat"             : "45.477180",
               "lon"             : "9.220888",
               "building_name"   : "Dip. Informatica"
            },
            "easyroom" : {
               "venue"     : easyroom_data["venue"],
               "address"   : easyroom_data["address"]
            },
            "merged"   : {
               "name"      : "Dip. Informatica",
               "address"   : "Via Giuseppe Balzaretti, 9 20133 Milano",
               "lat"       : 45.47718,
               "lng"       : 9.22089
            }
         }
      }

      merged_data = self.dm.merge_building(edilizia_data,easyroom_data)

      self.assertEqual( merged_data["date"] , result["date"] )
      self.assertEqual( merged_data["payload"]["edilizia"] , result["payload"]["edilizia"] )
