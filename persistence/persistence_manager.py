import os
class PersistenceManager:

   def write_data(self, obj):
      file_path = self.prepare_file_path(obj)
      with open(file_path, "w") as fp:
         fp.write(self.get_write_data(obj))

   def prepare_file_path(self, obj = None):
      """Composes a file_path for saving obj.

      The resulting filepath will have the following format:
         base_write_path/file_format.extension"""

      base_building_path = self.get_base_write_path(obj)

      if not os.path.exists(base_building_path):
         os.makedirs(base_building_path)

      filename = self.get_filename_format(obj)

      extension = self.get_file_extension(obj)
      extension = (extension and "."+extension) or ""
      return os.path.join(base_building_path, filename + extension)


   def get_base_write_path(self, obj = None):
      """Given an object, must return a base path for writing it to filesystem

      Documentation purposes only, must be overriden by subclasses"""
      pass

   def get_filename_format(self, obj = None):
      """Given an object, must return a filename for writing it to filesystem

      Documentation purposes only, must be overriden by subclasses"""
      pass

   def get_file_extension(self, obj = None):
      """Given an object, must return a file extension for writing it to filesystem

      Documentation purposes only, must be overriden by subclasses"""
      pass
