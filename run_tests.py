
import unittest
import sys
from os import listdir
import re
from colour_runner.runner import ColourTextTestRunner
from utils.logger import Logger

from tasks.data_merger import DataMerger
DataMerger.skip_geocoding = True


Logger.verbosity = 0

if(len(sys.argv) == 1):
   files_list = listdir('test')
else:
   files_list = sys.argv[1:]
   sys.argv = sys.argv[0:1]

for filename in files_list:
   if re.match(".+test\.py" , filename):
      s = __import__("test."+filename.rsplit(".py")[0], globals(), locals(), ['*'], 0)
      potential_class_names = [local for local in dir(s) if re.match("[A-Z][^_]+", local) ]
      for classname in potential_class_names:
         setattr(sys.modules[__name__], classname, getattr(s, classname))


unittest.main(exit=False, verbosity = 2, testRunner=ColourTextTestRunner)
