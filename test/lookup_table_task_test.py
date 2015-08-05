from tasks import LookupTableTask
import unittest
import os, time, datetime

class LookupTableTaskTest(unittest.TestCase):

   def setUp(self):
      self.ltt = LookupTableTask()

   def test_db_name(self):
      self.assertEqual( self.ltt.db_name() , "rooms_lookup.sqlite" )

   def test_path(self):
      self.assertEqual( self.ltt.db_path() , os.path.join("data","sqlite","rooms_lookup.sqlite") )

   def test_old_db_was_removed(self):
      self.ltt._delete_old_db()

      with self.assertRaises(IOError):
         open(self.ltt.db_path())

   def test_if_db_should_update_db_true(self):
      client_date = datetime.datetime(2015,7,29).timestamp()
      db_date     = datetime.datetime(2015,8,5).timestamp()
      self.assertTrue(self.ltt.client_should_update_db(client_date,db_updated_at=db_date))


   def test_if_db_should_update_db_true_day_before(self):
      client_date = datetime.datetime(2015,8,4).timestamp()
      db_date     = datetime.datetime(2015,8,5).timestamp()
      self.assertTrue(self.ltt.client_should_update_db(client_date,db_updated_at=db_date))


   def test_if_db_should_update_db_false(self):
      client_date = datetime.datetime(2015,8,5).timestamp()
      db_date     = datetime.datetime(2015,8,5).timestamp()
      self.assertFalse(self.ltt.client_should_update_db(client_date,db_updated_at=db_date))

   def test_if_db_should_update_db_false_future(self):
      client_date = datetime.datetime(2020,8,5).timestamp()
      db_date     = datetime.datetime(2015,8,5).timestamp()
      self.assertFalse(self.ltt.client_should_update_db(client_date,db_updated_at=db_date))


