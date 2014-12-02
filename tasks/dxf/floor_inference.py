import re
import json
import os
from model.drawable     import Point, Text
from utils.logger       import Logger

class FloorInference:
   """This class supplies auxiliary methods to infer the floor name / identification"""

   config_file = "config/floor_inference.json"
   with open(config_file) as cf:
      FLOOR_DICT = json.load(cf)

   @classmethod
   def get_identifier(self, filename, grabber):
      """Given two potential floor identifiers, choose the best one, or return
      None if they're conflicting"""

      filename_id    = self.from_filename(filename)
      possible_ids   = self.from_cartiglio(grabber)

      if(len(possible_ids) > 1):
         Logger.warning("Multiple floor identifiers inferred from layer \"CARTIGLIO\":");

         if(filename_id in possible_ids):
            Logger.info("[DECIDED] One of them equals the id obtained from the filename.")
            return filename_id
         else:
            Logger.error("[UNDECIDABLE] Multiple cartiglios in file?")
            return False

      cartiglio_id = len(possible_ids) and possible_ids.pop()

      if filename_id and cartiglio_id and (filename_id != cartiglio_id):
         Logger.warning("The floor identification issues a conflict:", filename_id, "from filename suffix but", cartiglio_id, "from layer \"CARTIGLIO\"")
      elif not filename_id and not cartiglio_id:
         Logger.error("No floor identification was possible from filename nor \"CARTIGLIO\" layer information")

      return cartiglio_id or filename_id

   @classmethod
   def from_filename(self, filename):
      """Reads REGEX json file and applies each REGEX to the filename suffix.

      Returns a floor identifier if any match is found, None otherwise."""

      suffix_match = re.match(".+_([^_]+)\.dxf", filename, re.I)
      if(suffix_match):
         suffix   = suffix_match.group(1)
         f_id     = self._floor_id_from_name_or_file_suffix(suffix, regex_key="suffix_regex")
         return f_id

      return False

   @classmethod
   def from_cartiglio(self, grabber):
      """From a dxfgrabber instance, reads the information on layer CARTIGLIO,
      trying to figure out which floor the dxf file refer to"""
      texts = self._extract_texts_from_cartiglio(grabber)

      label_position = None
      possible_ids = set()
      for t in texts:

         m = re.match("(pianta\s+)?piano\s+((\w+\.?\s*)+)", t.text, re.I)
         new_id = None
         if(m):
            new_id = self._floor_id_from_name_or_file_suffix(m.group(2))
         elif(t.text == "PIANO"):
            new_id = self._find_text_value_for_piano_label(t.anchor_point, texts)

         if(new_id):
            possible_ids.add(new_id)

      return possible_ids

   @classmethod
   def _find_text_value_for_piano_label(self, label_ac, texts):
      possible_texts = [
            t for t in texts
            if self._is_possible_text_for_label(t.anchor_point, label_ac) and
               self._floor_id_from_name_or_file_suffix(t.text) and
               t.text != "PIANO"
         ]

      possible_texts.sort( key = lambda s : abs(label_ac.x - s.anchor_point.x) )

      if len(possible_texts) > 0:
         return self._floor_id_from_name_or_file_suffix(possible_texts[0].text)

      return False

   @classmethod
   def _is_possible_text_for_label(self, insert_point, label_point):
      """Auxiliary method for inference from cartiglio"""
      return (
          (label_point.x + 300 >= insert_point.x >= label_point.x - 100)  and
          (      label_point.y >  insert_point.y >= label_point.y - 100)
         )

   @classmethod
   def _extract_texts_from_cartiglio(self, grabber):
      """Auxiliary method for inference from cartiglio"""
      def get_text(p):
         return self.sanitize_layer_name(
                  ( hasattr(p, "text") and p.text or p.plain_text()) or
                  ( hasattr(p, "rawtext") and p.rawtext ) or ""
               )

      return [
               Text( get_text(p), Point(p.insert) )
               for p in grabber.entities
               if re.match("CARTIGLIO", p.layer, re.I) and
                  (p.dxftype == "MTEXT" or p.dxftype == "TEXT")
            ]

   @classmethod
   def sanitize_layer_name(self, name):
      """Auxiliary method for inference from cartiglio"""
      regex = "\{[^;]+;((\w+\s*)+)\.?\s*\}"
      m = re.match(regex, name)
      if(m):
         name = m.group(1)
      return name.strip()

   @classmethod
   def _floor_id_from_name_or_file_suffix(self, name, regex_key = "name_regexes"):
      for floor_info in self.FLOOR_DICT:
         patterns = floor_info[regex_key]
         for p in patterns:
            if( re.match(p, name.strip(), re.I) ):
               return floor_info["id"]

      return False

