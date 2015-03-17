from model.drawable     import Point, Text
from utils.logger       import Logger
import re, json

class FloorInference:
   """
   This class supplies auxiliary methods to infer the floor name/identification.
   """
   config_file = "config/floor_inference.json"
   with open(config_file) as cf:
      FLOOR_DICT = json.load(cf)

   @classmethod
   def get_identifier(self, filename, grabber):
      """
      Given two potential floor identifiers and choose the best one.

      Arguments:
      - filename: name of the dxf floor file;
      - grabber: dxfgrabber istance result of the dxf parsing.

      Returns:
      - a string representing the best id fouded for the floor;
      - False in case of conflict.

      Take an id from the filename and a group of ids from the "cartiglio"
      layers. Returns the best id and in case of conflicts prints messages with
      the logger.
      """
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
            "from filename suffix but", cartiglio_id,
            "from layer \"CARTIGLIO\""
            ):
            Logger.warning("[SOLVED]", cartiglio_id, "will be used")

      return cartiglio_id or filename_id

   @classmethod
   def from_filename(self, filename):
      """
      Reads REGEX json file and applies each REGEX to the filename suffix.

      Arguments:
      - filename: name of the dxf floor file.

      Returns:
      - a string representing a floor identifier;
      - False.

      Returns a floor id if any match is found applying the regex, None
      otherwise.
      """
      suffix_match = re.match(".+_([^_]+)\.dxf", filename, re.I)
      if(suffix_match):
         suffix   = suffix_match.group(1)
         f_id     = self.fid_from_string(suffix, regex_key="suffix_regex")
         return f_id

      return False

   @classmethod
   def from_cartiglio(self, grabber):
      """
      Match texts in the dxfgrabber and return a set of possible ids.

      Arguments:
      - grabber: instance of dxfgrabber result of the dxf parsing.

      Returns:
      - a set of possible ids.

      From a dxfgrabber instance, reads the information on layer CARTIGLIO,
      trying to find significative texts. Adds the possible floor id to a set
      and return it, if possible texts not founded return an empty set.
      """
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
      """
      Find a possible floor id matching texts near the "PIANO" text.

      Arguments:
      - label_ac: position of the "PIANO" text;
      - texts: list of texts from the layer cartiglio.

      Returns:
      - a string representing a floor id;
      - False.

      """
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
      """
      Controls if a text is near the label_point.

      Arguments:
      - insert_point: position of the text;
      - label_point: position of the "PIANO" text.

      Returns:
      - True if the text are close enough;
      - False otherwise.

      Auxiliary method for inference from cartiglio
      """
      return (
         (label_point.x + 300 >= insert_point.x >= label_point.x - 100)  and
         (label_point.y       >  insert_point.y >= label_point.y - 100)
      )

   @classmethod
   def _extract_texts_from_cartiglio(self, grabber):
      """
      Returns text from the layers who contain the cartiglio.

      Arguments:
      - grabber: instance of dxfgrabber result of the dxf parsing.

      Returns: a list of texts.

      Auxiliary method for inference from cartiglio
      """
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
      """
      Sanitize the name of a layer.

      Arguments:
      - name: string representing the layer name.

      Returns:
      - a string representing the sanitized layer name.

      Auxiliary method for inference from cartiglio.
      """
      regex = "\{[^;]+;((\w+\s*)+)\.?\s*\}"
      m = re.match(regex, name)
      if(m):
         name = m.group(1)
      return name.strip()

   @classmethod
   def fid_from_string(self, name, regex_key = "name_regexes"):
      """
      Transform a string in a floor id using a regex.

      Arguments:
      - name: string we want match;
      - regex_key: string representing the key in the regex dictionary.

      Returns:
      - a string representing a floor id;
      - False.

      Given a potential string, tests wether or not the string is a valid floor
      name or filename suffix, according to the regex_key to be used.
      If the string IS valid, returns the floor_id associated, else it returns
      False
      """

      for floor_key in self.FLOOR_DICT:
         patterns = self.FLOOR_DICT[floor_key][regex_key]

         if floor_key == name.strip():
            return floor_key

         for p in patterns:
            if( re.match(p, name.strip(), re.I) ):
               return floor_key

      return False
