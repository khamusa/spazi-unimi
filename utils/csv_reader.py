import csv
from utils.myfunctools import subtract_dict

class CSVReader:

   def __init__(self, csvfile, possible_headers = None):
      self._read_file(csvfile)

      # Find csv_type and apply filters if necessary
      self.service, self.entities_type = (
         CSVReader._infer_csv_from_header(possible_headers, self.header)
         )

      if possible_headers:
         self._apply_columns_filter(possible_headers)


   def _read_file(self, csvfile):
      """Performs file reading and return a reader object"""
      try:
         dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters = '\n')
      except csv.Error as e:
         dialect = "excel"

      csvfile.seek(0)
      reader = csv.reader(csvfile, dialect)

      # The first iterator iterates over first line, i.e: header
      it                      = iter(reader)
      self.header             = [ s.strip() for s in next(it) ]

      # Populates Content field, we iterate over each additional line
      self.content = []
      for line in it:
         self.content.append(
            {
               c: l.strip() for c, l in zip(self.header, line)
            }
         )


   def _apply_columns_filter(self, possible_headers):
      """Ensure headers contains no leading or trailing spaces, and apply the
      necessary column filters, according to inferred csv type"""

      # If we have been able to infer csv type, we must also apply the filter
      if self.service and self.entities_type:

         valid_headers  = possible_headers[self.service][self.entities_type]
         self.header    = [ s for s in self.header if s in valid_headers ]
         self.content   = [ subtract_dict(c, self.header) for c in self.content ]


   @classmethod
   def _infer_csv_from_header(self, possible_headers, effective_header):
      """Straightforward :D"""

      # Guarantees there will be something "iterable" so no exception is raised
      possible_headers = possible_headers or []

      # Find csv type and returns tuple
      for service in possible_headers:
         for entities_type in possible_headers[service]:
            if (set(possible_headers[service][entities_type]).issubset(effective_header)):
               return (service, entities_type)

      return (None, None)

