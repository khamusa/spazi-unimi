from utils                 import ConfigManager
from persistence           import MongoDBPersistenceManager
from model                 import RoomCategory,Building,BuildingView
from model.odm             import ODMModel
from bson.json_util        import dumps
from flask                 import Flask, jsonify,abort,request,send_from_directory



app                     = Flask(__name__,static_url_path='')
app.app_config          = ConfigManager('config/general.json')
app.persistence         = MongoDBPersistenceManager(app.app_config)
app.api_namespace       = '/api'
app.api_version         = 'v1.0'
ODMModel.set_pm( app.persistence )
BuildingView.setup_collection()
# radius used with GeoSpatial Query (meters)
app.radius              = 2000


###########
# HELPERS #
###########

def url_for_endpoint(url_endpoint):
   return '/'.join( [app.api_namespace,app.api_version,url_endpoint] )+'/'

def filter_buildings_by_service(buildings,service):
   return [ b for b in buildings if len([ f for f in b['floors'] if service in f['available_services'] ])>0  ]

@app.before_request
def prepare_buildings_collection():
   app.buildings     = BuildingView.get_collection()


##########
# ROUTES #
##########

# Buildings
@app.route( url_for_endpoint('buildings'),methods=['GET'] )
def get_buildings():
   buildings = list(app.buildings.find({'building_name':{'$exists':True}}))
   for b in buildings:
      for floor in b['floors']:
         del floor['rooms']

   service = request.args.get('service') or None
   if service:
      buildings = filter_buildings_by_service(buildings,service)

   return jsonify({ 'buildings': buildings })

@app.route( url_for_endpoint('buildings/<b_id>'),methods=['GET'] )
def get_building_by_id(b_id):

   if not Building.is_valid_bid(b_id):
      abort(400)

   building = app.buildings.find_one({'_id':b_id})
   if not building:
       building = []
   return jsonify({ 'buildings': building })

@app.route( url_for_endpoint('buildings/near/<float:lat>/<float:lng>'),methods=['GET'])
def get_buildings_near_position(lat,lng):
   r = request.args.get('radius') or app.radius
   if (not lat) or (not lng):
      abort(400)

   geo_json_point = {
      '$geometry' : {
         'type'         : 'Point',
         'coordinates'  : [ lng , lat ] },
         '$maxDistance' : int(r)
   }

   buildings   = list(app.buildings.find({ 'coordinates' : { '$near' : geo_json_point } }))

   service = request.args.get('service') or None
   if service:
      buildings = filter_buildings_by_service(buildings,service)

   return jsonify({ 'buildings': buildings })

# Categories
@app.route( url_for_endpoint('categories'),methods=['GET'])
def get_categories():
   return 0


# Rooms lookup table
@app.route( url_for_endpoint('rooms'),methods=['GET'] )
def get_rooms():
   buildings   = list(app.buildings.find({'building_name':{'$exists':True}}))
   rooms       = []

   for building in buildings:
      for floor in building['floors']:
         for room_id in floor['rooms']:
            data = {
               'b_id'            : building['_id'],
               'building_name'   : building['building_name'],
               'floor'           : floor['floor_name'],
               'r_id'            : room_id,
               'room_name'       : floor['rooms'][room_id]['room_name']
            }
            rooms.append(data)

   return jsonify({ 'rooms': rooms })

@app.route( url_for_endpoint('rooms/<b_id>/<r_id>'),methods=['GET'] )
def get_room_by_id(b_id,r_id):
   building = app.buildings.find_one({'_id':b_id})
   if not building:
      abort(404)

   for floor in building['floors']:
      room        = floor['rooms'].get(r_id,None)
      coordinates = building['coordinates']['coordinates']
      if room:
         room['b_id']                  = b_id
         room['building_name']         = building['building_name']
         room['building_address']      = building['address']
         room['building_coordinates']  = { 'lng' : coordinates[0], 'lat' : coordinates[1] }
         room['floor']                 = floor['floor_name']
         return jsonify({'room':room})

   abort(404)

@app.route( url_for_endpoint('available-services/'),methods=['GET'] )
def get_available_services():
   buildings   = list(app.buildings.find({'building_name':{'$exists':True}}))
   services    = set()

   for building in buildings:
      for floor in building['floors']:
         for s in floor['available_services']:
            services.add(s)

   services = { k:v for k,v in enumerate(services) }

   return jsonify({'services':services})





