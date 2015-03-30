import re, json

class RoomCategory():

   @classmethod
   def get_cat_dict(klass):
      """
      Get room categories from a JSON and converst them into a dictionary
      where keys are category ids and values are group names, descritions and
      scopes.
      """
      cat_file = "config/room_categories.json"

      with open(cat_file) as cat_json:
         cat_dict = json.load(cat_json)

      return cat_dict

   @classmethod
   def get_room_categories_names_dict(klass, cats):
      """
      Given a dictionary of room categories obtained by a call to
      get_room_categories_dict, returns a new dictionary in which keys
      are an uppercase version of the human name of the categories, and values
      are the original values.
      """
      return { v.upper().strip() : v for _, v in cats.items() }


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
