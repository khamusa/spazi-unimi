from model                    import Building
from utils.logger             import Logger
from itertools                import chain

class DXFRoomIdsResolver:

   @classmethod
   def resolve_rooms_id(klass, building, floor_dict = None, source_name = None):
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
      identified_rooms = set()
      target_floors = (
                  floor_dict and [floor_dict] or
                  building.attr("dxf") and building.attr("dxf")["floors"] or
                  []
               )

      source_floors = klass._get_source_floors(building, source_name)

      for floor_dict in target_floors:
         # Ordino i piani per priorita'. E' piu probabile trovare le informazioni
         # per una stanza che e' nel piano 0 su un piano 0 o 0.5 che sul piano 3
         def sortfunc(f):
            return abs( float(floor_dict["f_id"]) - float(f["f_id"]) )
         source_floors = sorted(source_floors, key=sortfunc)

         for i, target_room in enumerate(floor_dict["unidentified_rooms"]):

            possible_ids = [ r["text"].strip().lower() for r in target_room["texts"] ]
            r_id = klass._find_r_id_on_source(source_floors, possible_ids)

            # Se la ricerca mi ha restituito un r_id, lo salvo nel dizionario
            # rooms con r_id come chiave e rimuovo la stanza da
            # unidentified_rooms
            if r_id:
               identified_rooms.add(r_id)
               floor_dict["rooms"][r_id] = target_room
               # Marchiamo l'elemento corrente come "rimosso". Non lo
               # rimuoviamo subito perché andremo ad alterare la lista su
               # cui stiamo iterando.
               floor_dict["unidentified_rooms"][i] = None

         # "Sweep" delle stanze marcate come cancellate
         floor_dict["unidentified_rooms"] = [
                  r for r in floor_dict["unidentified_rooms"] if r is not None
               ]

      if identified_rooms:
         Logger.info(
            "The following rooms have been identified:",
            ", ".join(identified_rooms)
            )

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
