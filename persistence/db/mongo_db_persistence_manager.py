from . import DB;

class MongoDBPersistenceManager:

   def __init__(self, config = None, db = None):
      if config is not None:
         db_cfg = config["db"]
         db = DB(db_cfg["url"], db_cfg["port"], db_cfg["db_name"])

      self.db = db

   def clean_collection(self,collection_name):
      self.db[collection_name].drop()

   def save(self, collection_name, value):
      self.db[collection_name].save(value)

   def get_collection(self, collection_name):
      return self.db[collection_name]
