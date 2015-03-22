from .room           import Room
from .floor          import Floor
from .building       import Building
from .room_category  import RoomCategory
from .building_view  import BuildingView
from IPython import embed

def update_building_view(building):
   bv = BuildingView.create_from_building(building)
   bv.save()

Building.listen("after_save", update_building_view)

Building.listen("after_remove_deleted_buildings", BuildingView.remove_deleted_buildings)
