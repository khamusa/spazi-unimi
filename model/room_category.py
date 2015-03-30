import re, json

class RoomCategory():

   cat_dict = None
   @classmethod
   def get_cat_dict(klass):
      """
      Get room categories from a JSON and converst them into a dictionary
      where keys are category ids and values are group names, descritions and
      scopes.
      """
      if not klass.cat_dict:
         cat_file = "config/room_categories.json"

         with open(cat_file) as cat_json:
            klass.cat_dict = json.load(cat_json)

      return klass.cat_dict

   @classmethod
   def get_cat_id_by_name(klass, name):
      if not name:
         return ""

      cat_dict   = klass.get_cat_dict()
      desc_to_id = {
         v["description"].upper().strip() : k
         for k, v in klass.get_cat_dict().items()
      }

      name = name.upper().strip()
      return desc_to_id.get(name, "")
