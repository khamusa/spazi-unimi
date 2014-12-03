from utils.csv_reader import CSVReader
from utils.logger import Logger
from persistence.db.mongo_db_persistence_manager import MongoDBPersistenceManager

class CSVTask:
   def __init__(self, config, persistence, reader_class = CSVReader):
      """Init a CSVTask """
      headers_dict         = config["csv_headers"]
      self._persistence    = persistence
      self._reader_class   = reader_class

      self._valid_headers  = {}

      for key in headers_dict :
         self._valid_headers[key] = { k : set(v) for k, v in headers_dict[key].items() }


   def infer_csv_from_header(self, effective_header):
      result = None

      for service in self._valid_headers:
         for entities_type in self._valid_headers[service]:
            if (self._valid_headers[service][entities_type].issubset(effective_header)):
               result = (service,entities_type)
               return result

      if result == None:
         Logger.error("Invalid CSV header file")

      return result

   def perform_update(self, csv_file):
      reader   = self._reader_class(csv_file)
      res      = self.infer_csv_from_header(reader.header)

      if res == None:
         return

      (service, entities_type) = res




