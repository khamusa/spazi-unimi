from utils.logger    import Logger
from pygeocoder      import Geocoder
from pygeocoder      import GeocoderError
from utils.logger    import Logger
from itertools       import chain
import time

class InvalidMergeStrategy(RuntimeError):
   pass

class DataMerger():

   skip_geocoding          = False
   geocoding_retry_count   = 0

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

      if(self.geocoding_retry_count > 0):
         time.sleep(self.geocoding_retry_count)

      try:
         if easyroom and easyroom.get("address", None):
            return easyroom["address"]

         elif self.skip_geocoding or self.geocoding_retry_count > 4:
            return ""

         elif len(edilizia["lon"].strip())>0 and len(edilizia["lat"].strip())>0 :
            g = Geocoder.reverse_geocode( float(edilizia["lat"]) , float(edilizia["lon"]) )
            self.geocoding_retry_count = max(self.geocoding_retry_count-1, 0)
            return g.formatted_address[:-len(g.country)-2]

         else:
            g = Geocoder.geocode( edilizia["address"] )
            self.geocoding_retry_count = max(self.geocoding_retry_count-1, 0)
            return g.formatted_address[:-len(g.country)-2]

      except GeocoderError as error:
         if error.status == GeocoderError.G_GEO_ZERO_RESULTS :
            Logger.warning("Address not valid " , edilizia["address"] )

         elif error.status == GeocoderError.G_GEO_OVER_QUERY_LIMIT :
               self.geocoding_retry_count += 1
               return DataMerger.merge_building_address(edilizia, easyroom)

   @classmethod
   def merge_building(self, edilizia = None, easyroom = None, dxf = None):
      """Merge easyroom and edilizia data"""

      coordinates = DataMerger.merge_building_coordinates(edilizia, easyroom)

      merged = {
         "l_b_id"          : DataMerger.merge_building_l_b_id(edilizia, easyroom),
         "address"         : DataMerger.merge_building_address(edilizia, easyroom),
         "building_name"   : DataMerger.merge_building_name(edilizia, easyroom),
         "coordinates"     : DataMerger.prepare_GeoJson_coordinates(coordinates),
         "floors"          : DataMerger.merge_floors(edilizia, easyroom, dxf)
      }

      return merged


   @classmethod
   def merge_room(klass, room1, room2):
      """Merge information of a single room"""
      eq = room1["equipments"] or room2["equipments"] or ""

      result = {
         "room_name"    : room1["room_name"]     or room2["room_name"]     or "",
         "capacity"     : room1["capacity"]      or room2["capacity"]      or "",
         "cat_name"     : room1["cat_name"]      or room2["cat_name"]      or "",
         "accessibility": room1["accessibility"] or room2["accessibility"] or "",
         "equipments"   : eq and eq.split("/")   or [],
         "polygon"      : room1["polygon"]       or room2["polygon"]       or False,
         }

      if not result["polygon"]:
         del result["polygon"]

      return result


   @classmethod
   def merge_floors(klass, edilizia, easyroom, dxf):
      floors = [
            dxf      and dxf["floors"],
            edilizia and edilizia.get("floors"),
            easyroom and easyroom.get("floors")
         ]

      floors = [ f for f in floors if f ]

      while len(floors) >= 2:
         result      = klass._match_and_merge_floors(floors[0], floors[1])
         floors[0:2] = [result]

      return floors and floors[0] or []


   @classmethod
   def _match_and_merge_floors(klass, base_floors, unmatched_floors):
      #TODO: salvare copia originale di base_floors
      for floor in chain(base_floors, unmatched_floors):
         klass._prepare_room_ids_set(floor)

      for unmatched in unmatched_floors:
         klass._match_and_merge_a_floor(base_floors, unmatched)

      for floor in chain(base_floors, unmatched_floors):
         klass._remove_room_ids_set(floor)

      #e adesso? esistono ancora unmatched floors con stanze?

      return base_floors

   @classmethod
   def _match_and_merge_a_floor(klass, base_floors, unmatched):

      for base in base_floors:
         match = base["room_ids"].intersection(unmatched["room_ids"])

         if match:
            unmatched["room_ids"].difference_update(match)
            merged_rooms = klass._merge_rooms_into_floor(base, unmatched, match)


   @classmethod
   def _merge_rooms_into_floor(klass, base, unmatched, matched_rooms):
      result = {}

      for room_id in matched_rooms:
         merged_room = klass.merge_room(
               base["rooms"][room_id],
               unmatched["rooms"][room_id]
            )
         result[room_id] = merged_room

      return result

   @classmethod
   def _prepare_room_ids_set(klass, floor):
      floor["room_ids"] = set(floor["rooms"].keys())

   @classmethod
   def _remove_room_ids_set(klass, floor):
      del floor["room_ids"]

   @classmethod
   def _floors_copy(klass, floors):
      return [ klass._floor_copy(floor) for floor in floors ]

   @classmethod
   def _floor_copy(klass, floor):
      result            = {}
      result["f_id"]    = floor["f_id"]
      # 1- copia lista di stanze
      final_room_keys   = [
            "polygon",
            "cat_name",
            "room_name",
            "equipments",
            "accessibility",
            "capacity"
         ]
      final_rooms_dict  = {}

      for room_id in floor["rooms"]:
         new_room = subtract_dict(floor["rooms"][room_id], final_room_keys)
         final_rooms_dict[room_id] = new_room

      result["rooms"]   = final_rooms_dict

      # 2- copia lista di stanze non identificate
      final_unidentified_rooms  = []

      for room in floor["unidentified_rooms"]:
         new_room = subtract_dict(room, final_room_keys)
         final_unidentified_rooms.append(new_room)

      result["unidentified_rooms"] = final_unidentified_rooms

      return result
