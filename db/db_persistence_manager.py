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
