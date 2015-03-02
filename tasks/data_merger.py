from utils.logger       import Logger
from pygeocoder         import Geocoder
from pygeocoder         import GeocoderError
from utils.logger       import Logger
from itertools          import chain
from utils.myfunctools  import subtract_dict
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
      """
      Given a list of base floors, and a list of unmatched floors,
      analyze each unmatched floor trying to associate its rooms
      to base floors rooms.

      TODO: decide what to do in the end if there are still unmatched floors
      with rooms

      Arguments:
      - base_floors: a list of dictionaries representing floors
      - unmatched_floors: a list of dictionaries representing floors
        which will be merged onto base_floors.

      Return value: a new list of new floors, representing the result
      of the merge operation.
      """
      # Ensure we work on a COPY of base floors.
      base_floors = [ klass._floor_copy(f) for f in base_floors ]

      for floor in chain(base_floors, unmatched_floors):
         floor["room_ids"] = set(floor["rooms"].keys())

      for unmatched in unmatched_floors:
         klass._match_and_merge_a_floor(base_floors, unmatched)

      for floor in chain(base_floors, unmatched_floors):
         del floor["room_ids"]

      #e adesso? esistono ancora unmatched floors con stanze?

      return base_floors

   @classmethod
   def _match_and_merge_a_floor(klass, base_floors, unmatched):
      """
      Given a list of base floors and a single unmatched floor, merge rooms
      from the unmatched floor onto different base floors.

      TODO: keep track of the mappings performed so that it can be used to match
      rooms that do not get matched by room id.

      Arguments:
      - base_floors: a list of base floors;
      - unmatched: a dictionary representing an unmatched floor.

      Return Value: None
      """
      for base in base_floors:
         match = base["room_ids"].intersection(unmatched["room_ids"])

         if match:
            unmatched["room_ids"].difference_update(match)
            merged_rooms = klass._merge_rooms_into_floor(base, unmatched, match)


   @classmethod
   def _merge_rooms_into_floor(klass, base, unmatched, matched_rooms):
      """
      Given two floors (base, unmatched) and a set of room ids (matched_rooms),
      merge the rooms indicated by the set from the unmatched floor into the
      base floor.

      The changes will be performed in place in the base floor.

      Arguments
      - base: a floor dictionary onto which merged rooms will be placed.
      - unmatched: a floor dictionary containing the rooms to be merged.
      - matched_rooms: a set containing the room ids that identifies the
      rooms from the unmatched floor to be merged onto the base floor.
      Both floors MUST contain the rooms identified by those ids, otherwise
      the function may cause an error.

      Return Value: None
      """

      for room_id in matched_rooms:
         merged_room = klass.merge_room(
               base["rooms"][room_id],
               unmatched["rooms"][room_id]
            )
         base["rooms"][room_id] = merged_room

   @classmethod
   def merge_room(klass, room1, room2):
      """
      Merge information of a single room by 2 generic room dictionaries.

      room1 attributes have higher priority compared to room2

      Arguments:
      - room1: room dictionary information;
      - room2: second room dictionary.

      Returns:
      - a new room dictionary obtained by merging together room1 and room2.
      """
      eq = room1.get("equipments") or room2.get("equipments")
      if getattr(eq, "split", None):
         eq = eq.split("/")

      result = {
         "room_name"    : room1.get("room_name")     or room2.get("room_name", ""),
         "capacity"     : room1.get("capacity")      or room2.get("capacity", ""),
         "cat_name"     : room1.get("cat_name")      or room2.get("cat_name", ""),
         "accessibility": room1.get("accessibility") or room2.get("accessibility", ""),
         "polygon"      : room1.get("polygon")       or room2.get("polygon", False),
         "equipments"   : eq                         or []
         }

      if result["polygon"] is False:
         del result["polygon"]

      return result

   @classmethod
   def _floor_copy(klass, floor):
      """
      Given a floor, perform a pseudo-deep copy, filtering unnecessary keys
      for floor merging.

      For pseudo-deep we mean that fields in the dictionary are copied on a
      per-case basis. In particular, rooms are merged together into a new
      room object, so that further processing algorithms won't change the
      original ones.

      Arguments:
      - floor: a dictionary containing a floor information

      Return Value: a new foor object that copies information from the original
      floor, ignoring however unused keys.
      """
      result                        = {}
      result["f_id"]                = floor["f_id"]
      result["rooms"]               = {}
      result["unidentified_rooms"]  = []

      # 1 - copia lista di stanze, creando copie e lasciando soltanto le
      #     chiavi necessarie per il merging.
      final_room_keys   = [
            "polygon",
            "cat_name",
            "room_name",
            "equipments",
            "accessibility",
            "capacity"
         ]

      for room_id, room in floor.get("rooms", {}).items():
         result["rooms"][room_id] = subtract_dict(room, final_room_keys)

      # 2- copia lista di stanze non identificate, creando copie e lasciando
      #    soltanto le chiavi necessarie per il merging.
      for room in floor.get("unidentified_rooms", []):
         new_room = subtract_dict(room, final_room_keys)
         result["unidentified_rooms"].append(new_room)

      return result
