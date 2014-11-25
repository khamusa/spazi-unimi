import sys, os

class Logger():
   INFO    = '\033[94m' # blue
   OK      = '\033[92m' # green
   WARN    = '\033[93m' # yellow
   ERR     = '\033[91m' # red
   ENDC    = '\033[0m'  # reset color

   def success(*texts):
      print(Logger._prefix("OK!", Logger.OK), *texts, file=sys.stderr)

   def warning(*texts):
      print(Logger._prefix("WARN", Logger.WARN), *texts, file=sys.stderr)

   def error(*texts):
      print(Logger._prefix("ERR", Logger.ERR), *texts, file=sys.stderr)

   def info(*texts):
      print(Logger._prefix("INFO", Logger.INFO), *texts)

   def _prefix(key, color):
      if (os.fstat(0) == os.fstat(1)):
         return "["+color+key+Logger.ENDC+"] :"
      else:
         return "["+key+"] :"
