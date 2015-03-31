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

      name   = name.upper().strip()
      cat_id = desc_to_id.get(name, "")
      if cat_id:
         return cat_id

      synonyms = {
         cat["synonym"].upper() : k for k, cat in cat_dict.items()
         if "synonym" in cat
      }

      return synonyms.get(name, "")

   @classmethod
   def get_cat_by_id(klass, cat_id):
      return klass.get_cat_dict().get(cat_id, {})

   @classmethod
   def get_scope_by_id(klass, cat_id):
      return klass.get_cat_dict().get(cat_id, {}).get("scope", "")

   @classmethod
   def get_group_name_by_id(klass, cat_id):
      cat_info   = klass.get_cat_dict().get(cat_id, {})
      group_name = cat_info.get("group_name", None)
      return group_name or cat_info.get("description", "Sconosciuto")
