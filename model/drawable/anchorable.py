
class Anchorable():
   """Base class for anchorable elements, implement some handy methods for
   performing operations on the anchor point, and also a prototype for
   absolutization of the element, i.e.: converting its elements to absolutize
   coordinates"""

   def absolutize(self):
     """Trasform the current element in an absolute coordinates element

     The child classes most implement the method __entities__ that returns
     a sequence of translatable entities that compose the child object"""
     if hasattr(self, "__entities__"):
      entities = self.__entities__()
      for e in entities:
         e.traslate(*self.anchor_point)
      self.anchor_point.x = 0
      self.anchor_point.y = 0
     return self

   def absolutized(self):
     return self.clone().absolutize()

   def traslate_ac(self, *args, **kargs):
     return self.anchor_point.traslate(*args, **kargs)

   def reflect_y_ac(self, *args, **kargs):
     return self.anchor_point.reflect_y(*args, **kargs)

   def scale_ac(self, *args, **kargs):
      return self.anchor_point.scale(*args, **kargs)

   def rotate_ac(self, *args, **kargs):
      return self.anchor_point.rotate(*args, **kargs)

   def traslated_ac(self, *args, **kargs):
      return self.anchor_point.clone().traslate(*args, **kargs)

   def reflected_y_ac(self, *args, **kargs):
      return self.anchor_point.clone().reflect_y(*args, **kargs)

   def scaled_ac(self, *args, **kargs):
      return self.anchor_point.clone().scale(*args, **kargs)

   def rotated_ac(self, *args, **kargs):
      return self.anchor_point.clone().rotate(*args, **kargs)
