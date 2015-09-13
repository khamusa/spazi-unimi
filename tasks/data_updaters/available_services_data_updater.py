from model import AvailableService

class AvailableServicesDataUpdater:
   """
   The AvailableServicesDataUpdater class implements the operations
   for updating the available service collection
   """

   def perform_update(self,entities_type, content):
      AvailableService.clean()
      for s in content:
         service = AvailableService(s)
         service.save()
