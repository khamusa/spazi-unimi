from db.db import DB

class DBPersistenceManager:

   def __init__(self, config = None, db = None):
      if config is not None:
         db_cfg = config["db"]
         db = DB(db_cfg["url"], db_cfg["port"], db_cfg["db_name"])

      self.db = db

   def clean_collection(self,collection_name):
      self.db[collection_name].drop()

   def insert_room_category(self, category):
      self.db["room_categories"].insert(category)

   def insert_room_categories(self,categories):
      self.clean_collection("room_categories")
      for c in categories:
         self.insert_room_category(c)

   def insert_building(self,building):
      self.db["buildings"].insert(building)

   def insert_buildings(self,buildings):
      self.clean_collection("buildings")
      for b in buildings:
         self.insert_building(b)

   def insert_room(self,room):
      self.db["rooms"].insert(room)

   def insert_rooms(self,rooms):
      for r in rooms:
         self.insert_room(r)

   def insert_bid_lookup_table(self,buildings):
      self.clean_collection("bid_to_lbid")

      # create indexes
      self.db["bid_to_lbid"].ensure_index("l_b_id")
      self.db["bid_to_lbid"].ensure_index("b_id")

      for b in buildings:
         self.db["bid_to_lbid"].insert({ "l_b_id":b["l_b_id"] , "b_id" : b["b_id"] })
