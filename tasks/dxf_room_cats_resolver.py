from itertools          import chain
from model              import RoomCategory
from utils.logger       import Logger

class DXFRoomCatsResolver:

   @classmethod
   def resolve_room_categories(klass, building, floor_dict = None):
      """
      Given a building, perform the mapping between it's dxf rooms and their
      relative categories.

      It does not save the building, which is responsibility of the caller.

      Arguments:
      - building: a Building object whose dxf rooms we want to process.
      - floor_dict: an (optional) dxf floor to limit the rooms to process. If
      None, all the current building floors will be used instead.

      Returns value: an integer representing the amount of rooms matched. The
      category name saved in place in each room dictionary, under the
      key "cat_name"
      """
      categorized_rooms = 0
      target_floors = (
                  floor_dict and [floor_dict] or
                  building.get("dxf") and building.get("dxf")["floors"] or
                  []
               )

      cats        = klass.get_room_categories_dict()
      cats_names  = klass.get_room_categories_names_dict(cats)
      for floor_dict in target_floors:
         categorized_rooms += klass._resolve_room_categories_for_floor(
            floor_dict,
            cats,
            cats_names
         )

      if categorized_rooms:
         Logger.info(categorized_rooms, "rooms were categorized")

      return categorized_rooms

   @classmethod
   def _resolve_room_categories_for_floor(klass, floor_dict, cats, cats_names):
      """
      Analyzes all rooms on floor_dict tries associating each one with a room
      category.

      Arguments:
      - floor_dict: a dictionary representing a floor
      - cats: a dictionary indexed by category ID. Values represents the
      category human name.
      Example: { "AUL01" : "Aula" }
      - cats_names: Another dictionary, in which keys are a uppercase version
      of category human names, and values is the normal version.
      Example: { "AULA INFORMATICA" : "Aula Informatica" }


      Return value: an integer representing the amount of rooms that matched
      a category.
      """
      all_rooms = chain(
         floor_dict["unidentified_rooms"],
         floor_dict["rooms"].values()
      )

      return klass._resolve_categories_for_rooms(
         all_rooms,
         cats,
         cats_names
      )

   @classmethod
   def _resolve_categories_for_rooms(klass, all_rooms, cats, cats_names):
      """
      Find texts that represent a category identifier and assigns the category
      name to rooms. If no category ID is found, the algorithm tries categories
      by their human names.

      Arguments:
      - all_rooms: list of rooms to search for categories
      - cats: a dictionary indexed by category ID. Values represents the
      category human name.
      - cats_names: Another dictionary, in which keys are a uppercase version
      of category human names, and values is the normal version.


      Return value: an integer representing the amount of rooms that matched
      a category.
      """

      categorized_rooms = 0

      for a_room in all_rooms:
         categorized_rooms += klass._resolve_category_for_room(
            a_room,
            cats,
            cats_names
         )

      return categorized_rooms

   @classmethod
   def _resolve_category_for_room(klass, a_room, cats, cats_names):
      """
      Looks for texts in a_room that looks like a category identifier and
      assigns the cat_name attribute to a_room. If no category ID is found,
      the algorithm tries categories by their human names.

      Arguments:
      - a_room: a room dictionary with a "texts" key containing the list of
      texts to be analyzed.
      - cats: a dictionary indexed by category ID. Values represents the
      category human name.
      Example: { "AUL01" : "Aula" }
      - cats_names: Another dictionary, in which keys are a uppercase version
      of category human names, and values is the normal version.
      Example: { "AULA INFORMATICA" : "Aula Informatica" }

      Return value: True if a match is found, False otherwise.
      """
      all_texts = [ t["text"].strip().upper() for t in a_room["texts"] ]

      # 1 - Look for exact category ids
      match_id  = next((t for t in all_texts if t in cats), None)
      if match_id:
         a_room["cat_name"] = cats[match_id]
         return True

      # 2 - look for category name match
      match_name  = next((t for t in all_texts if t in cats_names), None)
      if match_name:
         a_room["cat_name"] = cats_names[match_name]
         return True

      print("No cat match", "|".join(all_texts))

      return False

   @classmethod
   def get_room_categories_dict(klass):
      """
      Get room categories from database and converst them into a dictionary
      where keys are category ids and values are category names
      """

      return { cat["_id"]: cat["cat_name"] for cat in RoomCategory.where({}) }

   @classmethod
   def get_room_categories_names_dict(klass, cats):
      """
      Given a dictionary of room categories obtained by a call to
      get_room_categories_dict, returns a new dictionary in which keys
      are an uppercase version of the human name of the categories, and values
      are the original values.
      """
      return { v.upper().strip() : v for _, v in cats.items() }
