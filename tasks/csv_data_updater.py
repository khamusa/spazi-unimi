from utils.csv_reader import CSVReader

class InvalidCSVHeaderError(RuntimeError):
   pass

class CSVDataUpdater:
   def __init__(self, headers_dict, persistence_manager):
      self._valid_headers = { k : set(v) for k, v in headers_dict.items() }
      self._pm = persistence_manager

   def add_origin(self,items):
      def add_origin_single(item):
         item["origin"] = "csv"
         return item
      return ( add_origin_single(item) for item in items )

   def perform_update(self, csvfile, reader_class = CSVReader):
      reader   = reader_class(csvfile)
      csv_type = self.infer_csv_from_header(reader.header)

      if csv_type == None:
         raise InvalidCSVHeaderError("L'intestazione del file CSV non è valida")

      {
         "rooms"           : self.update_rooms,
         "buildings"       : self.update_buildings,
         "room_categories" : self.update_room_categories

      }[csv_type](reader.content)


   def infer_csv_from_header(self, effective_header):
      is_in_effective_header = lambda s: s in is_in_effective_header

      for valid_key in self._valid_headers:
         if (self._valid_headers[valid_key].issubset(effective_header)):
            return valid_key

      return None

   def update_room_categories(self, categories):
      self._pm.clean_collection(self._pm.ROOM_CATEGORIES)
      self._pm.insert_room_categories(categories)

   def update_buildings(self,buildings):
      self._pm.clean_collection(self._pm.BUILDINGS)
      self._pm.clean_collection(self._pm.BID_TO_LBID)
      self._pm.insert_bid_lookup_table( buildings )
      self._pm.insert_buildings( self.add_origin(buildings) )

   def update_rooms(self,rooms):
      self._pm.insert_rooms( self.add_origin(rooms) )
