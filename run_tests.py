
import unittest
import sys
from os import listdir
import re

for filename in listdir('test'):
   if re.match(".+test\.py" , filename):
      s = __import__("test."+filename.rsplit(".py")[0], globals(), locals(), ['*'], 0)
      potential_class_names = [local for local in dir(s) if re.match("[A-Z][^_]+", local) ]
      for classname in potential_class_names:
         setattr(sys.modules[__name__], classname, getattr(s, classname))

unittest.main(exit=False, verbosity = 2)
