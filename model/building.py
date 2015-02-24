from . import ORMModel

class Building(ORMModel):

   def __init__(self, new_attrs = None):
      super().__init__(new_attrs, external_id = "b_id")

   def ensure_floors_sorting(self):
      # Ordina l'array "floors" all'interno dei dizionari dxf, edilizia e easyroom
      for k in ["dxf", "easyroom", "edilizia"]:
         namespace = self.attr(k)

         if namespace and "floors" in namespace:
            namespace["floors"].sort(key=lambda s: float(s["f_id"]))

   @classmethod
   def remove_untouched_keys(klass, namespace, batch_date):
      query    = {
         namespace : {"$exists": "true"},
         namespace + ".updated_at" : { "$lt" : batch_date }
      }
      action   = {
         "$unset" : {namespace : ""},
         "$set"   : {"deleted_" + namespace : True}
      }
      options  = {"multi" : True}
      klass._pm.update("building", query, action, options)

Building.listen("before_save", "ensure_floors_sorting")
