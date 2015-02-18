from utils.logger import Logger
from pygeocoder import Geocoder
from pygeocoder import GeocoderError
from utils.logger import Logger
import time

class InvalidMergeStrategy(RuntimeError):
   pass

class DataMerger():

   skip_geocoding = False

   @classmethod
   def merge(self,field,edilizia,easyroom):
      strategy_name   = "merge_building_"+field
      merge_strategy  = getattr(DataMerger, strategy_name, DataMerger.raise_exception)
      return merge_strategy(edilizia,easyroom)

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

      elif easyroom and not self.skip_geocoding:
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
   def prepare_GeoJson_coordinates(self,coordinates):
      coordinates = coordinates or { "lng" : 0 , "lat" : 0 }
      return {
            "type"         : "Point",
            "coordinates"  : [ coordinates["lng"] , coordinates["lat"] ]
         }


   @classmethod
   def merge_building_address(self, edilizia=None, easyroom=None):
      """Address merge strategy: use easyroom field if is present,
         otherwhise use Geocoder in order to obtain a well-formed address"""

      try:
         if easyroom and easyroom.get("address", None):
            return easyroom["address"]

         elif self.skip_geocoding:
            return ""

         elif len(edilizia["lon"].strip())>0 and len(edilizia["lat"].strip())>0 :

            g = Geocoder.reverse_geocode( float(edilizia["lat"]) , float(edilizia["lon"]) )
            return g.formatted_address[:-len(g.country)-2]

         else:
            g = Geocoder.geocode( edilizia["address"] )
            return g.formatted_address[:-len(g.country)-2]

      except GeocoderError as error:
         if error.status == GeocoderError.G_GEO_ZERO_RESULTS :
            Logger.warning("Address not valid " , edilizia["address"] )

         elif error.status == GeocoderError.G_GEO_OVER_QUERY_LIMIT :
            time.sleep(1)
            DataMerger.merge_building_address(edilizia, easyroom)



   @classmethod
   def merge_building(self, edilizia=None, easyroom=None):
      """Merge easyroom and edilizia data"""

      coordinates = DataMerger.merge_building_coordinates(edilizia, easyroom)

      merged = {
         "l_b_id"          : DataMerger.merge_building_l_b_id(edilizia, easyroom),
         "address"         : DataMerger.merge_building_address(edilizia, easyroom),
         "building_name"   : DataMerger.merge_building_name(edilizia, easyroom),
         "coordinates"     : DataMerger.prepare_GeoJson_coordinates(coordinates)

      }

      return merged


   @classmethod
   def merge_room(self, edilizia = None, easyroom = None):
      """Merge information of a single room"""

      eq = (easyroom and easyroom.get("equipments", "")) or ""
      if eq is "":
         eq = []
      else:
         eq = eq.split("/")
      return {
         "r_id"            : (edilizia and edilizia.get("r_id", None) or easyroom["r_id"]),
         "room_name"       : (edilizia and edilizia.get("room_name", None) or easyroom.get("room_name", "")) or "",
         "capacity"        : (edilizia and edilizia.get("capacity", None) or easyroom.get("capacity", "")) or "",
         "type_name"       : (edilizia and edilizia.get("type_name", "")) or "",
         "accessibility"   : (easyroom and easyroom.get("accessibility", "")) or "",
         "equipments"      : eq
         }


