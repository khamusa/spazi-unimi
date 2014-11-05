from csv_reader import CSVReader

class CSVDataUpdater:
   def __init__(self, headers_dict):
      self._valid_headers = { k : set(v) for k, v in headers_dict.items() }

   def perform_update(self, filename):
      reader   = CSVReader(filename)
      csv_type = self.infer_csv_from_header(reader.header)

   def infer_csv_from_header(self, effective_header):
      is_in_effective_header = lambda s: s in is_in_effective_header

      for valid_key in self._valid_headers:
         if (self._valid_headers[valid_key].issubset(effective_header)):
            return valid_key

      return None
