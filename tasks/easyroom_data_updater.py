import re
from .data_updater import DataUpdater

class EasyroomDataUpdater(DataUpdater):
   """
   Responsible for handling data updates from source "Edilizia"
   """

   def perform_update(self, entities_type, content ):
      """
      Main entry point, responsible for deciding what procedure to execute
      according to entities_type variable. Behaves as a simple dispatcher.

      Returns None.
      """
      {
         "buildings"       : self.update_buildings,
         "rooms"           : self.update_rooms
      }[entities_type](content)

   def get_namespace(self):
      """
      The namespace simbolizes the part of document to be updated on database.

      Return value: a string representing the namespace.

      Hook method used by parent DataUpdater class.
      """
      return "easyroom"

   def _is_valid_b_id(self, b_id):
      """
      Determines wether or not b_id is a valid building identifier according to
      the current data source policies.

      Return value: True o False

      Hook method used by parent DataUpdater class
      """
      return b_id and re.match("^\d\d\d\d\d$", b_id)

   def sanitize_room(self, room):
      """
      Sanitizes a room ensuring it is valid and correctly formatted.

      Arguments:
      - room: a dictionary containing information of a room to be inserted or
      updated into database

      Return value: a reference to a dictionary contianing the sanitized info.

      Hook method called by parent DataUpdater class for every room to be
      updated.
      """
      r_id = room.get("r_id", "")
      r_id = ("#" in r_id) and r_id.split("#")[1] or r_id
      room["r_id"] = r_id

      return super().sanitize_room(room)
