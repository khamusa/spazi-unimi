import shutil, os
from utils.logger import Logger

class Task():

   def perform_updates_on_files(self,files):
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
      try:
         target_filepath = self.get_backup_filepath(source_filepath)
         if target_filepath:
            shutil.copy(source_filepath, target_filepath)
      except Exception as e:
         pass

   def get_backup_filepath(self, filename):
      return ""


class FileUpdateException(Exception):

   def __init__(self, message):
      self.msg = message
