from flask                 import Flask, jsonify,abort,request
from model.building_view   import BuildingView
from bson.json_util        import dumps
from utils                 import ConfigManager
from persistence           import MongoDBPersistenceManager
from model.odm             import ODMModel

app                     = Flask(__name__)
app.app_config          = ConfigManager("config/general.json")
app.persistence         = MongoDBPersistenceManager(app.app_config)
ODMModel.set_pm( app.persistence )

# radius used with GeoSpatial Query (meters)
app.radius              = 2000


###########
# HELPERS #
###########
@app.before_request
def prepare_buildings_collection():
   app.buildings = BuildingView.get_collection()


##########
# ROUTES #
##########
@app.route('/api/v1.0/buildings/',methods=['GET'])
def get_buildings():
   return jsonify({ 'buildings': list(app.buildings.find()) })

@app.route('/api/v1.0/buildings/<b_id>',methods=['GET'])
def get_building_by_id(b_id):
   building = app.buildings.find_one({"_id":b_id})
   if not building:
       abort(404)
   return jsonify(building)

@app.route('/api/v1.0/buildings/near/<float:lat>/<float:lng>',methods=['GET'])
def get_buildings_near_position(lat,lng):
   r = request.args.get('radius') or app.radius
   if (not lat) or (not lng):
      abort(404)

   geo_json_point = {
      "$geometry" : {
         "type"         : "Point",
         "coordinates"  : [ lng , lat ] },
         "$maxDistance" : int(r)
   }

   buildings   = list(app.buildings.find({ "coordinates" : { "$near" : geo_json_point } }))

   return jsonify({ 'buildings': buildings })



