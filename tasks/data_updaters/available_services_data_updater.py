from model import AvailableService

class AvailableServicesDataUpdater:
   """
   The AvailableServicesDataUpdater class implements the interface
   for query the available services used for filter buildings and floors
   """

   def perform_update(self,entities_type, content):
      AvailableService.clean()
      for s in content:
         service = AvailableService(s)
         service.save()
