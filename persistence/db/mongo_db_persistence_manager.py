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

   def destroy_by_id(self, collection_name, id):
      self.db[collection_name].remove({"_id" : id})

   def get_collection(self, collection_name):
      return self.db[collection_name]

   def update(self, collection_name, query, action, options):
      return self.db[collection_name].update(query, action, **options)

   def remove(self, collection_name, query, options):
      return self.db[collection_name].remove(query, **options)
