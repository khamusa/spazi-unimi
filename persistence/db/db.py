import pymongo
import sys

class DB():

   def __init__(self, url, port, dbname):
      self.url    = url
      self.port   = port
      self.dbname = dbname
      try:
         self.client = pymongo.MongoClient(self.url,self.port)
         self.db     = self.client[self.dbname]

      except pymongo.errors.ConnectionFailure:
         sys.exit("Connection error")

   def __getitem__(self, key):
      return self.db[key]
