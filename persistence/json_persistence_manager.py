import json
import os
from .persistence_manager import PersistenceManager

class JSONPersistenceManager(PersistenceManager):

   def __init__(self, config):
      self._cm = config

   # Deprecated (era usato prima per generare dei JSON con le info ottenute
   # da un file DXF, ma adesso vanno inviate direttamente al DB)
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
            obj.building_id
            )

   def get_filename_format(self, obj = None):
      return self._cm["filepaths"]["preprocessed_floor_format"].format(
         building_id    = obj.building_id,
         f_id           = obj.f_id
      )

   def get_file_extension(self, obj = None):
      return "json"
