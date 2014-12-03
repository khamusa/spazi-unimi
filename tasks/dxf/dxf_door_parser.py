import math
from dxfgrabber.entities import Line, Insert

class DXFDoorParser:
   def parse_doors(self):
      def is_valid_door(ent):
         """Domanda: ma sono effettivamente sempre di tipo Insert, gli oggetti di porta?"""
         return type(ent) in [Insert] and ent.layer in self.valid_door_layers

      doors = ( el for el in self._grabber.entities if is_valid_door(el) )

      blocks = {}

      for d in doors:
         if d.name not in blocks:
            blocks[d.name] = self.parse_door_block(d.name)

      print(blocks)

   def parse_door_block(self, block_name):
      def calc_distance(start, end):
         x = abs(start[0] - end[0])
         y = abs(start[1] - end[1])
         return math.sqrt(x*x + y*y)

      def valid_lines_min_distance(line1, line2):
         return min( [
               calc_distance(line1.start, line2.start),
               calc_distance(line1.start, line2.end),
               calc_distance(line1.end, line2.end),
               calc_distance(line1.end, line2.start)
            ] ) < 8

      def print_a_line(p1, p2):
         print("{0:10.2f} {1:10.2f} -> {2:10.2f} {3:10.2f}".format( p1[0],
            p1[1], p2[0], p2[1]) )

      print("Cercando block", block_name)
      block          = self._grabber.blocks[block_name]
      block_entities = [
                        el for el in block._entities
                           if type(el) == Line and
                              calc_distance(el.start, el.end) < 15
                       ]

      if block_name == "P55-2U":
         print("P55-2U TROVATA! ########################")
         print([
                        el for el in block._entities
                           if type(el) == Line
                       ])



      valid_lines = []

      # verifica che i segmenti trovati siano abbastanza vicini almeno a un
      # altro segmento
      print("LInee originali")
      for line in block_entities:
         print_a_line(line.start, line.end)
         if line not in valid_lines:
            for other in block_entities:
               if( valid_lines_min_distance(line, other) and line != other ):
                  valid_lines.append(line)
                  valid_lines.append(other)
                  continue

      # trova il bounding box dei segmenti trovati
      minX = float("+inf");
      minY = float("+inf");
      maxX = float("-inf");
      maxY = float("-inf");
      for p in valid_lines:
         minX = min([minX, p.start[0], p.end[0]])
         minY = min([minY, p.start[1], p.end[1]])
         maxX = max([maxX, p.start[0], p.end[0]])
         maxY = max([maxY, p.start[1], p.end[1]])

      bounding_box = ( (minX, minY), (maxX, maxY) )

      def get_proportions(p1, p2):
         return abs(p1[0] - p2[0]) / abs(p1[1] - p2[1])

      prop = get_proportions(*bounding_box)

      if ( .5 > prop > 2 ):
         return None

      # START DEBUGGING STUFF #
      print("trovato ", len(valid_lines), "linee\n")
      print("Bounding box:", bounding_box)
      import svgwrite
      svg = svgwrite.Drawing()
      for p in valid_lines:
         svg.add(
            svg.line(
                  (p.start[0] - minX, p.start[1] - minY),
                  (p.end[0] - minX, p.end[1] - minY),
                  stroke="#FF0000",
                  stroke_width = 2
               )
         )

         print_a_line(p.start, p.end)
      svg.filename="assets/test_"+block_name
      svg.save()
      # END DEBUGGING STUFF #

      # restituiamo il bounding box
      return bounding_box
