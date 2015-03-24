from flask                 import Flask, jsonify,abort
from model.building_view   import BuildingView
from bson.json_util        import dumps
from utils                 import ConfigManager
from persistence           import MongoDBPersistenceManager
from model.odm             import ODMModel

app                     = Flask(__name__)
app.app_config          = ConfigManager("config/general.json")
app.persistence         = MongoDBPersistenceManager(app.app_config)
ODMModel.set_pm( app.persistence )


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

