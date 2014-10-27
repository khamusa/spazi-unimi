import json
import os
from json_room_encoder import JsonRoomEncoder

class PersistenceManager():

    def __init__(self, config):
        self._cm = config

    def floor_write(self, floor):
        base_building_path = os.path.join(
            self._cm["folders"]["data_dxf_preprocessed_output"],
            floor.building_name)

        if not os.path.exists(base_building_path):
            os.makedirs(base_building_path)

        filename = self._cm["filepaths"]["preprocessed_floor_format"].format(building_name = floor.building_name, floor_name = floor.floor_name)
        full_file_path = os.path.join(base_building_path, filename + ".json")
        with open(full_file_path, "w") as fp:
            json.dump(floor, fp, cls = JsonRoomEncoder, indent = self._cm["json_indent"])
