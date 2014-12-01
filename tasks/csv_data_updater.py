from utils.csv_reader import CSVReader
from utils.logger import Logger

class CSVDataUpdater:
   def __init__(self, headers_dict, persistence, data_merger, reader_class = CSVReader):
      self._valid_headers  = { k : set(v) for k, v in headers_dict.items() }
      self._data_merger    = data_merger
      self._persistence    = persistence

   def infer_csv_from_header(self, effective_header):
      csv_type = None
      for valid_key in self._valid_headers:
         if (self._valid_headers[valid_key].issubset(effective_header)):
            csv_type = valid_key

      if csv_type == None:
         Logger.error("Invalid CSV header file")

      return csv_type
