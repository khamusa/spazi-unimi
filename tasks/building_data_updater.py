from model                    import Building
from utils.logger             import Logger
from tasks.data_merger        import DataMerger
from datetime                 import datetime

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
      self.batch_date   = datetime.now()

      for b in buildings:
         if not self._validate_building_data(b):
            continue

         building = self.find_building_to_update(b)
         self._mark_building_as_updated(building)

         with Logger.info("Processing "+str(building)):
            self._update_a_building(building, b)

      self._clean_unmarked_buildings()

   def _mark_building_as_updated(self, building):
      """
      When a building is contemplated in an update, ensure it's updated_at
      attributes gets updated, and removes deleted_<source> keys from it
      if it is present.

      This logic is necessary, in conjuction with the logic on
      _clean_unmarked_buildings method to guarantee the consistency of
      the data on database.

      Arguments:
      building - a building being contemplated by the current update batch

      Returns None
      """
      namespace         = self.get_namespace()
      namespaced_attr   = building.attributes_for_source(namespace)

      # If this namespace was previously "deleted", remove the "delete key"
      deleted_key       = "deleted_" + namespace
      if deleted_key in building:
         del building[deleted_key]

      # set batch update date on appropriate keys
      building['updated_at']        = self.batch_date
      namespaced_attr["updated_at"] = self.batch_date

   def _update_a_building(self, building, b_dict):
      """
      Main process of updating a building with the new data contained on b_dict.

      Arguments:
      - building: a Building object on which to perform the data update
      - b_dict: a dictionary containing the new building data

      Return value: None, updates are made in place on the building object.
      """
      namespaced_attr = building.attributes_for_source(self.get_namespace())
      namespaced_attr.update(b_dict)

      self._sanitize_building(building)

      edilizia = building.get('edilizia')
      easyroom = building.get('easyroom')
      dxf      = building.get('dxf')

      floors   = building.get_path("merged.floors")
      building['merged'] = DataMerger.merge_building(edilizia, easyroom, dxf)

      if floors:
         building['merged']['floors'] = floors

      building.save()

   def _clean_unmarked_buildings(self):
      """
      After an update batch is completed, buildings not updated are to be
      considered as "removed" by the supplied data source, and, hence, a logic
      "delete" operation is performed, by adding a delete_<namespace> key
      to the building object.

      A building is completely removed from database if every source that once
      stated it existed now has a deleted_<namespace> key set.

      What this algorithm does is to look for Buildings with updated_at field
      older than this last batch_date (i.e., untouched), and add the logic
      delete key to those buildings. Finally, it looks for buildings that
      had all data logically deleted and removes them physically from DB.

      Return value: None
      """
      # Make sure the current update is performed as a perfect snapshot,
      # removing also "untouched" buildings
      n_removed, b_removed = Building.remove_untouched_keys(
         self.get_namespace(), self.batch_date
      )
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

   def _validate_building_data(self, b_dict):
      """
      Ensure a dictionary containing building information is actually valid
      for updating purposes. The main goal is to validate the presence and
      format of b_id and/or l_b_id.

      If no b_id is present but a l_b_id is valid, it is set as current b_id,
      which ensures the building does not get discarded.

      Arguments:
      - b_dict: a dictionary representing a building

      Return value: True if data is valid, False otherwise
      """
      b_id     = b_dict.get("b_id", "")
      l_b_id   = b_dict.get("l_b_id", "")

      if not Building.is_valid_bid(b_id):
         if Building.is_valid_bid(l_b_id):
            Logger.warning(
               "Invalid building id: \"{}\"".format(b_id),
               "- legacy id", l_b_id, "will be used instead."
               )
            b_dict["b_id"] = l_b_id
         else:
            Logger.error(
               "Building discarded:",
               "Invalid building id", b_id,
               "and no valid legacy id is present"
               )
            return False

      return True

   def _sanitize_building(self, building):
      """
      Intended to be implemented by subclasses if necessary. This method should
      sanitize a building namespace data"""
      pass

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
