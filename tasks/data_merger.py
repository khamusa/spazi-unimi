from utils.logger import Logger
from pygeocoder import Geocoder
from pygeocoder import GeocoderError
from utils.logger import Logger
import time

class InvalidMergeStrategy(RuntimeError):
   pass

class DataMerger():
   def merge(self,field,edilizia,easyroom):
      strategy_name   = "merge_"+field
      merge_strategy  = getattr(self,strategy_name,self.raise_exception)
      merge_strategy(edilizia,easyroom)

   def raise_exception(self,field,data):
      raise InvalidMergeStrategy(field)

   # Helpers
   def coordinates_are_valid(self,data):
      """ check if coordinates keys "lat" and "lon" are present and if their values are floats """
      try:
         float(data["lat"])
         float(data["lon"])
         return True
      except ValueError:
         return False
      except KeyError:
         return False

   # Strategies
   def merge_building_name(self,edilizia,easyroom):
      """Building name merge strategy"""
      edilizia_is_valid                = any( x in edilizia["building_name"] for x in ["Dip","Polo","Dipartimento"] )
      easyroom_is_not_address_subset   = easyroom["venue"] not in easyroom["address"]

      if( edilizia_is_valid ):
         return edilizia["building_name"]
      elif( easyroom_is_not_address_subset ):
         return easyroom["venue"]
      else:
         return edilizia["building_name"]



   def merge_coordinates(self,edilizia,easyroom):
      """Coordinates merge strategy: return lat and lng if are present and valid
         in the edilizia data, otherwhise make a reverse geocoding request"""
      if( self.coordinates_are_valid(edilizia) ):
         lat = round(float(edilizia["lat"]),5)
         lng = round(float(edilizia["lon"]),5)
         return { "lat" :  lat, "lng" : lng }
      else:
         try:
            (lat,lng)   = (Geocoder.geocode(easyroom["address"])).coordinates
            lat         = round(lat,5)
            lng         = round(lng,5)
            return { "lat" : lat, "lng" : lng }
         except KeyError:
            Logger.warning("Address not found in easyroom data")
         except GeocoderError:
            Logger.warning("Coordinates parsing error")

      return { "lat" : None , "lng" : None }

   def merge_address(self,edilizia,easyroom):
      """Address merge strategy: use easyroom field if is present,
         otherwhise use Geocoder in order to obtain a well-formed address"""
      if( "address" in easyroom ):
         return easyroom["address"]
      else:
         return (Geocoder.geocode(edilizia["address"])).formatted_address


   def merge_building(self,edilizia,easyroom):
      """Merge easyroom and edilizia data"""

      Logger.info("Merge building")

      coordinate_merged = self.merge_coordinates(edilizia,easyroom)
      merged_data       = { key : self.merge(key,edilizia,easyroom) for key in ["building_name","address"] }
      merged_data["lat"] = coordinate_merged["lat"]
      merged_data["lng"] = coordinate_merged["lng"]

      merged = { "l_b_id":edilizia["l_b_id"],"b_id":edilizia["b_id"],"payload": {}, "date":time.strftime("%Y-%m-%d")}
      merged["payload"]["edilizia"] = { key:edilizia[key] for key in edilizia if key != "b_id" and key != "l_b_id" } 
      merged["payload"]["easyroom"] = { key:easyroom[key] for key in easyroom if key != "b_id" }
      merged["payload"]["merged"]   =  merged_data

      return merged
