from itertools    import chain
from model        import Building, RoomCategory
from utils.logger import Logger
from datetime     import datetime

class DXFDataUpdater:

   @staticmethod
   def resolve_room_categories(building, floor_dict = None):
      """
      Given a building, perform the mapping between it's dxf rooms and their
      relative categories.

      It does not save the building, which is responsibility of the caller.

      Arguments:
      - building: a Building object whose dxf rooms we want to process.
      - floor_dict: an (optional) dxf floor to limit the rooms to process. If
      None, all the current building floors will be used instead.

      Returns None, updates are performed directly on the dxf rooms.
      """
      target_floors = (
                  floor_dict and [floor_dict] or
                  building.attr("dxf") and building.attr("dxf")["floors"] or
                  []
               )

      cats = { cat.attr("_id"): cat.attr("cat_name") for cat in RoomCategory.where({}) }
      for floor_dict in target_floors:

         all_rooms = chain(
                           floor_dict["unidentified_rooms"],
                           floor_dict["rooms"].values()
                           )
         for target_room in all_rooms:
            if "cat_name" in target_room:
               continue

            for target_text in target_room["texts"]:
               if target_text["text"].upper() in cats:
                  target_room["cat_name"] = cats[target_text["text"].upper()]


   @staticmethod
   def resolve_rooms_id(building, floor_dict = None, source_name = None):
      """
      Associates r_id to rooms obtained by dxf file processing, by comparing
      texts with r_id information retrieved from easyroom or edilizia.

      Arguments:
      - target_building: a Building object whose dxf rooms we want to associate
      (i.e find their respective r_id).
      - floor_dict: the floor to process, as a list of dictionaries,
      each one representing a room. It may be None, in which case all
      target_building dxf floors will be processed.
      - source_name: a string indicating what namespace to use when looking
      for room identifiers. Must be either "edilizia" or "easyroom". If it is
      none, both will be used for searching the room id.

      Return value:
      - None, associations are made directly on the floor_dict dictionary items.

      """
      target_floors = (
                  floor_dict and [floor_dict] or
                  building.attr("dxf") and building.attr("dxf")["floors"] or
                  []
               )

      source_floors = DXFDataUpdater._get_source_floors(building, source_name)

      for floor_dict in target_floors:
         # Ordino i piani per priorita'. E' piu probabile trovare le informazioni
         # per una stanza che e' nel piano 0 su un piano 0 o 0.5 che sul piano 3
         def sortfunc(f):
            return abs( float(floor_dict["f_id"]) - float(f["f_id"]) )
         source_floors = sorted(source_floors, key=sortfunc)

         for i, target_room in enumerate(floor_dict["unidentified_rooms"]):

            possible_ids = [ r["text"].strip().lower() for r in target_room["texts"] ]
            r_id = DXFDataUpdater._find_r_id_on_source(source_floors, possible_ids)

            # Se la ricerca mi ha restituito un r_id, lo salvo nel dizionario
            # rooms con r_id come chiave e rimuovo la stanza da
            # unidentified_rooms
            if r_id:
               Logger.info("Found room: ", r_id)
               floor_dict["rooms"][r_id] = target_room
               # Marchiamo l'elemento corrente come "rimosso". Non lo
               # rimuoviamo subito perché andremo ad alterare la lista su
               # cui stiamo iterando.
               floor_dict["unidentified_rooms"][i] = None

         # "Sweep" delle stanze marcate come cancellate
         floor_dict["unidentified_rooms"] = [
                  r for r in floor_dict["unidentified_rooms"] if r is not None
               ]

   @staticmethod
   def _find_r_id_on_source(source_floors, possible_ids):
      for source_floor in source_floors:
         for r_id in source_floor["rooms"]:
            if r_id.lower() in possible_ids:
               return r_id

      return None

   @staticmethod
   def _get_source_floors(building, source_name):
      sources = (
               source_name and [source_name] or
               ["easyroom", "edilizia"]
               )

      def extract_floors_from_source(source):
            floors = building.attr(source) or []
            if floors:
               return floors.get("floors", [])
            return []

      # mettiamo tutti i piani in una sola lista sequenziale
      source_floors = [ extract_floors_from_source(s) for s in sources ]
      source_floors = list( chain(*source_floors) )

      return source_floors

   def find_building_to_update(self, building_dict):
      """
      Finds on database or create a Buiding object to be updated with information
      contained by building_dict

      Arguments:
      - building_dict: a dictionary containing the new values to be inserted
      on the building.

      Returns a Building object.

      Finds a building on database using b_id as identifier, otherwise looks for a
      building using l_b_id. If none of the above succeeds, creates a new building
      object to be inserted on database.
      """
      b_id = building_dict.get("b_id", "")

      return (
               Building.find(b_id) or
               Building.find_by_field("merged.l_b_id", b_id) or
               Building( {"_id": b_id} )
               )

   def save_floor(self, building, floor):
      """
      Implements the DXF Data Update functionality, saving a floor information to
      an existing building document.

      Arguments:
      - building: a Building object representing the database object to be
      updated with the new floor information.
      - floor: a Floor object representing the data to be updated / inserted into
      database.

      Returns: None

      If a floor with the same f_id already exists on the current building, it
      is replaced by the new one. The floor ordering is ensured by the Building
      model itself.
      """


      new_floor = floor.to_serializable()
      # Inseriamo le stanze non ancora identificate in unidentified_rooms
      # la chiave rooms conterrà un dizionario di stanze identificate
      new_floor["unidentified_rooms"]  = new_floor["rooms"]
      new_floor["rooms"]               = {}
      new_floor["updated_at"]          = datetime.now()
      del new_floor["b_id"]

      # Non vogliamo cancellare quanto c'è nel database, soltanto lo stesso floor
      dxf         = building.get("dxf", {})
      floors      = dxf.get("floors", [])

      # Se il floor corrente esiste gia' nel database, vogliamo sostituirlo
      for k, f in enumerate(floors):
         if f["f_id"] == floor.f_id:
            del floors[k]

      floors.append(new_floor)

      dxf["floors"]           = floors
      building["dxf"]         = dxf
      building["updated_at"]  = new_floor["updated_at"]

      callback = lambda b: DXFDataUpdater.resolve_rooms_id(b, new_floor, source_name = None)
      building.listen_once("before_save", callback)

      callback = lambda b: DXFDataUpdater.resolve_room_categories(b, new_floor)
      building.listen_once("before_save", callback)

      building.save()
