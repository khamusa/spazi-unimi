from utils.csv_reader import CSVReader
from .                import Task, FileUpdateException
from .data_updaters   import EdiliziaDataUpdater, EasyroomDataUpdater
import os, re

class CSVTask(Task):
   def __init__(self, config, reader_class = CSVReader):
      """
      Builds a CSVTask object.

      Arguments:
      - config: a config manager reference, from which retrieve csv_headers
      dictionary and csv backup folder.
      - reader_class: Class to be used for reading CSV files.

      """
      self._valid_headers  = config["csv_headers"]
      self._backup_folder  = config["folders"]["data_csv_sources"]
      self._reader_class   = reader_class

   def perform_update(self, csv_filename):
      """
      Main entry point, called once for every csv file to be updated.

      Arguments:
      - csv_filename: full path to csv file to process.

      Returns: None
      Throws FileUpdateException in case of unsolvable errors.

      Called by parents perform_update_on_files method (Task class).
      """
      rm = re.match(".+\.csv", os.path.basename(csv_filename), re.I)
      if rm is None:
         raise FileUpdateException("The supplied file extension is not CSV.")

      # Read csv file and validate it's format and type
      reader = self._read_csv_file(csv_filename)
      self._validate_csv(reader)

      # This is where the real update takes place
      self._dispatch_update(reader.service, reader.entities_type, reader.content)

      # Used by backup logic (get_backup_filepath)
      backup_filename      = reader.service + '_' + reader.entities_type + ".csv"
      self.backup_filepath = os.path.join(self._backup_folder, backup_filename)

   def _validate_csv(self, reader):
      """
      Ensure a csv file is valid

      Arguments:
      - reader: The CSVReader object used

      Returns None but raises FileUpdateException in case of invalid CSV Files.
      """
      if not reader.service :
         raise FileUpdateException("Invalid CSV header file")

      if not reader.content :
         raise FileUpdateException("CSV file contains only header")

   def _read_csv_file(self, filename):
      """
      Reads a CSV file. The main utility of this method is for code readibility and
      is to ensure the file opening becomes easily mockable.

      Returns an instance of CSVReader that contains the read data.

      Raises FileUpdateException in case of errors reading the file.
      """
      try:
         with open(filename) as csv_file:
            return self._reader_class(csv_file, self._valid_headers)
      except Exception:
         raise FileUpdateException("There was an error reading the CSV file.")

   def _dispatch_update(self, service, entities_type, content):
      """
      As the name implies, it dispatches the update of the content of a CSV file
      by choosing the correct DataUpdater according to the CSV type (service).

      Returns None
      Raises FileUpdateException if service is unknown.
      """
      if (service == "edilizia"):
         updater = EdiliziaDataUpdater()
      elif (service == "easyroom"):
         updater = EasyroomDataUpdater()
      else:
         raise FileUpdateException("Unknown service type: "+str(service))

      updater.perform_update(entities_type, content)

   def get_backup_filepath(self, filename):
      """
      Given a source filename, returns a full path for saving a backup file.

      Arguments:
      - filename: a string representing the source filename (with extension)

      Returns: a string representing the destination backup path
      (without filename).

      Called by parent class (method perform_file_backup).
      """
      return self.backup_filepath



