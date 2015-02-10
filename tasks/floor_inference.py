import re
import json
import os, sys
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
         with Logger.warning(
               "Multiple floor identifiers inferred from layer \"CARTIGLIO\" (",
               str(", ".join(s for s in possible_ids)),
               "):"
            ):

            if(filename_id in possible_ids):
               Logger.warning(
                     "[SOLVED] One of them equals the id obtained from the filename: "+filename_id
                  )
               return filename_id
            else:
               Logger.warning(
                     "[UNDECIDABLE] Multiple cartiglios in file?"
                  )
               return False

      cartiglio_id = len(possible_ids) and possible_ids.pop()

      if filename_id and cartiglio_id and (filename_id != cartiglio_id):
         with Logger.warning(
            "The floor identification issues a conflict:", filename_id,
            "from filename suffix but", cartiglio_id, "from layer \"CARTIGLIO\"",
            out = sys.stdout
            ):
            Logger.warning("[SOLVED]", cartiglio_id, "will be used")

      return cartiglio_id or filename_id

   @classmethod
   def from_filename(self, filename):
      """Reads REGEX json file and applies each REGEX to the filename suffix.

      Returns a floor identifier if any match is found, None otherwise."""

      suffix_match = re.match(".+_([^_]+)\.dxf", filename, re.I)
      if(suffix_match):
         suffix   = suffix_match.group(1)
         f_id     = self.fid_from_string(suffix, regex_key="suffix_regex")
         return f_id

      return False

   @classmethod
   def from_cartiglio(self, grabber):
      """From a dxfgrabber instance, reads the information on layer CARTIGLIO,
      trying to figure out which floor the dxf file refer to"""
      texts          = self._extract_texts_from_cartiglio(grabber)
      possible_ids   = set()

      for t in texts:
         strategy_1  = re.match("(pianta\s+)?piano\s+((\w+\.?\s*)+)", t.text, re.I)
         strategy_2  = t.text == "PIANO"

         found = None

         if strategy_1:
            found = self.fid_from_string(strategy_1.group(2))
         elif strategy_2:
            found = self._fid_from_piano_label(t.anchor_point, texts)

         if found:
            possible_ids.add(found)

      return possible_ids

   @classmethod
   def _fid_from_piano_label(self, label_ac, texts):
      possible_texts = [
            t for t in texts
            if self._points_are_close_enough(t.anchor_point, label_ac) and
               t.text != "PIANO"
         ]

      possible_texts.sort( key = lambda s : abs(label_ac.x - s.anchor_point.x) )

      for pt in possible_texts:
         fid = self.fid_from_string(pt.text)
         if(fid):
            return fid

      return False

   @classmethod
   def _points_are_close_enough(self, insert_point, label_point):
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
   def fid_from_string(self, name, regex_key = "name_regexes"):
      """Given a potential string, tests wether or not the string is a valid floor
      name or filename suffix, according to the regex_key to be used

      If the string IS valid, returns the floor_id associated, else it returns
      False"""

      for floor_info in self.FLOOR_DICT:
         patterns = floor_info[regex_key]
         for p in patterns:
            if( re.match(p, name.strip(), re.I) ):
               return floor_info["id"]

      return False

