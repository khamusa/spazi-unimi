from model                 import Building
from tasks.floor_drawer    import FloorDrawer
from utils.logger          import Logger
import os

class SVGTask():
   def __init__(self, config):
      """
      Builds a SVGTask object.

      Arguments:
      - config: a config manager reference, from which retrieve the path of
      preprocessed svg folder
      """
      self._svg_folder  = config["folders"]["data_svg_preprocessed_output"]

   def perform_svg_update(self, b_ids = None):
      """
      Call the perform_maps_update on every building or on a list of buildings
      specified with a list of b_ids.

      Arguments:
      - b_ids: a list of string representing b_ids.

      Returns: None.
      """

      query = { "$and" : [
            { "merged.floors" : {"$exists": True} },
            { "dxf.floors" : {"$exists": True} }
         ] }

      if  b_ids:
         query["_id"] = { "$in": b_ids }

      buildings   = Building.where(query)

      for building in buildings:
         self.perform_maps_update(building)

   def perform_maps_update(self, building):
      """
      Call the perform_map_update on every floor in the dxf key of the building
      dictionary.

      Arguments:
      - building: a dictionary representing a building we want to update/create the
      svg maps.

      Returns: None.
      """
      with Logger.info("Generating floor maps for", str(building)):
         for floor in building["merged"]["floors"]:
            Logger.info("Generating map for floor: ", floor["f_id"])
            svg      = FloorDrawer.draw_floor(floor)

            filename = self.prepare_path_and_filename(building["_id"], floor["f_id"])
            svg.saveas(filename)

   def prepare_path_and_filename(self, b_id, f_id):
      """
      Returns a complete filename for the svg (path + filename + extension).
      If the path not exists creates it.

      Arguments:
      - b_id: a string representing the building id;
      - f_id: a string representing the floor id of the svg file.

      Returns: a string representing the complete filename of the svg file.
      """
      path = os.path.join(self._svg_folder, b_id)
      if not os.path.exists(path):
         os.makedirs(path)
      return os.path.join(self._svg_folder, b_id, b_id + "_" + f_id + ".svg")
