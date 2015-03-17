from tasks.dxf.dxf_reader     import DxfReader
from tasks.task               import Task, FileUpdateException
from tasks.dxf_data_updater   import DXFDataUpdater
import os, re

class DXFTask(Task):
   """
   Responsible for handling update of DXF files. Must be initialized with a
   config manager from which to retrive the dxf backup folder.
   """

   def __init__(self, config):
      """
      Arguments:
      config: a dictionary-like object containing the source dxf backup path
      (view code)
      """
      self._backup_folder  = config["folders"]["data_dxf_sources"]

   def perform_update(self, dxf_file):
      """
      Main entry point, called once for every dxf file to be updated.

      Arguments:
      - dxf_file: full path to dxf file to process.

      Returns: None
      Throws FileUpdateException in case of unsolvable errors.

      Called by parents perform_update_on_files method.
      """
      # Valido che il file su cui lavoriamo sia effettivamente un DXF
      rm = re.match(".+\.dxf", os.path.basename(dxf_file), re.I)
      if rm is None:
         raise FileUpdateException("The supplied file extension is not DXF.")

      # Leggo il file DXF su cui stiamo lavorando
      try:
         self.dx = DxfReader(dxf_file)
      except FileUpdateException:
         raise
      except Exception as e:
         raise FileUpdateException("There was an unknown error reading the DXF file: "+ str(e))

      floor = self.dx.floor;
      if not floor:
         raise FileUpdateException("No floor found")

      # Troviamo un building_id valido (sequenzad di digiti)
      floor.b_id = self.sanitize_b_id(floor.b_id)

      if not floor.b_id:
         raise FileUpdateException("It was not possible to identify the building id.")

      updater = DXFDataUpdater()

      # Trova un building su cui lavorare, cercando per diverse strategie:
      # Un building salvo con b_id corretto, con un legacy_building, oppure
      # un nuovo building creato con il building_id estratto dal floor.
      building = updater.find_building_to_update({ "b_id": floor.b_id })

      # Pulisce i dati ed esegue il vero salvataggio sul DB
      updater.save_floor(building, floor)

      backup_filename      = self.get_backup_filepath(dxf_file)
      self.backup_filepath = os.path.join(backup_filename)

   def get_backup_filepath(self, filename):
      """
      Given a source filename, returns a full path for saving a backup file.

      Arguments:
      - filename: a string representing the source filename (with extension)

      Returns: a string representing the destination backup path
      (without filename).

      Called by parent class (method perform_file_backup).
      """
      backup_file_folder  = os.path.join(self._backup_folder, self.dx.floor.b_id)

      if not os.path.exists( backup_file_folder ):
         os.mkdir(backup_file_folder)

      return os.path.join(backup_file_folder ,self.dx.floor.b_id+'_'+self.dx.floor.f_id+'.dxf')

   def sanitize_b_id(self, b_id):
      """
      Sanitizes and validate the string identifying a building.

      Arguments:
      - b_id: a string representing a possible building id. Example: 5830_1p

      Returns: a clean and digit-only version of the b_id. Example: 5830
      """
      rm = re.match("(\d{4,})", b_id)
      return rm and rm.group(0)

