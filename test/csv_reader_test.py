import unittest
import io
from utils.csv_reader import CSVReader

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

   def test_column_filter(self):
      available_headers = {
         "edilizia":{
            "rooms"              : ["codice", "filipippo", "pluto"],
            "room_categories"    : ["verdi", "codice", "gialli"],
            "buildings"          : ["codice", "pippo"]
         },
         "easyroom":{
            "buildings"          : ["b_id", "address", "building_name", "n_floors"],
            "rooms"              : ["r_id", "b_id", "room_name", "capacity", "floor", "accessibility", "equipments" ]
         }
      }

      csv = CSVReader(io.StringIO("codice,tipologia,pippo\na,b,c\nd,e,f"), available_headers)

      self.assertTrue("tipologia" not in csv.header)
      self.assertTrue("pippo" in csv.header)
      self.assertTrue("codice" in csv.header)

      self.assertTrue("pippo" in csv.content[0])
      self.assertTrue("tipologia" not in csv.content[0])
      self.assertTrue("codice" in csv.content[0])
      self.assertTrue("pippo" in csv.content[1])
      self.assertTrue("tipologia" not in csv.content[1])
      self.assertTrue("codice" in csv.content[1])

   def test_header_inference(self):

      headers = {
            "edilizia":{
               "a": ["1", "2", "3"],
               "b": ["4", "5", "6"]
            },
            "easyroom":{
               "a": ["1", "2", "7"],
               "b": ["4", "5", "8"]
            }
         }

      infer = lambda di: CSVReader._infer_csv_from_header(headers, di)

      self.assertEqual( ("edilizia","b") , infer({"4", "5", "6"}) )
      self.assertEqual( ("edilizia","b") , infer({"4", "2", "5", "6"}) )

      self.assertEqual( ("easyroom","a") , infer({"1", "2", "7", "6"}) )
      self.assertEqual( ("easyroom","a") , infer({"2", "7", "1", "6" , "10"}) )

      self.assertEqual( ("easyroom","b") , infer({"8", "5", "4", "10"}) )

      self.assertEqual( ("edilizia","a") , infer({"1", "2", "22", "3"}) )

      self.assertEqual((None, None), infer({"1", "6" , "10"}))
      self.assertEqual((None, None), infer({"22", "10" , "33"}))
      self.assertEqual((None, None), infer({"1", "3", "10" }))

