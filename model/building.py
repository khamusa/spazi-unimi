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
      """
      Performs a swipe on database, looking for buildings that haven't been
      touched by the last update action (on batch_date) under the supplied
      namespace. Removes the namespace key on those buildings and set
      a deleted_<namespace> key to the current bach_date.

      Arguments:
      - namespace: a string "edilizia" or "easyroom"
      - batch_date: a datetime object representing the date of the last
      update action of buildings on the supplied namespace

      Returns a tuple (n, buildings), where n is the amount of records
      affected, and buildings is a list of the buildings that have been
      changed. The buildings list reflect the state of those buildings
      BEFORE the update action.
      """
      query       = {
         namespace : {"$exists": True},
         namespace + ".updated_at" : { "$lt" : batch_date }
      }
      buildings   = list(Building.where(query))
      action      = {
         "$unset" : {namespace : ""},
         "$set"   : {"deleted_" + namespace : batch_date}
      }
      options  = {"multi" : True}
      result   = klass._pm.update("building", query, action, options)
      return (result["n"], buildings)

   @classmethod
   def remove_deleted_buildings(klass):
      """
      Performs a swipe on database, erasing buildings that are to be considered
      deleted from the previous update operations.

      A building is "deleted" if it once existed but not anymore according to
      all it's sources.

      Returns a tuple (n, buildings), where n is the amount of records
      affected, and buildings is a list of the buildings that have been
      changed. The buildings list reflect the state of those buildings
      BEFORE the update action.
      """
      query    = {
         "$or" : [
            {
               "edilizia" : {"$exists": False},
               "deleted_easyroom" : {"$exists": True},
            },
            {
               "easyroom" : {"$exists": False},
               "deleted_edilizia" : {"$exists": True}
            }
         ]
      }
      buildings   = list(Building.where(query))
      options     = {"multi" : True}
      result      = klass._pm.remove("building", query, options)
      return (result["n"], buildings)


Building.listen("before_save", "ensure_floors_sorting")
