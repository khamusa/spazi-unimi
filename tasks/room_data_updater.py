from model                          import Building
from utils.logger                   import Logger
from tasks.data_merger              import DataMerger
from tasks.dxf_room_ids_resolver    import DXFRoomIdsResolver
from datetime                       import datetime
from itertools                      import groupby

class RoomDataUpdater():
   """
   The RoomDataUpdater class implements the behavior of updating and inserting
   rooms information on the Database. It has no direct reference to
   PersistenceManager, interacting with the Database only indirectly, through
   the usage of the appropriate models.

   The main entry point is the method update_rooms, called by the appropriate
   Task Handler (mainly CSVTask).
   """

   def update_rooms(self,rooms):
      """
      Perform an update of room data on Database.

      Arguments:
      - rooms: a list of dictionaries representing a room data.

      Does not return (None).

      Example of a room retrieved from an Edilizia csv file:
      {
         'room_name' : 'Aula Seminari',
         'cat_name' : 'Aula',
         'r_id'      : 'T065',
         'b_id'      : '11010',
         'capacity'  : '52',
         'l_floor'   : 'T'
      }

      The b_id field will be used to locate the associated building on the
      database. If it is found, it will be updated with the information,
      otherwise a new building will be created.

      Note that for each building that gets updated, it's floors will be emptied
      before adding the rooms information. Hence no partial updates are possible:
      everytime this method is called, it must receive the final list of rooms
      for each updated floor.
      """
      # salviamo una data di aggiornamento comune a tutti i palazzi
      self.batch_date = datetime.now()

      # ordiniamo le stanze per edificio e per piano in modo da velocizzare l'algoritmo
      rooms.sort(key = lambda s: (s["b_id"], s["l_floor"]))

      # raggruppiamo le stanze per building_id
      rooms = groupby(rooms, key = lambda s: s["b_id"])

      # Analizziamo un building alla volta
      for (b_id, rooms) in rooms:

         # Non procedo se il b_id non è valido
         if not Building.is_valid_bid(b_id):
            Logger.error(
               "Invalid building id: \"{}\".".format(b_id),
               "Rooms discarded:",
               ", ".join(r["r_id"] for r in rooms)
            )
            continue

         building = Building.find_or_create_by_id(b_id)

         # Lavoro principale di aggiornamento
         self.replace_building_rooms(building, rooms)

         # Non sarebbe questa gia' una politica di merge? Si tratta di usare
         # info di piu' sorgenti per risolvere qualcosa di DXF, ma usiamo più
         # sorgenti! È un tipo di merge, non un DXFDataUpdater. Mi sembra nel
         # posto sbagliato questo metodo. Mi sembra che le funzionalità di
         # merge sono compito del building model.
         DXFRoomIdsResolver.resolve_rooms_id(building, None, self.get_namespace())

         # Ensure floor merging is performed AFTER DXF Room_id resolution
         merged            = building.attributes_for_source("merged")
         merged["floors"]  = DataMerger.merge_floors(
            building.get("edilizia"),
            building.get("easyroom"),
            building.get("dxf")
         )

         building.save()

   def replace_building_rooms(self, building, rooms):
      """
      Replace the current building floors/rooms with those rooms (and
      consequently floors) contained in rooms.

      Arguments
      - building: a Building object to be updated
      - rooms : a list of dictionaries, each one representing a room. The format
      is the same of the rooms supplied to RoomDataUpdater.update_rooms.

      Return Value
      - None, changes are performed directly on the building object.
      """

      with Logger.info("Processing", str(building)):

         namespaced_attr = building.attributes_for_source(self.get_namespace())
         namespaced_attr["floors"] = []

         # salviamo le date di aggiornamento
         building["updated_at"]        = self.batch_date
         namespaced_attr["updated_at"] = self.batch_date

         # cicliamo su un floor alla volta
         for (f_id, floor_rooms) in groupby(rooms, key = lambda s:s["l_floor"]):

            # Controlliamo di avere almeno un floor id valido
            f_id = self.sanitize_and_validate_floor(f_id, floor_rooms)
            if not f_id:
               continue

            # possiamo fare a meno di questo error_context, facendo si che
            # la prepare_rooms, in seguito a un errore, stampi anche
            # il floor id?
            with Logger.error_context("Processing floor {}".format(f_id)):
               namespaced_attr["floors"].append( {
                     "f_id"   : f_id,
                     "rooms"  : self.prepare_rooms(f_id, floor_rooms)
               } )

   def prepare_rooms(self, floor_id, rooms):
      """
      Transform a list of rooms in a dictionary indexed by room id.
      Arguments:
      - floor_id: a string representing the floor identifier,
      - rooms: a list of rooms.
      Returns: a dictionary of rooms.
      Validate the r_id using Building.is_valid_rid function and discard rooms
      with invalid id. Create and return a dictionary of validated rooms.
      """
      result = {}
      discarded_rooms = set()

      for r in map(self.sanitize_room, rooms):
         if not Building.is_valid_rid(r["r_id"]):
            discarded_rooms.add(r["r_id"])
            continue

         r_id = r["r_id"]
         del r["r_id"]
         result[r_id] = r

      if discarded_rooms:
         Logger.warning(
            "Rooms discarded from floor", floor_id,
            "for having an invalid room id:",
            ", ".join(discarded_rooms)
            )
      return result

   def sanitize_room(self, room):
      """
      Sanitizes each room before saving it to database

      Arguments:
      room - a dictionary containing the information of the room to be persisted
      to database (may represent an insertion or update)

      Returns a reference to the updated dictionary.

      The default implementation removes the key b_id, since it is present as the
      main document _id. Subclasses MUST either ensure b_id is removed or call
      this superclass implementation.
      """

      # remove the attribute b_id from the room
      del room["b_id"]
      return room

   def sanitize_and_validate_floor(self, floor_id, floor_rooms):
      """
      Intended to clean up and validating floor_ids before insertion on database.
      It must also Log in case the floor is invalid.

      Arguments:
      - floor_id: the original floor_id string to be sanitized.
      - floor_rooms: a list of dictionaries representing the floor rooms.

      Returns a string representing the sanitized version of the floor_id.

      It is a good practice for subclasses to call this parent superclass.
      """
      valid = Building.is_valid_fid(floor_id)

      if not valid:
         rooms = [ r["r_id"] for r in floor_rooms ]
         Logger.warning(
            "Empty floor id in building.",
            len(rooms), "rooms discarded:",
            ", ".join(rooms)
            )

      return valid
