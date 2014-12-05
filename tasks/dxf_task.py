from tasks.dxf.dxf_reader import DxfReader
from tasks.task import Task, FileUpdateException
from utils.logger import Logger
import shutil, os, re

class DXFTask(Task):

   def __init__(self, config, persistence):
      self._persistence    = persistence
      self._backup_folder  = config["folders"]["data_dxf_sources"]

   def perform_update(self, dxf_file):
      rm = re.match(".+\.dxf", os.path.basename(dxf_file), re.I)
      if rm is None:
         raise FileUpdateException("The supplied file extension is not DXF.")

      try:
         self.dx = DxfReader(dxf_file)
      except Exception:
         raise FileUpdateException("There was an error reading the DXF file.")

      if not self.dx.floor:
         raise FileUpdateException("No floor found")

      self._persistence.floor_write(self.dx.floor)


   def get_backup_filepath(self, filename):
      backup_file_folder  = os.path.join(self._backup_folder, self.dx.floor.building_name)

      if not os.path.exists( backup_file_folder ):
         os.mkdir(backup_file_folder)

      return os.path.join(backup_file_folder ,self.dx.floor.building_name+'_'+self.dx.floor.floor_name+'.dxf')
