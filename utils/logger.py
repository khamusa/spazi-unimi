import sys, os

class Logger():
   INFO    = '\033[94m' # blue
   OK      = '\033[92m' # green
   WARN    = '\033[93m' # yellow
   ERR     = '\033[91m' # red
   ENDC    = '\033[0m'  # reset color

   VERBOSITY_ALL        = 3
   VERBOSITY_INFO       = 3
   VERBOSITY_WARNINGS   = 2
   VERBOSITY_FATAL      = 1
   verbosity = VERBOSITY_ALL

   def success(*texts):
      if(Logger.verbosity >= Logger.VERBOSITY_INFO):
         print(Logger._prefix(" OK ", Logger.OK), *texts, file=sys.stderr)

   def info(*texts):
      if(Logger.verbosity >= Logger.VERBOSITY_INFO):
         print(Logger._prefix("INFO", Logger.INFO), *texts)

   def warning(*texts):
      if(Logger.verbosity >= Logger.VERBOSITY_WARNINGS):
         print(Logger._prefix("WARN", Logger.WARN), *texts, file=sys.stderr)

   def error(*texts):
      if(Logger.verbosity >= Logger.VERBOSITY_FATAL):
         print(Logger._prefix(" ERR", Logger.ERR), *texts, file=sys.stderr)

   def _prefix(key, color):
      if (os.fstat(0) == os.fstat(1)):
         return "["+color+key+Logger.ENDC+"] :"
      else:
         return "["+key+"] :"
