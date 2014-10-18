
from json import JSONEncoder

class JsonRoomEncoder(JSONEncoder):

   def default(self, obj):
      if(hasattr(obj, "to_serializable")):
         return obj.to_serializable()

      super(obj)
