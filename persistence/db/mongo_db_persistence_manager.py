from . import DB;

class MongoDBPersistenceManager:

   ROOM_CATEGORIES = "room_categories"
   BUILDINGS = "buildings"
   BID_TO_LBID = "bid_to_lbid"
   ROOMS = "rooms"

   _valid_collections = [ROOM_CATEGORIES, BUILDINGS, BID_TO_LBID, ROOMS]

   def __init__(self, config = None, db = None):
      if config is not None:
         db_cfg = config["db"]
         db = DB(db_cfg["url"], db_cfg["port"], db_cfg["db_name"])

      self.db = db

   def clean_collection(self,collection_name):
      self.db[collection_name].drop()

   def insert_room_category(self, category):
      self.db[self.ROOM_CATEGORIES].insert(category)

   def insert_room_categories(self,categories):
      for c in categories:
         self.insert_room_category(c)

   def insert_building(self,building):
      self.db[self.BUILDINGS].insert(building)

   def insert_buildings(self,buildings):
      for b in buildings:
         self.insert_building(b)

   def insert_room(self,room):
      self.db[self.ROOMS].insert(room)

   def insert_rooms(self,rooms):
      for r in rooms:
         self.insert_room(r)

   def insert_bid_lookup_table(self,buildings):
      # create indexes
      self.db[self.BID_TO_LBID].ensure_index("l_b_id")
      self.db[self.BID_TO_LBID].ensure_index("b_id")

      for b in buildings:
         self.db[self.BID_TO_LBID].insert({ "l_b_id":b["l_b_id"] , "b_id" : b["b_id"] })
