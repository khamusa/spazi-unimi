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

   def test_row_reader(self):
      csv = CSVReader(io.StringIO("codice,tipologia,pippo\na,b,c\nd,e,f"))
      self.assertEqual("a", csv.content[0]["codice"])
      self.assertEqual("b", csv.content[0]["tipologia"])
      self.assertEqual("c", csv.content[0]["pippo"])
      self.assertEqual("d", csv.content[1]["codice"])
      self.assertEqual("e", csv.content[1]["tipologia"])
      self.assertEqual("f", csv.content[1]["pippo"])

   def test_row_reader_trimm(self):
      csv = CSVReader(io.StringIO(" codice , tipologia   ,   pippo \n  a , b   , c \n d   , e    ,f  "))
      self.assertEqual("a", csv.content[0]["codice"])
      self.assertEqual("b", csv.content[0]["tipologia"])
      self.assertEqual("c", csv.content[0]["pippo"])
      self.assertEqual("d", csv.content[1]["codice"])
      self.assertEqual("e", csv.content[1]["tipologia"])
      self.assertEqual("f", csv.content[1]["pippo"])

   def test_column_feature(self):
      csv = CSVReader(io.StringIO("codice,tipologia,pippo\na,b,c\nd,e,f"), ["codice", "pippo"])
      self.assertTrue("codice" in csv.header)
      self.assertTrue("tipologia" not in csv.header)
      self.assertTrue("pippo" in csv.header)
      self.assertEqual("a", csv.content[0]["codice"])
      self.assertFalse("tipologia" in csv.content[0])
      self.assertEqual("c", csv.content[0]["pippo"])
      self.assertEqual("d", csv.content[1]["codice"])
      self.assertFalse("tipologia" in csv.content[1])
      self.assertEqual("f", csv.content[1]["pippo"])
