
class Drawable():
   """Base class for drawable objects, implement some ausiliary methods but no
   concrete behavior"""

   def traslated(self, *args, **kargs):
      """Immutable version of traslate"""
      return self.clone().traslate(*args, **kargs)

   def reflected_y(self, *args, **kargs):
      """Immutable version of reflecte_y"""
      return self.clone().reflect_y(*args, **kargs)

   def scaled(self, *args, **kargs):
      return self.clone().scale(*args, **kargs)

   def rotated(self, *args, **kargs):
      return self.clone().rotate(*args, **kargs)
