import re
import json

class FloorInference:
   """This class supplies auxiliary methods to infer the floor name / identification"""

   config_file = "config/floor_inference.json"
   with open(config_file) as cf:
      FLOOR_DICT = json.load(cf)

   print(FLOOR_DICT[5])

   @classmethod
   def choose_identifier(self, id1, id2):
      """Given two potential floor identifiers, choose the best one, or return
      None if they're conflicting"""
      pass

   @classmethod
   def from_filename(self, filename):
      """Reads REGEX json file and applies each REGEX to the filename suffix.

      Returns a floor identifier if any match is found, None otherwise."""
      pass

   @classmethod
   def from_cartiglio(self, grabber):
      """From a dxfgrabber instance, reads the information on layer CARTIGLIO,
      trying to figure out which floor the dxf file refer to"""
      texts = self._get_texts_from_cartiglio(grabber)

      label_position = None
      for (insert_point, t) in texts:
         m = re.match("(pianta\s+)?piano\s+((\w+\.?\s*)+)", t, re.I)
         if(m):
            floor_id = self._floor_id_from_name(m.group(2))
            if(floor_id):
               return floor_id

         if(t == "PIANO"):
            label_position = insert_point
            break

      # Strategy two has found the label 'PIANO'
      if(label_position):
         possible_texts = [
               self._floor_id_from_name(t) for insert_point, t in texts
               if self._is_possible_text_for_label(insert_point, label_position) and
                  self._floor_id_from_name(t) and
                  t != "PIANO"
            ]

         return (len(possible_texts) > 0) and possible_texts[0]

      return False

   @classmethod
   def _is_possible_text_for_label(self, insert_point, label_position):
      """Auxiliary method for inference from cartiglio"""
      label_x, label_y, _ = label_position
      return (
          (label_x + 250 >= insert_point[0] >= label_x - 100)  and
          (label_y > insert_point[1] >= label_y - 100)
         )

   @classmethod
   def _get_texts_from_cartiglio(self, grabber):
      """Auxiliary method for inference from cartiglio"""
      def get_text(p):
         return self.sanitize_layer_name(
                  ( hasattr(p, "text") and p.text ) or
                  ( hasattr(p, "rawtext") and p.rawtext )
               )

      return [
               (p.insert, get_text(p))
               for p in grabber.entities
               if re.match("CARTIGLIO", p.layer, re.I) and
                  p.dxftype == "MTEXT"
            ]

   @classmethod
   def sanitize_layer_name(self, name):
      """Auxiliary method for inference from cartiglio"""
      regex = "\{[^;]+;((\w+\s*)+)\.?\s*\}"
      m = re.match(regex, name)
      if(m):
         name = m.group(1)
      return name

   @classmethod
   def _floor_id_from_name(self, name):
      for floor_info in self.FLOOR_DICT:
         patterns = floor_info["name_regexes"]
         for p in patterns:
            if( re.match(p, name.strip(), re.I) ):
               return floor_info["id"]+" - "+name

      return "DID NOT MATCH DICT - "+name

if __name__ == "__main__":
   import sys, dxfgrabber, shutil, os
   files = sys.argv[1:]
   s = dict()

   for f in files:
      grabber = dxfgrabber.readfile(f, { "resolve_text_styles": False } )

      n = str(FloorInference.from_cartiglio(grabber)).lower()

      basename = os.path.basename(f)
      valid_filename_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
      directory = "assets/dxf/tutti_con_audit/"+''.join(c for c in n if c in valid_filename_chars)+"/"

      if( not os.path.exists(directory) ):
         os.makedirs(directory)

      print(n)
      shutil.copy(f, directory)

      if(n not in s):
         s[n] = 1
      else:
         s[n] = s[n] + 1

   for key in s:
      print(key, s[key])

