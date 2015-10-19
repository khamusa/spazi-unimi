import xml.dom.minidom
import urllib.request

class RoomTimeTable:
   def __init__(self,b_id,r_id):
      self.b_id      = b_id
      self.r_id      = r_id
      self.base_url  = "http://spazididattici.unimi.it/EasyRoom/feed.php?type=week&space=room&code={}{}{}"
      self.spacer    = "%23" # is #23 encoded used by easyroom in order to split b_id and r_id
      self.exists    = False

      try:
         response       = urllib.request.urlopen( self.base_url.format(b_id,self.spacer,r_id) )
         self.parseEvents(response.read())

      except urllib.error.HTTPError:
         self.exists = False
         return None


   def parseEvents(self,response):
      feed = xml.dom.minidom.parseString(response)
      self.events = [self.parseEvent(e) for e in feed.getElementsByTagName('event')]

   def parseEvent(self,eventXML):
      event = {}
      for nodeName in ["day","from","to","short_description"]:
         event[nodeName] = self.getNodeValue(eventXML.getElementsByTagName(nodeName)[0])
      return event

   def getNodeValue(self,node):
      return node.firstChild.nodeValue

