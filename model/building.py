from . import ORMModel

class Building(ORMModel):

   def __init__(self, new_attrs = None):
      super().__init__(new_attrs, external_id = "b_id")

   # TODO - move to superclass
   @classmethod
   def find_or_create_by_bid(self, b_id):
      res = self.find(b_id)
      if not res:
         res = Building({"_id":b_id})

      return res

