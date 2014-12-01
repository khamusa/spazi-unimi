from tasks.csv_data_updater import CSVDataUpdater

class EdiliziaDataUpdater(CSVDataUpdater):

   def perform_update(self, csvfile ):
         self._reader   = reader_class(csvfile)
         csv_type       = self.infer_csv_from_header(self._reader.header)

         invalid_csv = lambda s : Logger.error("Invalid CSV header for EdiliziaDataUpdater: ",csv_type)
         {
            "room_categories" : self.update_room_categories,
            "buildings"       : self.update_buildings,
            "rooms"           : self.update_rooms
         }.get(csv_type, invalid_csv)(self._reader.content)


   def update_room_categories(self, categories):
      Logger.info("Updating room_categories collection")
      self._pm.clean_collection(self._pm.ROOM_CATEGORIES)
      self._pm.insert_room_categories(categories)

   def update_buildings(self,buildings):
      Logger.info("Updating buildings collection")

      """self._pm.clean_collection(self._pm.BID_TO_LBID)
      self._pm.insert_bid_lookup_table( buildings )"""

      """"self._pm.insert_buildings( self.add_origin(buildings) )"""

   def update_rooms(self,rooms):
      Logger.info("Updating rooms collection")
      """self._pm.insert_rooms( self.add_origin(rooms) )"""
