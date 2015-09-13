from .odm            import ODMModel
from persistence     import MongoDBPersistenceManager
import re

class AvailableService(ODMModel):
   """
   The AvailableService class implements a single service used
   for filter buildings and floors
   """

   def __init__(self, new_attrs = None):
      super().__init__(new_attrs)
      self.key    = new_attrs['key']
      self.langs  = {l for l in new_attrs if l!='key'}


   @classmethod
   def services(klass):
      collection  = list(klass.get_collection().find())
      services    = []

      for s in collection:
         services.append( AvailableService(s) )

      return services
