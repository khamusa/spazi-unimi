import unittest
from api import api

class ApiTest(unittest.TestCase):

   def setUp(self):
      self.app = api.app.test_client()

   def test_buildings(self):
        rv = self.app.get('/buildings')
