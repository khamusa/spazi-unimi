from utils                 import ConfigManager
from persistence           import MongoDBPersistenceManager
from model                 import RoomCategory,Building,BuildingView,AvailableService
from tasks                 import LookupTableTask
from model.odm             import ODMModel
from bson.json_util        import dumps
from flask                 import Flask, jsonify,abort,request,send_from_directory,render_template,Markup
from datetime              import datetime
from api.model             import RoomTimeTable


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
app.lookup_table_folder = 'static-table'

###########
# HELPERS #
###########

def url_for_endpoint(url_endpoint):
   return '/'.join( [app.api_namespace,app.api_version,url_endpoint] )+'/'

def filter_buildings_by_service(buildings,service,remove_floor_details=False):
  return [ b for b in buildings if len([ f for f in b['floors'] if service in f['available_services'] ])>0  ]


def maps_url(b_id,f_id):
   return '{0}://{1}/{2}/{3}/{3}_{4}.svg'.format(app.protocol,app.domain,app.maps_folder,b_id,f_id)

def lookup_table_url(db_name):
   return '{0}://{1}/{2}/{3}'.format(app.protocol, app.domain, app.lookup_table_folder, db_name)

def prepare_floor_for_api(floor):
   rooms = []
   for r_id in floor['rooms']:
      room           = floor['rooms'][r_id]
      room['r_id']   = r_id
      rooms.append(room)
   floor['rooms'] = rooms;
   return floor

def prepare_building_for_api(building):
   building['b_id'] = building['_id']
   del building['_id']

   # remove unnecessary nested object used in GeoJson coordinates structure
   building['coordinates'] = building['coordinates']['coordinates']

   #normalize floors
   building['floors'] = [ prepare_floor_for_api(f) for f in building['floors'] ]

   return building

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
      <p><em>show_floors[boolean] default false</em>: show every building with its floors detailed or return for every building its details and a collapsed list of available services</p>

   """
   buildings = list(app.buildings.find({'building_name':{'$exists':True}}))

   show_floors = request.args.get('show_floors') or False

   for b in buildings:
      b = prepare_building_for_api(b)

      # collapse available services
      if not show_floors:
         services = set()
         for f in b['floors']:
            del f['rooms']
            for s in f['available_services']:
               services.add(s)

         b['available_services'] = list(services)

   # filter by available service
   service = request.args.get('service') or None
   if service:
      buildings = filter_buildings_by_service(buildings,service)

   if not show_floors:
      for b in buildings:
         del b['floors']

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

   for i in range(0,len(building['floors'])):
      building['floors'][i]['map'] = maps_url( b_id,building['floors'][i]['f_id'] )

   building = prepare_building_for_api(building)

   return jsonify(building)

@app.route( url_for_endpoint('buildings/near/<float:lat>/<float:lng>'),methods=['GET'])
def api_get_buildings_near_position(lat,lng):
   """
      <h3>/buildings/near/<em>lat</em>/<em>lng</em><em>?radius=X</em></h3>
      <p>Returns a list of the all available buildings near the coordinate with latitude and longitude passed by params</p>
      <h5>Parameters</h6>
      <p><em>lat[float]</em> : latitude</p>
      <p><em>lng[float]</em> : longitude</p>
      <p><em>radius[float]</em> : radius in meters, default 2000m</p>
      <p><em>service[string]</em> : one of the valid available-services</p>

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

   buildings = [ prepare_building_for_api(b) for b in buildings ]
   return jsonify({ 'buildings': buildings })

# Categories
@app.route( url_for_endpoint('categories'),methods=['GET'])
def get_categories():
   return 0


