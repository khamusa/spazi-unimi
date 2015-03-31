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
      for floor_dict in target_floors:
         categorized_rooms += klass._resolve_room_categories_for_floor(
            floor_dict,
            cats
         )

      if categorized_rooms:
         Logger.info(categorized_rooms, "rooms were categorized")

      return categorized_rooms

   @classmethod
   def _resolve_room_categories_for_floor(klass, floor_dict, cats):
      """
      Analyzes all rooms on floor_dict tries associating each one with a room
      category.

      Arguments:
      - floor_dict: a dictionary representing a floor
      - cats: a dictionary indexed by category ID. Values represents the
      category human name.
      Example: { "AUL01" : "Aula" }


      Return value: an integer representing the amount of rooms that matched
      a category.
      """
      all_rooms = chain(
         floor_dict["unidentified_rooms"],
         floor_dict["rooms"].values()
      )

      return klass._resolve_categories_for_rooms(
         all_rooms,
         cats
      )

   @classmethod
   def _resolve_categories_for_rooms(klass, all_rooms, cats):
      """
      Find texts that represent a category identifier and assigns the category
      name to rooms. If no category ID is found, the algorithm tries categories
      by their human names.

      Arguments:
      - all_rooms: list of rooms to search for categories
      - cats: a dictionary indexed by category ID. Values represents the
      category human name.


      Return value: an integer representing the amount of rooms that matched
      a category.
      """

      categorized_rooms = 0

      for a_room in all_rooms:
         categorized_rooms += klass._resolve_category_for_room(
            a_room,
            cats
         )

      return categorized_rooms

   @classmethod
   def _resolve_category_for_room(klass, a_room, cats):
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

      Return value: True if a match is found, False otherwise.
      """
      all_texts = [ t["text"].strip().upper() for t in a_room["texts"] ]

      # 1 - Look for exact category ids
      match_id  = next((t for t in all_texts if t in cats), None)
      if match_id:
         a_room["cat_id"] = match_id
         return True

      # 2 - look for category name match
      match_name  = next((t for t in all_texts if RoomCategory.get_cat_id_by_name(t)), None)
      if match_name:
         a_room["cat_id"] = RoomCategory.get_cat_id_by_name(match_name)
         return True

      return False

   @classmethod
   def get_room_categories_dict(klass):
      """
      Get room categories and converst them into a dictionary where keys are
      category ids and values are category names
      """

      return  {
         k: v["description"]
         for k, v in RoomCategory.get_cat_dict().items()
         if k != "VNS02"
      }
