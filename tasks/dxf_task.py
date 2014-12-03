from tasks.dxf.dxf_reader import DxfReader

class DXFTask:

   def __init__(self, config, persistence):


   def perform_updates_on_files(self,files):
      for filename in files:
         self.perform_update(filename)

   def perform_update(self, file):
      rm = re.match("(\w+)_(\w+)\.dxf", os.path.basename(filename))
      if rm is None:
         print("File name format error: ", filename)
         continue

      dx = DxfReader(filename, rm.group(1), rm.group(2))
      persistence.floor_write(dx.floor)
