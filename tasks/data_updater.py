from model              import Building
from utils.logger       import Logger
from tasks.data_merger  import DataMerger
from tasks.dxf_data_updater              import DXFDataUpdater
import itertools

class DataUpdater():
   """
   The DataUpdater class implements the behavior of updating and inserting
   building and rooms information on the Database. It has no direct reference
   to PersistenceManager, interacting with the Database only indirectly, through
   the usage of the appropriate models.

   The main entry points are the methods update_buildings and update_rooms, both
   called by the appropriate Task Handler (mainly CSVTask).
   """

   def update_buildings(self, buildings):
      """
      Perform an update of building data on Database.

      Arguments:
      - buildings: a list of dictionaries, where each dictionary represents
      a building.

      Does not return (None).

      Example of a building retrived from an Edilizia csv file:
      {
         'b_id'      : '11030',
         'address'   : 'Milano - Via Francesco Sforza 44',
         'lon'       : '9.193670',
         'lat'       : '45.458065',
         'l_b_id'    : '5471'
      }

      If a building with the same b_id exists on the database, hence it will
      be updated, otherwise it will be replaced.
      """
      namespace = self.get_namespace()

      for b in buildings:
         b_id = b.get("b_id", "")

         if not self._is_valid_b_id(b_id):
            Logger.warning("Invalid building ID: \"{}\"".format(b_id))
            continue

         building = self.find_building_to_update(b)
         namespaced_attr = building.attr(namespace) or {}
         namespaced_attr.update(b)
         building.attr(namespace, namespaced_attr )

         edilizia = building.attr('edilizia')
         easyroom = building.attr('easyroom')

         building.attr('merged', DataMerger.merge_building(edilizia, easyroom))
         building.save()

   def update_rooms(self,rooms):
      """
      Perform an update of room data on Database.

      Arguments:
      - rooms: a list of dictionaries representing a room data.

      Does not return (None).

      Example of a room retrieved from an Edilizia csv file:
      {
         'room_name' : 'Aula Seminari',
         'type_name' : 'Aula',
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
      namespace = self.get_namespace() # che sorgente dati stiamo aggiornando?
      floor_key = self.get_floor_key() #

      # ordiniamo le stanze per edificio e per piano in modo da velocizzare l'algoritmo
      keyfunc           = lambda s: (s["b_id"], s[floor_key])
      rooms.sort(key=keyfunc)

      # raggruppiamo le stanze per building_id e floor_id
      rooms             = itertools.groupby(rooms, key=keyfunc)

      # inizialmente non abbiamo un building su cui stiamo lavorando
      building          = None

      for ((b_id, f_id), floor_rooms) in rooms:

         # Controlliamo di avere almeno un floor id valido
         if not(f_id and f_id.strip()):
            Logger.warning("Empty floor id in building: \"{}\". \"{}\" rooms discarded".format(b_id, len(list(floor_rooms))))
            continue

         # remove the attribute b_id from the rooms
         floor_rooms = map(self.sanitize_room, floor_rooms)

         if not self._is_valid_b_id(b_id):
            Logger.warning("Invalid building ID: \"{}\"".format(b_id))
            continue

         # Se b_id non si riferisce più allo stesso building ...
         if not building or building.attr("b_id") != b_id:
            # Salviamo l'ultimo building contemplato, ormai avrà le info
            # aggiornate su tutte le sue stanze

            # Aggiungiamo prima il callback per l'associazione dei room_id
            # dei file dxf
            if building:
               callback = lambda b: DXFDataUpdater.resolve_rooms_id(b, None, namespace)
               building.listen_once("before_save", callback)
               building.save()

            building = Building.find_or_create_by_id(b_id)

            # Namespaced_attr si riferisce a una sottoparte del dizionario
            # che costituisce il documento del building: quella relativa
            # alla sorgente che aggiorniamo in questo momento.
            namespaced_attr = building.attr(namespace) or {}
            namespaced_attr["floors"] = []
            building.attr(namespace, namespaced_attr)

         namespaced_attr["floors"].append( {
               "f_id"   : self.sanitize_floor_id(f_id),
               "rooms"  : list(floor_rooms)
            } )

      building and building.save()


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


   def sanitize_floor_id(self, floor_id):
      """
      Intended to clean up floor_ids before insertion on database.

      Arguments:
      - floor_id: the original floor_id string to be sanitized.

      Returns a string representing the sanitized version of the floor_id.

      It is a good practice for subclasses to call this parent superclass.
      """
      return floor_id


   def find_building_to_update(self, building_dict):
      """
      Finds on database or create a Buiding object to be updated with information
      contained by building_dict

      Arguments:
      - building_dict: a dictionary containing the new values to be inserted
      on the building.

      Returns a Building object.

      The default implementation finds the building by its b_id or creates a new
      one if none exists. Subclasses may override this behavior.
      """
      b_id = building_dict.get("b_id", "")

      return Building.find_or_create_by_id(b_id)
