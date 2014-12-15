from . import ORMModel

class RoomCategory(ORMModel):

   def __init__(self, new_attrs = None):
      super().__init__(new_attrs, external_id = "cat_id")


