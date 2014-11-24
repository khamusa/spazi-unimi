import sys

class Logger():

   def warning(text):
         print("[WARN] :", text,file=sys.stderr)

   def error(text):
      print(" [ERR] :",text,file=sys.stderr)

   def info(text):
      print("[INFO] :",text)
