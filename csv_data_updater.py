from csv_reader import CSVReader

class InvalidCSVHeaderError(RuntimeError):
   pass

class CSVDataUpdater:
   def __init__(self, headers_dict, persistence_manager):
      self._valid_headers = { k : set(v) for k, v in headers_dict.items() }
      self._pm = persistence_manager

   def perform_update(self, filename, reader_class = CSVReader):
      reader   = reader_class(filename)
      csv_type = self.infer_csv_from_header(reader.header)

      if csv_type == None:
         raise InvalidCSVHeaderError("L'intestazione del file CSV non è valida")

      {
         "rooms"           : lambda s: None,
         "buildings"       : lambda s: None,
         "room_categories" : self.update_room_categories

      }[csv_type](reader.content)


   def infer_csv_from_header(self, effective_header):
      is_in_effective_header = lambda s: s in is_in_effective_header

      for valid_key in self._valid_headers:
         if (self._valid_headers[valid_key].issubset(effective_header)):
            return valid_key

      return None

   def update_room_categories(self, categories):
      self._pm.insert_room_categories(categories)
