import csv

class CSVReader:
   def __init__(self, csvfile, columns = None):
      try:
         dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters = '\n')
      except csv.Error as e:
         dialect = "excel"

      csvfile.seek(0)
      reader = csv.reader(csvfile, dialect)

      it = iter(reader)
      self.header = [s.strip() for s in next(it)]
      self.content = []
      for line in it:
         self.content.append({ c: l.strip() for c,l in zip(self.header, line) if columns is None or c in columns})

      self.header = [ h for h in self.header if columns is None or h in columns ]


   def apply_column_filter(self, valid_headers):
      # TODO filtrare già nell'init
      """ Function for filter valid headers and column in content """
      self.header = [ s for s in self.header if s in valid_headers ]

      self.content = [
         { k: v for k, v in el.items() if k in self.header }
         for el in self.content
      ]

