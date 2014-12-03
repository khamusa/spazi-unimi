from tasks.dxf.dxf_reader import DxfReader
from utils.logger import Logger
import shutil, os, re

class DXFTask:

   def __init__(self, config, persistence):
      self._persistence    = persistence
      self._backup_folder  = config["folders"]["data_dxf_sources"]


   def perform_updates_on_files(self,files):
      for filename in files:
         self.perform_update(filename)

   def perform_update(self, dxf_file):
      Logger.info("Processing file: " + dxf_file)

      rm = re.match(".+\.dxf", os.path.basename(dxf_file), re.I)
      if rm is None:
         Logger.error("The supplied file extension is not DXF.")
         return

      try:
         dx = DxfReader(dxf_file)
      except Exception:
         Logger.error("File processing was not completed: " + dxf_file)
         return

      if( dx.floor ):
         self._persistence.floor_write(dx.floor)
         Logger.info("Completed - {} rooms founded in: {}".format(dx.floor.n_rooms, dxf_file))

         backup_file_folder  = os.path.join(self._backup_folder,dx.floor.building_name)

         if not os.path.exists( backup_file_folder ):
            os.mkdir(backup_file_folder)

         backup_filename = os.path.join(backup_file_folder ,dx.floor.building_name+'_'+dx.floor.floor_name+'.dxf')
         shutil.copy(dxf_file, backup_filename )

      else:
         Logger.error("File processing was not completed ( no floor found ): " + dxf_file)

