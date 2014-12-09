from tasks.dxf.floor_inference import FloorInference
import sys, dxfgrabber, shutil, os


if __name__ == "__main__":
   files = sys.argv[1:]

   for i in range(len(files)):
      f = files[i]

      print(i, " - Processing file", os.path.basename(f))

      try:
         grabber  = dxfgrabber.readfile(f, { "resolve_text_styles": False } )
      except Exception:
         print("[ERROR] Eccezione non gestita")

      n        = str(FloorInference.get_identifier(f, grabber)).lower()

      valid_filename_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
      directory = "assets/dxf/tutti_con_audit/"+''.join(c for c in n if c in valid_filename_chars)+"/"

      if( not os.path.exists(directory) ):
         os.makedirs(directory)

      shutil.copy(f, directory)
      sys.stdout.flush()
      sys.stderr.flush()
