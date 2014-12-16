from utils.csv_reader import CSVReader
from tasks import Task, FileUpdateException, EdiliziaDataUpdater
from utils.logger import Logger
import os, re

class CSVTask(Task):
   def __init__(self, config, reader_class = CSVReader):
      """Init a CSVTask """
      self._valid_headers  = config["csv_headers"]
      self._backup_folder  = config["folders"]["data_csv_sources"]
      self._reader_class   = reader_class

   def perform_update(self, filename):
      rm = re.match(".+\.csv", os.path.basename(filename), re.I)
      if rm is None:
         raise FileUpdateException("The supplied file extension is not CSV.")

      """Read csv file and validate it's format and type"""
      reader = self._read_csv_file(filename)
      self._validate_csv(reader)

      """This is where the real update takes place"""
      self._dispatch_update(reader.service, reader.entities_type, reader.content)

      """Used by backup logic (get_backup_filepath)"""
      backup_filename      = reader.service + '_' + reader.entities_type + ".csv"
      self.backup_filepath = os.path.join(self._backup_folder, backup_filename)

   def _validate_csv(self, reader):
      """Ensure a csv file is valid"""
      if not reader.service :
         raise FileUpdateException("Invalid CSV header file")

      if not reader.content :
         raise FileUpdateException("CSV file contains only header")

   def _read_csv_file(self, filename):
      """Wraps the open so that it becomes easily mockable. Yeah, we know.. xD"""
      try:
         with open(filename) as csv_file:
            return self._reader_class(csv_file, self._valid_headers)
      except Exception:
         raise FileUpdateException("There was an error reading the CSV file.")

   def _dispatch_update(self, service, entities_type, content):
      """Requests the appropriate class for the appropriate update service,
      according to the inferred csv type"""
      if (service == "edilizia"):
         updater = EdiliziaDataUpdater()
         updater.perform_update(entities_type, content)
      elif (service == "easyroom"):
         raise FileUpdateException("Service "+ service +" not yet implemented")
      else:
         raise FileUpdateException("Unknown service type: "+str(service))

   def get_backup_filepath(self, filename):
      """Hook method to implement file backup (logic defined in super Task class)"""
      return self.backup_filepath



