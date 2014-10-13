
class RoomText:
   def __init__(self, txt, anchor_point):
      self.text         = txt
      self.anchor_point = anchor_point 

   def __str__(self):
      return "Text({}, {})".format(self.text[0:15], self.anchor_point)

   def __repr__(self):
      return str(self)
