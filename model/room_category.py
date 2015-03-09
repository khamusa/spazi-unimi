from . import ORMModel
import re

class RoomCategory(ORMModel):

   def __init__(self, new_attrs = None):
      new_attrs["cat_name"] = re.sub("\s*\([^\)]*\)\s*", "", new_attrs["cat_name"])
      super().__init__(new_attrs, external_id = "cat_id")


