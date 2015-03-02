import sys, os, io, re

class BaseLoggingContext():
   """Base Logging Context is the class responsible for actually writing messages
   to standard output. Other contexts should delegate to it's write method."""

   def __init__(self):
      self.indent_lvl     = 0

   def write(self, req_verbosity, *texts):
      """This is the method that actually writes to stdout"""
      if(Logger.verbosity >= req_verbosity):
         my_str = " ".join(str(t) for t in texts)
         my_str = self.filter_colors(my_str, sys.stdout)
         print(my_str, end="")
         return True
      return False

   def filter_colors(self, text, target_out):
      """If colors are not to be printed (output to file, for example), filter
      all ANSI color codes from text and return it"""
      if not os.isatty(target_out.fileno()):
         ansi_escape = re.compile(r'\x1b[^m]*m')
         return ansi_escape.sub('', text)
      return text


class LoggingContext(BaseLoggingContext):
   """Each Logging Context encapsulates an indentation level and handles a
   verbosity bubble effect: when "child" prints have higher verbosity, it must
   be propagated to the parent prints, so they're also displayed"""

   def __init__(self, indent_lvl, verbosity, buffer_init = ""):
      self.indent_lvl     = indent_lvl
      self.buffer         = io.StringIO()
      self.buffer.write(buffer_init)
      self.verbosity      = verbosity

   def __enter__(self):
      self._lastcontext = Logger.context
      Logger.context    = self
      return Logger

   def __exit__(self, type, value, traceback):
      Logger.context = self._lastcontext
      self._lastcontext.write(self.verbosity, self.buffer.getvalue())
      return False

   def write(self, req_verbosity, *texts):
      if(Logger.verbosity >= req_verbosity):
         self.verbosity = min(req_verbosity, self.verbosity)
         self.buffer.write("".join(str(t) for t in texts))
         return True
      return False


class LoggerMeta(type):
   def __getattr__(self, attrname):
      """Responsible for actually implementing the logging methods on the
      Logger class"""
      if attrname in Logger.print_methods:
         # Retrieve the method options
         opts = Logger.print_methods[attrname]

         def log_message(*texts):
            prefix = Logger._get_prefix(opts["default_prefix"], opts["color"])
            return prefix+" ".join(str(t) for t in texts)

         # Apply the decorator to the message function
         verbosity_wrap = Logger.contextualized_print(opts["verbosity"])
         final_function = verbosity_wrap(log_message)

         return final_function
      else:
         raise AttributeError(attrname+" not found in class Logger")



class Logger(metaclass = LoggerMeta):

   COLORS = {
      "BLUE"    : '\033[94m',
      "GREEN"   : '\033[92m',
      "YELLOW"  : '\033[93m',
      "RED"     : '\033[91m',
      "RESET"   : '\033[0m'
   }

   VERBOSITY_ALL        = 4
   VERBOSITY_INFO       = 3
   VERBOSITY_WARNING    = 2
   VERBOSITY_FATAL      = 1
   verbosity = VERBOSITY_ALL

   """Initial context, it's the one that actually writes to stdout"""
   context = BaseLoggingContext()

   """Print method definitions, actually implemented dynamically by the metaclass"""
   print_methods = {
      "success" : {
         "default_prefix" : "ok",
         "color" : COLORS["GREEN"],
         "verbosity" : VERBOSITY_INFO
      },
      "info" : {
         "default_prefix" : "info",
         "color" : COLORS["BLUE"],
         "verbosity" : VERBOSITY_INFO
      },
      "error_context" : {
         "default_prefix" : "info",
         "color" : COLORS["BLUE"],
         "verbosity" : 99
      },
      "warning" : {
         "default_prefix" : "warn",
         "color" : COLORS["YELLOW"],
         "verbosity" : VERBOSITY_WARNING
      },
      "error" : {
         "default_prefix" : "fail",
         "color" : COLORS["RED"],
         "verbosity" : VERBOSITY_FATAL
      }
   }

   def contextualized_print(method_vlevel):
      """Decorates the printing methods so that the print context is automatically
      defined and propagated to next calls"""
      def decorator(method):
         def print_wrapper(*args, **kargs):
            cur_cont = Logger.context

            my_str      = Logger._get_indent(cur_cont.indent_lvl)
            my_str      = my_str + method(*args, **kargs)+"\n"

            # Will return False if required level of verbosity is not satisfied
            if(Logger.context.write(method_vlevel, my_str)):
               my_str = ""

            return LoggingContext(cur_cont.indent_lvl + 1, method_vlevel, my_str)
         return print_wrapper
      return decorator

   def _get_prefix(prefix_str, color):
      """Given a prefix str and color, return a formatted string for the prefix,
      with the ANSI color code wrapping it"""
      if not prefix_str:
         return ""

      prefix_str = "{:^4}".format(prefix_str[:4])

      #if (os.fstat(0) == os.fstat(out.fileno())):
      prefix_str = color+prefix_str+Logger.COLORS["RESET"]

      return "["+prefix_str+"] "

   def _get_indent(indent_lvl):
      """Convert an identation amount into a string of spaces"""
      out = Logger.context
      return " "*indent_lvl*7
