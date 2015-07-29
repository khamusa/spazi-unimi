from utils                 import ConfigManager
from persistence           import MongoDBPersistenceManager
from model                 import RoomCategory,Building,BuildingView
from model.odm             import ODMModel
from bson.json_util        import dumps
from flask                 import Flask, jsonify,abort,request,send_from_directory,render_template,Markup



app                     = Flask(__name__,static_url_path='')
app.app_config          = ConfigManager('config/general.json')
app.persistence         = MongoDBPersistenceManager(app.app_config)
app.api_namespace       = '/api'
app.api_version         = 'v1.0'
ODMModel.set_pm( app.persistence )
BuildingView.setup_collection()
# radius used with GeoSpatial Query (meters)
app.radius              = 2000
app.maps_folder         = 'static-maps'

###########
# HELPERS #
###########

def url_for_endpoint(url_endpoint):
   return '/'.join( [app.api_namespace,app.api_version,url_endpoint] )+'/'

def filter_buildings_by_service(buildings,service):
   return [ b for b in buildings if len([ f for f in b['floors'] if service in f['available_services'] ])>0  ]

def maps_url(res):
   return '{0}://{1}/{2}/{3}'.format(app.protocol,app.domain,app.maps_folder,res)

@app.before_request
def prepare_buildings_collection():
   app.buildings     = BuildingView.get_collection()
   app.protocol      = 'http'
   app.domain        = request.headers['Host']


##########
# ROUTES #
##########

# Buildings
@app.route( url_for_endpoint('buildings'),methods=['GET'] )
def api_get_buildings():
   """
      <h3>/buildings/<em>?service=XXX</em></h3>
      <p>Returns a list of the all available buildings.</p>
      <h5>Parameters</h6>
      <p><em>service[string]</em> : could be one of the available services, if provided returns only those buildings with the specified service</p>

   """
   buildings = list(app.buildings.find({'building_name':{'$exists':True}}))
   for b in buildings:
      for floor in b['floors']:
         del floor['rooms']

   service = request.args.get('service') or None
   if service:
      buildings = filter_buildings_by_service(buildings,service)

   return jsonify({ 'buildings': buildings })

@app.route( url_for_endpoint('buildings/<b_id>'),methods=['GET'] )
def api_get_building_by_id(b_id):
   """
      <h3>/buildings/<em>b_id</em></h3>
      <p>Returns the building with the specified b_id .</p>
      <h5>Parameters</h6>
      <p><em>b_id[string]</em> : a valid b_id</p>

   """
   if not Building.is_valid_bid(b_id):
      abort(400)

   building = app.buildings.find_one({'_id':b_id})
   if not building:
       building = []

   maps = [ maps_url( '{0}/{0}_{1}.svg'.format(b_id,f['f_id']) ) for f in building['floors'] ]

   building['maps'] = maps
   return jsonify({ 'buildings': building })

@app.route( url_for_endpoint('buildings/near/<float:lat>/<float:lng>'),methods=['GET'])
def api_get_buildings_near_position(lat,lng):
   """
      <h3>/buildings/near/<em>lat</em>/<em>lng</em><em>?radius=X</em></h3>
      <p>Returns a list of the all available buildings near the coordinate with latitude and longitude passed by params</p>
      <h5>Parameters</h6>
      <p><em>lat[float]</em> : latitude</p>
      <p><em>lng[float]</em> : longitude</p>
      <p><em>radius[float]</em> : radius in meters, default 2000m</p>

   """

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
def api_get_rooms():
   """
      <h3>/rooms/</h3>
      <p>Rooms lookup table</p>
   """
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
def api_get_room_by_id(b_id,r_id):
   """
      <h3>/rooms/<em>b_id</em>/<em>r_id</em></h3>
      <p>Returns the room with r_id within the bulding with b_id .</p>
      <h5>Parameters</h6>
      <p><em>b_id[string]</em> : a valid b_id</p>
      <p><em>b_id[string]</em> : a valid r_id</p>

   """

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
def api_get_available_services():
   """
      <h3>/available-services/</h3>
      <p>Returns the complete list of the all available services</p>
   """
   buildings   = list(app.buildings.find({'building_name':{'$exists':True}}))
   services    = set()

   for building in buildings:
      for floor in building['floors']:
         for s in floor['available_services']:
            services.add(s)

   services = { k:v for k,v in enumerate(services) }

   return jsonify({'services':services})


@app.route( url_for_endpoint('docs/'),methods=['GET'] )
def get_docs():
   html = '<ul>'
   endpoints = [ val for name,val in globals().items() if name.count('api_')>0 ]

   for endpoint in endpoints:
      html += '<li>{}</li>'.format(endpoint.__doc__)

   html +='</ul>'
   return render_template('docs.html',content=Markup(html))


if __name__ == "__main__":
    app.run()







