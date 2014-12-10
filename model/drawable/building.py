from . import ORMModel

class Building(ORMModel):

   @classMethod
   def find_or_create_by_bid(self, b_id):
      res = self.find(b_id)
      if not res:
         res = new_from_template(b_id)

      return res


   b = Building.find()
   b.attrs()

   b.attrs({"pippo" : pluto})
