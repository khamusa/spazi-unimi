from db import DB

class DBPersistenceManager:

   def __init__(self, config):
      db_cfg = config["db"]
      self.db = DB(db_cfg["url"], db_cfg["port"], db_cfg["db_name"])


