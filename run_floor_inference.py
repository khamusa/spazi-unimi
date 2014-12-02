from tasks.dxf.floor_inference import FloorInference


if __name__ == "__main__":
   import sys, dxfgrabber, shutil, os
   files = sys.argv[1:]

   for i in range(files):
      f = files[i]

      print(i, " - Processing file", os.path.basename(f))
      grabber  = dxfgrabber.readfile(f, { "resolve_text_styles": False } )

      n        = str(FloorInference.get_identifier(f, grabber)).lower()

      valid_filename_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
      directory = "assets/dxf/tutti_con_audit/"+''.join(c for c in n if c in valid_filename_chars)+"/"

      if( not os.path.exists(directory) ):
         os.makedirs(directory)

      shutil.copy(f, directory)
      sys.stdout.flush()
      sys.stderr.flush()
