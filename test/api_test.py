import unittest
from api import api

class ApiTest(unittest.TestCase):

   def setUp(self):
      self.app = api.app.test_client()

   def test_base_api_url(self):
      self.assertEqual( api.base_api_url('pippo') , '/api/v1.0/pippo/' )

   def test_buildings_uri(self):
      response = self.app.get('/api/v1.0/buildings/')
      self.assertEqual(response.status_code,200)

   def test_buildings_by_id(self):
      response = self.app.get('/api/v1.0/buildings/1245/')
      self.assertEqual(response.status_code,200)
