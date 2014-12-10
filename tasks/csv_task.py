from utils.csv_reader import CSVReader
from tasks.task import Task, FileUpdateException
from utils.logger import Logger
from persistence.db.mongo_db_persistence_manager import MongoDBPersistenceManager
import os, re

class CSVTask(Task):
   def __init__(self, config, persistence, reader_class = CSVReader):
      """Init a CSVTask """
      headers_dict         = config["csv_headers"]
      self._backup_folder  = config["folders"]["data_csv_sources"]
      self._persistence    = persistence
      self._reader_class   = reader_class
      self._valid_headers  = {}

      for key in headers_dict :
         self._valid_headers[key] = { k : set(v) for k, v in headers_dict[key].items() }


   def infer_csv_from_header(self, effective_header):
      for service in self._valid_headers:
         for entities_type in self._valid_headers[service]:
            if (self._valid_headers[service][entities_type].issubset(effective_header)):
               return (service, entities_type)

      return None

   def perform_update(self, filename):
      rm = re.match(".+\.csv", os.path.basename(filename), re.I)
      if rm is None:
         raise FileUpdateException("The supplied file extension is not CSV.")

      with open(filename) as csv_file:
         reader   = self._reader_class(csv_file)

      res = self.infer_csv_from_header(reader.header)

      if res == None:
         raise FileUpdateException("Invalid CSV header file")

      if not reader.content :
         raise FileUpdateException("CVS file contains only header")

      (service, entities_type)   = res
      self._dispatch_update(service, entities_type, reader.content)

      """Used by backup logic (get_backup_filepath)"""
      self.backup_filepath       = os.path.join(self._backup_folder,service + '_' + entities_type + ".csv")

   def _dispatch_update(self, service, entities_type, content):
      if (service == "edilizia"):
         updater = EdiliziaDataUpdater()
         updater.perform_update(entities_type, content)
      elif (service == "easyroom"):
         raise FileUpdateException("Service "+ service +" not yet implemented")
      else:
         raise FileUpdateException("Unknown service type: "+str(service))

   def get_backup_filepath(self, filename):
      """Hook method to implement file backup (logic defined in super Task class)"""
      return self.backup_filepath



