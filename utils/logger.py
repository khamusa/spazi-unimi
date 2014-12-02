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

   def success(*texts, indent=0, out=sys.stdout):
      if(Logger.verbosity >= Logger.VERBOSITY_INFO):
         print(" "*indent+Logger._prefix(" OK ", Logger.OK), *texts, file=out)

   def info(*texts, indent=0, out=sys.stdout):
      if(Logger.verbosity >= Logger.VERBOSITY_INFO):
         print(" "*indent+Logger._prefix("INFO", Logger.INFO), *texts, file=out)

   def warning(*texts, indent=0, out=sys.stdout):
      if(Logger.verbosity >= Logger.VERBOSITY_WARNINGS):
         print(" "*indent+Logger._prefix("WARN", Logger.WARN), *texts, file=out)

   def error(*texts, indent=0, out=sys.stderr):
      if(Logger.verbosity >= Logger.VERBOSITY_FATAL):
         print(" "*indent+Logger._prefix(" ERR", Logger.ERR), *texts, file=out)

   def _prefix(key, color):
      if (os.fstat(0) == os.fstat(1)):
         return "["+color+key+Logger.ENDC+"] :"
      else:
         return "["+key+"] :"
