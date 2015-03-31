import unittest
from api import api

class ApiTest(unittest.TestCase):

   def setUp(self):
      self.app = api.app.test_client()

   def test_base_api_url(self):
      self.assertEqual( api.url_for_endpoint('pippo') , '/api/v1.0/pippo/' )

   def test_base_api_url_with_params(self):
      self.assertEqual( api.url_for_endpoint('pippo/<float:age>') , '/api/v1.0/pippo/<float:age>/' )

   def test_buildings_uri(self):
      response = self.app.get('/api/v1.0/buildings/')
      self.assertEqual(response.status_code,200)

   def test_buildings_by_id_with_valid_bid(self):
      response = self.app.get('/api/v1.0/buildings/1245/')
      self.assertEqual(response.status_code,200)

   def test_buildings_by_id_with_invalid_bid(self):
      response = self.app.get('/api/v1.0/buildings/pippo/')
      self.assertEqual(response.status_code,400)

   def test_buildings_near_with_params(self):
      response = self.app.get('/api/v1.0/buildings/near/2.342141/2.443/')
      self.assertEqual(response.status_code,200)

   def test_buildings_near_with_bad_request(self):
      response = self.app.get('/api/v1.0/buildings/near/pippo/pluto/')
      self.assertEqual(response.status_code,404)
