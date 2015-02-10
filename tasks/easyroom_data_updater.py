import re
from .data_updater import DataUpdater

class EasyroomDataUpdater(DataUpdater):

   def perform_update(self, entities_type, content ):
      {
         "buildings"       : self.update_buildings,
         "rooms"           : self.update_rooms
      }[entities_type](content)

   def get_namespace(self):
      """Hook method used by parent DataUpdater class"""
      return "easyroom"

   def _is_valid_b_id(self, b_id):
      """Hook method used by parent DataUpdater class"""
      return b_id and re.match("^\d\d\d\d\d$", b_id)

   def get_floor_key(self):
      """Hook method used by parent DataUpdater class"""
      return "l_floor"

   def sanitize_room(self, room):
      """Richiamato dalla classe padre per ogni stanza da inserire nel DB"""
      r_id = room.get("r_id", "")
      r_id = ("#" in r_id) and r_id.split("#")[1] or r_id
      room["r_id"] = r_id

      return super().sanitize_room(room)
