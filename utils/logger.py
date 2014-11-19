import sys

class Logger():

   def warning(text):
         print("[WARN] : %s", text,file=sys.stderr)

   def error(text):
      print(" [ERR] : %s",text,file=sys.stderr)


   def info(text):
      print("[INFO] : %s",text)
