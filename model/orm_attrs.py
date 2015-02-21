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

      self._changed  = True


   def __eq__(self, other):
      """
      Defines equality politics based on attributes.
      """
      return self._attrs == other._attrs

   def replace_external_key(decorated_method):
      """
      Decorator that ensure external_id is treated transparently, but always
      saved to internal id (_id as used in mongo)
      """

      def wrapper(self, key, *args, **kargs):
         if(key == self._external_id):
            key = "_id"

         return decorated_method(self, key, *args, **kargs)

      return wrapper

   """
         PUBLIC ATTRIBUTES INTERFACE

   """

   @replace_external_key
   def __setitem__(self, key, value):
      """
      The __setitem__ ensures _id gets sanitized every time it is
      assigned, and also enforce attributes changed policy.
      """
      old = self._attrs.get(key)

      self._attrs[key] = value
      self._ensure_sanitize_id()

      if old != self._attrs.get(key):
         self._changed  = True

   @replace_external_key
   def __getitem__(self, key):
      """
      Item getter.
      Just delegates attributes retrieval to native dictionary
      """
      return self._attrs[key]

   @replace_external_key
   def __contains__(self, key):
      """
      Just delegates contains to native dictionary
      """
      return key in self._attrs

   @replace_external_key
   def get(self, key, default = None):
      """
      Optional get, delegates to native dict method
      """
      return self._attrs.get(key, default)

   def _ensure_sanitize_id(self):
      """
      Ensure _ids are always saved as a string, no leading or trailing spaces
      """
      if("_id" in self._attrs):
         self._attrs["_id"] = self.sanitize_id(self._attrs["_id"])

   @classmethod
   def sanitize_id(klass_or_instance, id):
      return str(id).strip()

   def as_dict(self):
      """
      Return a representation of the attributes as a dictionary. It is not a
      clone, and hence changes in the returned dictionary will propagate to
      the object attributes.
      """
      return self._attrs

   def _merge_new_attrs(self, new_attrs):
      """
      Merges a dictionary with current instances attributes, key by key
      """
      for k in new_attrs:
         self[k] = new_attrs[k]

   def set_changed(self, value=True):
      self._changed = value

   def is_changed(self):
      return self._changed

   """

      DEPRECATED METHODS

   """
   def attrs(self, new_attrs = None):
      """
      DEPRECATED: This method behaves both as a getter of attributes (if no
      argument is supplied) and as a setter of attrs, if a dictionary is passed.
      In the later case it's keys will be merged into the object's attributes
      """
      if(new_attrs):
         self._merge_new_attrs(new_attrs)
      else:
         return self._attrs

   def attr(self, key, value = None):
      """
      DEPRECATED: Return an attribute value or set it.

      Preferrable way is to use subscription for accessing
      attributes, or self.get in case a default is needed
      """
      if value :
         self[key] = value
         return
      return self.get(key, None)

   def has_attr(self, key):
      """
      DEPRECATED: Check wether or not an attribute is present. Preferrable to
      use the python syntax of "key" in object instead of object.has_attr(key).
      """
      return key in self
