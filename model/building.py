from .odm import ODMModel, around_callbacks
import re

class Building(ODMModel):

   def __init__(self, new_attrs = None):
      super().__init__(new_attrs, external_id = "b_id")

   def __str__(self):
      b_id     = self.get("b_id", "?")
      merged   = self.get("merged")
      l_b_id   = (
               self.get("l_b_id") or
               merged and merged.get("l_b_id") or
               self.get("edilizia") and self.get("edilizia").get("l_b_id") or
               "?"
               )
      name     = (
               merged and merged.get("building_name") or
               self.get("easyroom") and
               self.get("easyroom").get("building_name") or
               ""
               )
      address = (
               merged and merged.get("address")
               )

      final_name = address and "("+address+")" or name and "("+name+")"
      my_str   = [
         "Building Id: " + b_id,
         "Legacy id: " + l_b_id,
         final_name
      ]

      return " ".join(my_str)

   def attributes_for_source(self, source):
      """
      Returns a dictionary representing the attributes of this building under
      the supplied namespace (source).

      If the namespace does not exist in the current attributes list, it
      gets created and assigned an empty dictionary, which is returned. A
      listen callback ensures that buildings don't get saved with empty
      dictionaries as source data.

      Attributes:
      - source: a string representing the desired namespace: dxf, edilizia or
      easyroom.

      Return Value: a dictionary
      """

      if source not in self:
         self[source] = {}

      return self.get(source)

   #################
   # CLASS METHODS #
   #################

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
   @around_callbacks
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

   @classmethod
   def is_valid_bid(klass, bid):
      """
      Determines wether or not b_id is a valid building identifier.

      Return value: True o False
      """
      return bid and re.match("^\d{3,5}$", bid.strip())

   @classmethod
   def is_valid_fid(klass, fid):
      """
      Determines wether or not fid is a valid floor identifier

      The current implementation basically checks it's not empty, we may
      in the future add some more validation, but in the present moment it
      doesn't seem necessary.

      Returns True or False.
      """
      return type(fid) is str and fid.strip()

   @classmethod
   def is_valid_rid(klass, rid):
      """
      Validates the supplied room id

      Arguments:
      - rid: a string representing a room id.

      Returns:
      - True if r_id is valid, False otherwise.
      """
      return (
            re.match("^[a-z]+\d+$", rid.lower(), re.I) or
            re.match("^\d{3,}$", rid.lower(), re.I) or
            re.match("^1i\d{3,}$", rid.lower(), re.I)
         )

   #########################
   # CALLBACKS / LISTENERS #
   #########################

   def ensure_floors_sorting(self):
      # Ordina l'array "floors" all'interno dei dizionari dxf, edilizia e easyroom
      for k in ["dxf", "easyroom", "edilizia"]:
         namespace = self.attr(k)

         if namespace and "floors" in namespace:
            namespace["floors"].sort(key=lambda s: float(s["f_id"]))

   def remove_empty_sources(self):
      """
      Ensure buildings don't get saved with empty source attributes.

      Currently called as a before_save filter.
      """
      for source in ["dxf", "edilizia", "easyroom", "merged"]:
         if source in self and not self[source]:
            del self[source]

Building.listen("before_save", "ensure_floors_sorting")
Building.listen("before_save", "remove_empty_sources")
