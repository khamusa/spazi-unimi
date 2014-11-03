import unittest
import io
from csv_reader import CSVReader

class CSVReaderTest(unittest.TestCase):
   def test_header_reader(self):
      csv = CSVReader(io.StringIO("codice,tipologia,pippo\na,b,c\nd,e,f"))
      self.assertTrue("codice" in csv.header)
      self.assertTrue("tipologia" in csv.header)
      self.assertTrue("pippo" in csv.header)
      self.assertTrue("a" not in csv.header)
      self.assertTrue("b" not in csv.header)
      self.assertTrue("c" not in csv.header)
      self.assertTrue("d" not in csv.header)
      self.assertTrue("e" not in csv.header)
      self.assertTrue("f" not in csv.header)

   def test_header_reader_trimm(self):
      csv = CSVReader(io.StringIO(" codice , tipologia   ,   pippo \n  a , b   , c \n d   , e    ,f  "))
      self.assertTrue("codice" in csv.header)
      self.assertTrue("tipologia" in csv.header)
      self.assertTrue("pippo" in csv.header)
      self.assertTrue("a" not in csv.header)
      self.assertTrue("b" not in csv.header)
      self.assertTrue("c" not in csv.header)
      self.assertTrue("d" not in csv.header)
      self.assertTrue("e" not in csv.header)
      self.assertTrue("f" not in csv.header)
