import unittest, json
from model import AvailableService

class AvailableServicesModelTest(unittest.TestCase):

   def test_available_service_from_json(self):
      json = {'it': 'italian text', 'en': 'english text', 'key': 'Aula Seminari - Magna - Lauree'};
      service = AvailableService(json)
      self.assertEquals(service.key,'Aula Seminari - Magna - Lauree')
      self.assertEquals(service.langs,{'en','it'})
      self.assertEquals(service['it'],'italian text')
      self.assertEquals(service['en'],'english text')

   def test_available_service_from_json_plus(self):
      json = {'it': 'italian text', 'en': 'english text', 'de': 'german text' , 'key': 'Aula Seminari - Magna - Lauree'}
      service = AvailableService(json)
      self.assertEquals(service.key,'Aula Seminari - Magna - Lauree')
      self.assertEquals(service.langs,{'it','de','en'})
      self.assertEquals(service['it'],'italian text')
      self.assertEquals(service['en'],'english text')
      self.assertEquals(service['de'],'german text')



