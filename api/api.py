from utils                 import ConfigManager
from persistence           import MongoDBPersistenceManager
from model.building_view   import BuildingView
from model.room_category   import RoomCategory
from model.odm             import ODMModel
from bson.json_util        import dumps
from flask                 import Flask, jsonify,abort,request,send_from_directory



app                     = Flask(__name__,static_url_path='')
app.app_config          = ConfigManager('config/general.json')
app.persistence         = MongoDBPersistenceManager(app.app_config)
ODMModel.set_pm( app.persistence )

# radius used with GeoSpatial Query (meters)
app.radius              = 2000


###########
# HELPERS #
###########
@app.before_request
def prepare_buildings_collection():
   app.buildings     = BuildingView.get_collection()

##########
# ROUTES #
##########

# Buildings
@app.route('/api/v1.0/buildings/',methods=['GET'])
def get_buildings():
   buildings = list(app.buildings.find())
   for b in buildings:
      for f_id in b['floors']:
         del b['floors'][f_id]['rooms']

   return jsonify({ 'buildings': buildings })

@app.route('/api/v1.0/buildings/<b_id>',methods=['GET'])
def get_building_by_id(b_id):
   building = app.buildings.find_one({'_id':b_id})
   if not building:
       abort(404)
   return jsonify(building)

@app.route('/api/v1.0/buildings/near/<float:lat>/<float:lng>',methods=['GET'])
def get_buildings_near_position(lat,lng):
   r = request.args.get('radius') or app.radius
   if (not lat) or (not lng):
      abort(404)

   geo_json_point = {
      '$geometry' : {
         'type'         : 'Point',
         'coordinates'  : [ lng , lat ] },
         '$maxDistance' : int(r)
   }

   buildings   = list(app.buildings.find({ 'coordinates' : { '$near' : geo_json_point } }))

   return jsonify({ 'buildings': buildings })

# Categories
@app.route('/api/v1.0/categories/',methods=['GET'])
def get_categories():
   return 0

# Rooms


