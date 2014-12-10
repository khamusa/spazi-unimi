class ORMAttrs:
   def __init__(self, attrs = None, external_id = "_id"):
      if external_id is not "_id" and external_id in attrs:
         attrs["_id"] = attrs[external_id]
         del attrs[external_id]

      self._attrs          = attrs or {}
      self._external_id    = external_id

      """Since __setitem__ is not called during ORMAttrs creation, we need
      to manually ensure id sanitization"""
      self._ensure_sanitize_id()

      self._changed  = False

   """Decorator that ensure external_id is treated transparently, but always
   saved to internal id (_id as used in mongo)"""
   def replace_external_key(decorated_method):

      def wrapper(self, key, *args, **kargs):
         if(key == self._external_id):
            key = "_id"

         return decorated_method(self, key, *args, **kargs)

      return wrapper

   """The __setitem__ ensures _id gets sanitized every time it is
   assigned"""
   @replace_external_key
   def __setitem__(self, key, value):
      old = self._attrs.get(key)

      self._attrs[key] = value
      self._ensure_sanitize_id()

      if old != self._attrs.get(key):
         self._changed  = True

   """Just delegates attributes retrieval to native dictionary"""
   @replace_external_key
   def __getitem__(self, key):
      return self._attrs[key]

   """Just delegates contains to native dictionary"""
   @replace_external_key
   def __contains__(self, key):
      return key in self._attrs

   """Optional get, delegates to native dict method"""
   @replace_external_key
   def get(self, key, default = None):
      return self._attrs.get(key, default)

   """Ensure _ids are always saved as a string, no leading or trailing spaces"""
   def _ensure_sanitize_id(self):
       if("_id" in self._attrs):
         self._attrs["_id"] = self.sanitize_id(self._attrs["_id"])

   @classmethod
   def sanitize_id(klass_or_instance, id):
      return str(id).strip()


class ORMModel:

   def __init__(self, new_attrs = None):
      self._attrs    = ORMAttrs(new_attrs)
      self._changed  = False

   """Double semantics: this method behaves both as a getter of
   attributes (if no argument is supplied) and as a setter of attrs,
   if a dictionary is passed. In the later case it's keys will be
   merged into the object's attributes"""
   def attrs(self, new_attrs = None):
      if(new_attrs):
         self._merge_new_attrs(new_attrs)
      else:
         return self._attrs

   """Merges a dictionary with current instances attributes, key by key"""
   def _merge_new_attrs(self, new_attrs):
      for k in new_attrs:
         self._attrs[k] = new_attrs[k]

   """Sets the class Persistence Manager to be used"""
   @classmethod
   def set_pm(klass, pm):
      ORMModel._pm = pm

   @classmethod # can actually be called on instances
   def get_collection(klass_or_instance):
      """Explicit reference to ORMModel so that the method behaves
      the same being called both on instances and class"""
      return ORMModel._pm[klass.collection_name()]

   @classmethod # can actually be called on instances
   def collection_name(klass_or_instance):
      return klass_or_instance.__name__.lower()

   @classmethod # can actually be called on instances
   def sanitize_id(klass_or_instance, id):
      return ORMAttrs.sanitize_id(id)


   """

      ORM INTERFACE METHODS

   """

   """Retrieves from database a document and returns an instance representing it.

   Returns none if query returns no results"""
   @classmethod
   def find(klass, id):
      obj = klass.get_collection().find( { "_id" : klass.sanitize_id(id) })
      if(obj):
         return klass(obj)

      return None



