from .odm import ODMModel, around_callbacks
import re

class AvailableService(ODMModel):
   def __init__(self, new_attrs = None):
      super().__init__(new_attrs)
      self.key    = new_attrs['key']
      self.langs  = {l for l in new_attrs if l!='key'}
