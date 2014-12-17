import unittest
import time
from mock import MagicMock
from tasks.data_merger import DataMerger
from tasks.data_merger import InvalidMergeStrategy

class DataMergerTest(unittest.TestCase):

   def setUp(self):
      self.dm           = DataMerger()
      self.db_building  = {
          "_id" : "21030",
          "edilizia" : {
              "lat" : "45.476098",
              "l_b_id" : "5703",
              "lon" : "9.227756",
              "address" : "Milano - Via Celoria 2_Ed 3",
              "b_id" : "21030",
              "floors" : [
                  {
                      "f_id" : "R",
                      "rooms" : [
                          {
                              "capacity" : "100",
                              "room_name" : "Aula 2",
                              "r_id" : "R014",
                              "type_name" : "Aula",
                              "l_floor" : "R",
                              "b_id" : "21030"
                          }
                      ]
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
                      "rooms" : [
                          {
                              "capacity" : "100",
                              "accessibility" : "0",
                              "room_name" : "Aula 2 Ag",
                              "r_id" : "21030#R014",
                              "floor" : "0",
                              "b_id" : "21030",
                              "equipments" : "Lavagna luminosa/Internet/Impianto audio"
                          },
                          {
                              "capacity" : "40",
                              "accessibility" : "0",
                              "room_name" : "Aula Pellizzi",
                              "r_id" : "21030#R029",
                              "floor" : "0",
                              "b_id" : "21030",
                              "equipments" : ""
                          }
                      ]
                  }
              ]
          }
      }

   def test_merge_building_name(self):
      """ Merge without edilizia data """
      merged = self.dm.merge_building_name(edilizia=None, easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"Agraria Edificio 3")

      """ Merge without easyroom data """
      merged = self.dm.merge_building_name(edilizia=self.db_building["edilizia"], easyroom=None)
      self.assertEqual(merged,"Milano - Via Celoria 2_Ed 3")

      """ Merge with edilizia and easyroom data """
      merged = self.dm.merge_building_name(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"Agraria Edificio 3")

   def test_merge_building_address(self):
      """ Merge without edilizia data """
      merged = self.dm.merge_building_address(easyroom=self.db_building["easyroom"])
      self.assertEqual(merged, "Via Celoria, 2, Milano, 20133")

      """ Merge without easyroom data """
      merged = self.dm.merge_building_address(edilizia=self.db_building["edilizia"])
      self.assertEqual(merged, "Via Giovanni Celoria, 2, 20133 Milano")

      """ Merge with edilizia and easyroom data """
      merged = self.dm.merge_building_address(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(merged, "Via Celoria, 2, Milano, 20133")

   def test_merge_bulding_l_b_id(self):
      """ Merge without edilizia data """
      merged = self.dm.merge_building_l_b_id(easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"")

      """ Merge without easyroom data """
      merged = self.dm.merge_building_l_b_id(edilizia=self.db_building["edilizia"])
      self.assertEqual(merged,"5703")

      """ Merge with edilizia and easyroom data """
      merged = self.dm.merge_building_l_b_id(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(merged,"5703")

   def test_coordinates_are_valid(self):
      self.assertTrue(  self.dm.coordinates_are_valid( { "lat" :  "45.1234"  , "lon" : "10.132" } ) )
      self.assertFalse( self.dm.coordinates_are_valid( { "lat" :  "pippo"  , "lon" : "10.132" } ) )
      self.assertFalse( self.dm.coordinates_are_valid( { "lat" :  "pippo"  , "lon" : "10.132" } ) )
      self.assertFalse( self.dm.coordinates_are_valid( { "lat" :  "pippo"  , "lon" : "pluto" } ) )
      self.assertFalse( self.dm.coordinates_are_valid( { "lat" :  "pippo" } ) )
      self.assertFalse( self.dm.coordinates_are_valid( { "lon" :  "pippo" } ) )
      self.assertFalse( self.dm.coordinates_are_valid( { "plut" :  "pippo" } ) )

   def test_merge_coordinates(self):
      """ Merge without edilizia data """
      coordinates = self.dm.merge_building_coordinates(easyroom=self.db_building["easyroom"])
      self.assertEqual(coordinates,{"lat" : 45.476739, "lng" : 9.227256})

      """ Merge without easyroom data """
      coordinates = self.dm.merge_building_coordinates(edilizia=self.db_building["edilizia"])
      self.assertEqual(coordinates,{"lat" : 45.476098, "lng" : 9.227756})

      """ Merge with edilizia and easyroom data """
      coordinates = self.dm.merge_building_coordinates(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(coordinates,{"lat" : 45.476098, "lng" : 9.227756})

      """ Merge with edilizia and easyroom data ( edilizia has no coordinates ) """
      self.db_building["edilizia"].pop("lon")
      self.db_building["edilizia"].pop("lat")
      coordinates = self.dm.merge_building_coordinates(edilizia=self.db_building["edilizia"], easyroom=self.db_building["easyroom"])
      self.assertEqual(coordinates,{"lat" : 45.476739, "lng" : 9.227256})




