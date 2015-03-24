from flask  import Flask, jsonify
from model.building_view  import BuildingView

app = Flask(__name__)


###########
# HELPERS #
###########

##########
# ROUTES #
##########
@app.route('/api/v1.0/buildings/',methods=['GET'])
def buildings():
   return jsonify({ 'buildings':['1','2','3'] })

@app.route('/api/v1.0/buildings/<string:b_id>',methods=['GET'])
def building_by_id(b_id):
   return jsonify({ '1' : 'nope' })

