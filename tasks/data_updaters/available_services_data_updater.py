from model import AvailableService

class AvailableServicesDataUpdater:

   def perform_update(self,entities_type, content):
      AvailableService.clean()
      for s in content:
         service = AvailableService(s)
         service.save()
