import csv

class CSVReader:
   def __init__(self, csvfile):
      try:
         dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters = '\n')
      except Exception as e:
         dialect = "excel"
      csvfile.seek(0)
      reader = csv.reader(csvfile, dialect)

      it = iter(reader)
      self.header = [s.strip() for s in next(it)]
