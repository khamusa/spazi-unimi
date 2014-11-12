import json
import os
from .persistence_manager import PersistenceManager

class JSONPersistenceManager(PersistenceManager):

   def __init__(self, config):
      self._cm = config

   def floor_write(self, floor):
      self.write_data(floor)

   def get_write_data(self, obj = None):
      indent = (self._cm["env"] == 'development' or None) and self._cm["json_indent"]
      return json.dumps(
                  obj.to_serializable(),
                  indent = indent
               )

   def get_base_write_path(self, obj = None):
      return os.path.join(
            self._cm["folders"]["data_dxf_preprocessed_output"],
            obj.building_name
            )

   def get_filename_format(self, obj = None):
      return self._cm["filepaths"]["preprocessed_floor_format"].format(
         building_name  = obj.building_name,
         floor_name     = obj.floor_name
      )

   def get_file_extension(self, obj = None):
      return "json"
