from tasks.dxf.dxf_reader import DxfReader
from tasks.task import Task, FileUpdateException
from utils.logger import Logger
from model.building import Building
from decimal import Decimal
import shutil, os, re

class DXFTask(Task):

   def __init__(self, config):
      self._backup_folder  = config["folders"]["data_dxf_sources"]

   def perform_update(self, dxf_file):

      # Valido che il file su cui lavoriamo sia effettivamente un DXF
      rm = re.match(".+\.dxf", os.path.basename(dxf_file), re.I)
      if rm is None:
         raise FileUpdateException("The supplied file extension is not DXF.")

      # Leggo il file DXF su cui stiamo lavorando
      try:
         self.dx = DxfReader(dxf_file)
      except Exception:
         raise FileUpdateException("There was an error reading the DXF file.")

      floor = self.dx.floor;
      if not floor:
         raise FileUpdateException("No floor found")

      # Troviamo un building_id valido (sequenzad di digiti)
      floor.b_id = self.sanitize_b_id(floor.b_id)

      if not floor.b_id:
         raise FileUpdateException("It was not possible to identify the building id.")

      # Trova un building su cui lavorare, cercando per diverse strategie:
      # Un building salvo con b_id corretto, con un legacy_building, oppure
      # un nuovo building creato con il building_id estratto dal floor.
      building = (
                  Building.find(floor.b_id) or
                  Building.find_by_field("merged.l_b_id", floor.b_id) or
                  Building( {"_id": floor.b_id} )
                  )

      # Pulisce i dati ed esegue il vero salvataggio sul DB
      self.save_floor(building, floor)
      # TODO: CALL A DATAMERGER

   def get_backup_filepath(self, filename):
      backup_file_folder  = os.path.join(self._backup_folder, self.dx.fl9oor.b_id)

      if not os.path.exists( backup_file_folder ):
         os.mkdir(backup_file_folder)

      return os.path.join(backup_file_folder ,self.dx.floor.b_id+'_'+self.dx.floor.f_id+'.dxf')

   def sanitize_b_id(self, b_id):
      """Dalla string che identifica il building estrae il suo ID"""
      rm = re.match("(\d{4,})", b_id)
      return rm and rm.group(0)

   def save_floor(self, building, floor):
      """Dato un oggetto di tipo Building e un oggetto di tipo Floor ottenuto a partire
      da un file DXF, pulisce i dati e salva il building sul DB"""

      new_floor = floor.to_serializable()
      del new_floor["b_id"]

      # Non vogliamo cancellare quanto c'è nel database, soltanto lo stesso floor
      dxf         = building.attr("dxf") or {}
      floors      = dxf.get("floors", [])

      # Se il floor corrente esiste gia' nel dataase, vogliamo sostituirlo
      for k, f in enumerate(floors):
         if f["f_id"] == floor.f_id:
            del floors[k]

      floors.append(new_floor)

      dxf["floors"] = floors
      building.attr("dxf", dxf)
      building.save()

