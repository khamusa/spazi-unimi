from model                    import Building
from utils.logger             import Logger
from tasks.data_merger        import DataMerger
from datetime                 import datetime
import itertools

class BuildingDataUpdater():
   """
   The BuildingDataUpdater class implements the behavior of updating and
   inserting building information on the Database. It has no direct reference
   to PersistenceManager, interacting with the Database only indirectly, through
   the usage of the appropriate models.

   The main entry point is the method update_buildings called by the appropriate
   Task Handler (mainly CSVTask).
   """

   def update_buildings(self, buildings):
      """
      Perform an update of building data on Database.

      Arguments:
      - buildings: a list of dictionaries, where each dictionary represents
      a building.

      Does not return (None).

      Example of a building retrived from an Edilizia csv file:
      {
         'b_id'      : '11030',
         'address'   : 'Milano - Via Francesco Sforza 44',
         'lon'       : '9.193670',
         'lat'       : '45.458065',
         'l_b_id'    : '5471'
      }

      If a building with the same b_id exists on the database, hence it will
      be updated, otherwise it will be replaced.
      """
      namespace   = self.get_namespace()
      batch_date  = datetime.now()

      for b in buildings:
         b_id     = b.get("b_id", "")
         l_b_id   = b.get("l_b_id", "")

         if not self._is_valid_b_id(b_id):
            if self._is_valid_b_id(l_b_id):
               Logger.warning(
                  "Invalid building id: \"{}\"".format(b_id),
                  "- legacy id", l_b_id, "will be used instead."
                  )
               b["b_id"]   = l_b_id
            else:
               Logger.error(
                  "Building discarded:",
                  "Invalid building id", b_id,
                  "and no valid legacy id is present"
                  )
               continue

         building             = self.find_building_to_update(b)
         namespaced_attr      = building.get(namespace, {})
         building[namespace]  = namespaced_attr
         namespaced_attr.update(b)

         deleted_key = "deleted_" + namespace
         if deleted_key in building:
            del building[deleted_key]

         with Logger.info("Processing "+str(building)):
            edilizia = building.get('edilizia')
            easyroom = building.get('easyroom')
            dxf      = building.get('dxf')

            building['merged']            = DataMerger.merge_building(edilizia, easyroom, dxf)
            building['updated_at']        = batch_date
            namespaced_attr["updated_at"] = batch_date
            building.save()

      # Make sure the current update is performed as a perfect snapshot,
      # removing also "untouched" buildings
      n_removed, b_removed = Building.remove_untouched_keys(namespace, batch_date)
      b_removed            = [ b["b_id"] for b in b_removed ]

      if b_removed:
         Logger.info(
                  n_removed,
                  "previously existing buildings are not present",
                  "in this snapshot:",
                  ", ".join(b_removed)
                  )

         n_destroyed, b_destroyed   = Building.remove_deleted_buildings()
         b_destroyed                = [ b["b_id"] for b in b_destroyed ]
         if n_destroyed:
            Logger.info(
                     n_destroyed,
                     "buildings were effectively removed from database",
                     "since no data source affirms its existence:",
                     ", ".join(b_destroyed)
                     )

   def find_building_to_update(self, building_dict):
      """
      Finds on database or create a Buiding object to be updated with information
      contained by building_dict

      Arguments:
      - building_dict: a dictionary containing the new values to be inserted
      on the building.

      Returns a Building object.

      The default implementation finds the building by its b_id or creates a new
      one if none exists. Subclasses may override this behavior.
      """
      b_id = building_dict.get("b_id", "")

      return Building.find_or_create_by_id(b_id)
