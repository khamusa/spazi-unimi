from utils.logger import Logger
from pygeocoder import Geocoder
from pygeocoder import GeocoderError
from utils.logger import Logger
import time

class InvalidMergeStrategy(RuntimeError):
   pass

class DataMerger():

   @classmethod
   def merge(self,field,edilizia,easyroom):
      strategy_name   = "merge_"+field
      merge_strategy  = getattr(self,strategy_name,self.raise_exception)
      merge_strategy(edilizia,easyroom)

   @classmethod
   def raise_exception(self,field,data):
      raise InvalidMergeStrategy(field)

   # Helpers
   @classmethod
   def coordinates_are_valid(self,data):
      """ check if coordinates keys "lat" and "lon" are present and if their values are floats """

      if not data:
         return False

      try:
         float(data.get("lat", ""))
         float(data.get("lon", ""))
         return True
      except ValueError:
         return False

   # Strategies

   @classmethod
   def merge_building_l_b_id(self, edilizia=None, easyroom=None):
      if edilizia :
         return edilizia.get("l_b_id", "")
      else:
         return ""

   @classmethod
   def merge_building_name(self, edilizia=None, easyroom=None):
      """Building name merge strategy"""
      if easyroom :
         return easyroom.get("building_name", None)
      else :
         return edilizia.get("address",None)


   @classmethod
   def merge_building_coordinates(self, edilizia=None, easyroom=None):
      """Coordinates merge strategy: return lat and lng if are present and valid
         in the edilizia data, otherwhise make a reverse geocoding request"""
      if self.coordinates_are_valid(edilizia) :
         lat = round(float(edilizia["lat"]), 6)
         lng = round(float(edilizia["lon"]), 6)

         return { "lat" :  lat, "lng" : lng }

      elif easyroom :
         address     =  easyroom.get("address", None) or edilizia.get("address", None)
         try :
            (lat,lng)   = (Geocoder.geocode(address)).coordinates
            lat         = round(lat,6)
            lng         = round(lng,6)
            return { "lat" : lat, "lng" : lng }
         except GeocoderError:
            Logger.warning("Coordinates parsing error")

         return { "lat" : None , "lng" : None }


   @classmethod
   def merge_building_address(self, edilizia=None, easyroom=None):
      """Address merge strategy: use easyroom field if is present,
         otherwhise use Geocoder in order to obtain a well-formed address"""

      if easyroom:
         return easyroom["address"]

      elif "lon" in edilizia and "lat" in edilizia:
         g = Geocoder.reverse_geocode( float(edilizia["lat"]) , float(edilizia["lon"]) )
         return g.formatted_address[:-len(g.country)-2]

      else:
         g = Geocoder.geocode( edilizia["address"] )
         return g.formatted_address[:-len(g.country)-2]


   @classmethod
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
