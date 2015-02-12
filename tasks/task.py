import shutil, os
from utils.logger import Logger

class Task():
   """
   Base Task class, supplies the common scaffolding structure with hook methods
   to be implemented/supplied by superclasses.
   """

   def perform_updates_on_files(self,files):
      """
      Given a list of files, dispatch the update and file backup procedures.
      Handles eventual errors raised and logs the process.

      Arguments:
      - files: a list of files to be processed.

      Returns None.
      """
      for filename in files:
         with Logger.info("Processing file " + filename):
            try:
               self.perform_update(filename)
               self.perform_file_backup(filename)
            except FileUpdateException as e:
               Logger.error(e.msg)
            else:
               Logger.success("File processing complete.")


   def perform_file_backup(self, source_filepath):
      """
      Handles common logic for performing file backup. Subclasses must provide
      the appropriate hooks in order for the backup process to work.

      In detail, subclasses must implement get_backup_filepath.

      Return None
      """
      try:
         target_filepath = self.get_backup_filepath(source_filepath)
         if target_filepath:
            shutil.copy(source_filepath, target_filepath)
      except Exception as e:
         pass

   def get_backup_filepath(self, filename):
      """
      Hook method to be replaced by subclasses. Must return the backup filepath
      for a file being updated.
      """
      return ""


class FileUpdateException(Exception):
   """
   Raised by update procedures when it is not possible to perform the update.
   """
   def __init__(self, message):
      self.msg = message