# Rooms lookup table
@app.route( url_for_endpoint('client-lookup-table'),methods=['GET'] )
def api_get_lookup_table():
   """
      <h3>/client-lookup-table/?local_update=date</h3>
      <p>Rooms lookup table</p>
      <p><em>date[string]</em> : a date with format yyy/mm/dd</p>
      <p>Return an object with a boolean <em>update</em> attribute and the URL of the sqlite database.</p>
      <p>If the <em>update</em> attribute is true, the client should update its local db.</p>
   """
   date = request.args.get('local_update') or ""
   print(date)

   try:
      date_obj = datetime.strptime(date,"%Y/%m/%d")
   except ValueError:
      abort(400)

   task              = LookupTableTask()
   to_update         = task.client_should_update_db(date_obj.timestamp())

   return jsonify({ 'update': to_update , 'url':lookup_table_url(task.db_name()) })

@app.route( url_for_endpoint('rooms/<b_id>'),methods=['GET'] )
def api_get_rooms_in_building(b_id):
   """
      <h3>/rooms/<em>b_id</em></h3>
      <p>Returns all the rooms within the bulding with b_id grouped by floor.</p>
      <h5>Parameters</h6>
      <p><em>b_id[string]</em> : a valid b_id</p>

   """

   building = app.buildings.find_one({'_id':b_id})
   if not building:
      abort(404)

   return jsonify({'floors':building['floors']})

@app.route( url_for_endpoint('rooms/<b_id>/<r_id>'),methods=['GET'] )
def api_get_room_by_id(b_id,r_id):
   """
      <h3>/rooms/<em>b_id</em>/<em>r_id</em></h3>
      <p>Returns the room with r_id within the bulding with b_id .</p>
      <h5>Parameters</h6>
      <p><em>b_id[string]</em> : a valid b_id</p>
      <p><em>r_id[string]</em> : a valid r_id</p>

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
         room['building_coordinates']  = [coordinates[0],coordinates[1]]
         room['f_id']                  = floor['f_id']
         room['floor']                 = floor['floor_name']
         room['map']                   = maps_url(b_id,floor['f_id'])
         room['r_id']                  = r_id
         return jsonify(room)

   abort(404)

@app.route( url_for_endpoint('rooms/timetable/<b_id>/<r_id>'),methods=['GET'] )
def api_get_room_timetable(b_id,r_id):
   """
      <h3>/rooms/timetable/<em>b_id</em>/<em>r_id</em></h3>
      <p>if exists returns the weekly timetable for room with r_id within the bulding with b_id .</p>
      <h5>Parameters</h6>
      <p><em>b_id[string]</em> : a valid b_id</p>
      <p><em>r_id[string]</em> : a valid r_id</p>

   """
   timetable = RoomTimeTable(b_id,r_id)

   if not timetable:
      abort(404)

   return jsonify({"events":timetable.events})


@app.route( url_for_endpoint('room-viewer/<b_id>/<r_id>'),methods=['GET'] )
def api_show_room_by_id(b_id,r_id):
   """
      <h3>/rooms/<em>b_id</em>/<em>r_id</em></h3>
      <p>Show the room with r_id within the bulding with b_id</p>
      <h5>Parameters</h6>
      <p><em>b_id[string]</em> : a valid b_id</p>
      <p><em>r_id[string]</em> : a valid r_id</p>

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
         room['building_coordinates']  = [coordinates[0],coordinates[1]]
         room['f_id']                  = floor['f_id']
         room['floor']                 = floor['floor_name']
         room['map']                   = maps_url(b_id,floor['f_id'])

         building_name        = building['building_name']
         building_address     = room['building_address']
         building_coordinates = [coordinates[0],coordinates[1]]
         floor_name           = floor['floor_name']
         map_url              = maps_url(b_id,floor['f_id'])
         room_name            = room['room_name']
         room_id              = r_id

         return render_template('map_show.html',**locals())

   abort(404)

@app.route( url_for_endpoint('available-services/<lang>'),methods=['GET'] )
def api_get_available_services(lang):
   """
      <h3>/available-services/</h3>
      <p>Returns the complete list of the all available services</p>
      <h5>Parameters</h6>
      <p><em>lang[string]</em> : language</p>
   """
   services = AvailableService.services()

   if lang not in services[0].langs:
      abort(404)
   return jsonify({'services':[ {'key':s.key,'label':s[lang]} for s in services ]})



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







