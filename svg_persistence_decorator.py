import svgwrite, random

class SVGPersistenceDecorator:

   def __init__(self, persistence):
      self._decorated = persistence

   def floor_write(self, floor):
      svg = svgwrite.Drawing()
      for r in floor.rooms:
         color    = "rgb({}, {}, {})".format(int(random.random()*200), int(random.random()*200), int(random.random()*200))
         points   = svg.polyline( ( (p.x, p.y) for p in r.points ), fill=color, stroke="#666")

         svg.add(points)

         for t in r.texts:
            svg.add(svg.text(t.text, t.anchor_point))

      svg.filename = "assets/test.svg"
      svg.save()
      self._decorated.floor_write(floor)
