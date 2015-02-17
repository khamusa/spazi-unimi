
class DXFDataUpdater:

   def find_building_to_update(self, building_dict):
      """
      Finds on database or create a Buiding object to be updated with information
      contained by building_dict

      Arguments:
      - building_dict: a dictionary containing the new values to be inserted
      on the building.

      Returns a Building object.

      Finds a building on database using b_id as identifier, otherwise looks for a
      building using l_b_id. If none of the above succeeds, creates a new building
      object to be inserted on database.
      """
      b_id = building_dict.get("b_id", "")

      return (
               Building.find(b_id) or
               Building.find_by_field("merged.l_b_id", b_id) or
               Building( {"_id": b_id} )
               )

   def save_floor(self, building, floor):
      """
      Implements the DXF Data Update functionality, saving a floor information to
      an existing building document.

      Arguments:
      - building: a Building object representing the database object to be
      updated with the new floor information.
      - floor: a Floor object representing the data to be updated / inserted into
      database.

      Returns: None

      If a floor with the same f_id already exists on the current building, it
      is replaced by the new one. The floor ordering is ensured by the Building
      model itself.
      """

      new_floor = floor.to_serializable()
      del new_floor["b_id"]

      # Non vogliamo cancellare quanto c'è nel database, soltanto lo stesso floor
      dxf         = building.attr("dxf") or {}
      floors      = dxf.get("floors", [])

      # Se il floor corrente esiste gia' nel database, vogliamo sostituirlo
      for k, f in enumerate(floors):
         if f["f_id"] == floor.f_id:
            del floors[k]

      floors.append(new_floor)

      dxf["floors"] = floors
      building.attr("dxf", dxf)
      building.save()
