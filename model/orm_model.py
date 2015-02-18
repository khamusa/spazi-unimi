import types

def around_callbacks(funz):
   """
   Decorator that, given a function, adds before and after callbacks to it.

   The implementing class must define a before_callbacks and after_callbacks
   dictionary in which the callbacks may be found. Can only be used over
   instance methods.
   """

   def _dispatch_callback(the_self, callback):
      if isinstance(callback, str):
         callback = getattr(the_self, callback)

      if type(callback) is types.MethodType:
         callback()
      else:
         callback(the_self)

   def wrapper(self, *args, **kargs):
      context = funz.__name__
      klass_name = self.__class__.__name__
      #1a - fire all CLASS before callbacks
      if klass_name in self.before_callbacks and context in self.before_callbacks[klass_name]:
         for callback in self.before_callbacks[klass_name][context]:
            _dispatch_callback(self, callback)

      #1b - fire all INSTANCE before callbacks
      if hasattr(self, "before_callbacks_single") and context in self.before_callbacks_single:
         for callback in self.before_callbacks_single[context]:
            _dispatch_callback(self, callback)

         self.before_callbacks_single[context] = []

      #2 - call original save function
      ret = funz(self, *args, **kargs)

      #3a - fire all CLASS after callbacks
      if klass_name in self.after_callbacks and context in self.after_callbacks[klass_name]:
         for callback in self.after_callbacks[klass_name][context]:
            _dispatch_callback(self, callback)

      #3b - fire all INSTANCE after callbacks
      if hasattr(self, "after_callbacks_single") and context in self.after_callbacks_single:
         for callback in self.after_callbacks_single[context]:
            _dispatch_callback(self, callback)

         self.after_callbacks_single[context] = []

      #4 - make sure to return the same thing as the original function
      #returned
      return ret
   return wrapper


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
      return self._attrs == other._attrs

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

   def as_dict(self):
      return self._attrs


class ORMModel:

   before_callbacks = {}
   after_callbacks  = {}

   def __init__(self, new_attrs = None, external_id = "_id"):
      self._attrs    = ORMAttrs(new_attrs, external_id = external_id)

   def __eq__(self, other):
      return ( self._attrs == other._attrs )

   """Double semantics: this method behaves both as a getter of
   attributes (if no argument is supplied) and as a setter of attrs,
   if a dictionary is passed. In the later case it's keys will be
   merged into the object's attributes"""
   def attrs(self, new_attrs = None):
      if(new_attrs):
         self._merge_new_attrs(new_attrs)
      else:
         return self._attrs

   def attr(self, key, value = None):
      if value :
         self._attrs[key] = value
         return
      return self._attrs.get(key,None)

   def has_attr(self, key):
      return key in self._attrs


   """Merges a dictionary with current instances attributes, key by key"""
   def _merge_new_attrs(self, new_attrs):
      for k in new_attrs:
         self._attrs[k] = new_attrs[k]

   def set_changed(self, value=True):
      self._attrs._changed = value

   def is_changed(self):
      return self._attrs._changed

   """

      GENERAL CLASS METHODS
# Building, RoomCategory
   """

   """Sets the class Persistence Manager to be used"""
   @classmethod
   def set_pm(klass, pm):
      ORMModel._pm = pm

   @classmethod # can actually be called on instances
   def get_collection(klass_or_instance):
      """Explicit reference to ORMModel so that the method behaves
      the same being called both on instances and class"""
      return ORMModel._pm.get_collection(klass_or_instance.collection_name())

   @classmethod # can actually be called on instances
   def collection_name(klass_or_instance):
      return klass_or_instance.__name__.lower()

   @classmethod # can actually be called on instances
   def sanitize_id(klass_or_instance, id):
      return ORMAttrs.sanitize_id(id)

   """

      ORM INTERFACE METHODS

   """

   @classmethod
   def find_or_create_by_id(klass, id):
      res = klass.find(id)
      if not res:
         res = klass({"_id":id})
      return res

   @around_callbacks
   def save(self):
      klass_name = self.__class__.__name__

      if self.is_changed :
         self._pm.save(self.collection_name(), self._attrs.as_dict())

   @classmethod
   def clean(self):
      self._pm.clean_collection(self.collection_name())

   @around_callbacks
   def destroy(self):
      self._pm.destroy_by_id(self.collection_name(), self.attr("_id"))

   """Retrieves from database a document and returns an instance representing it.

   Returns none if query returns no results"""
   @classmethod
   def find(klass, id):
      return klass.find_by_field("_id", klass.sanitize_id(id))

   @classmethod
   def find_by_field(klass, field_name, value):
      obj = klass.get_collection().find_one( { field_name : value })

      res = None
      if(obj):
         res = klass(obj)
         res.set_changed(False)

      return res

   @classmethod
   def where(klass, query):
      """
      Retrieves a list of objects from database.

      Arguments:
      - query: a MONGO filtering query

      Return value: a generator of ORMModel objects.
      """
      docs = klass.get_collection().find( query )

      def generate_model_obj(document):
         document = klass(document)
         document.set_changed(False)
         return document

      results = ( generate_model_obj(doc) for doc in docs )
      return results

   """

      CALLBACK POLICY METHODS

   """

   @classmethod
   def listen(klass, event, callback_name_or_callable):
      """
      Adds a before or after callback to function calls.

      Arguments:
      - event: a string representing the event to listen to. Must be on the
      format before_<methodname> or after_<methodname> where <methodname>
      is the name of the instance method whose calls you want to listen to.
      - callback_name_or_callable: either a string representing the method to be
      called or a callable object. If a string is used, It MUST be an instance
      method. If a callable is supplied, it must accept exactly one argument,
      which will be a reference to the instance itself.

      Return value: None

      Usage:
      ORMModel.listen("after_save", "nice_method")
      ORMModel.listen("before_destroy", "other_beautiful_method")

      Example:
      >>> from model import ORMModel
      >>> from mock import MagicMock
      >>> ORMModel.set_pm(MagicMock())
      >>> b = ORMModel({ "_id": 123 })
      >>> before = lambda s: print("Before Save executed")
      >>> after  = lambda s: print("After Save executed")
      >>> ORMModel.listen("before_save", before)
      >>> ORMModel.listen("after_save", after)
      >>> b.save()
      Before Save executed
      After Save executed

      Note: the second part of the event name identifies a method name. The
      callbacks will be executed before/after that method is executed. In order
      for it to be possible, the method must have been DECORATED with
      @around_callbacks. Currently only before_save and before_update are
      supported.
      """
      evt_type, evt_action = klass._listen_split_event(event)

      if evt_type is "before":
         callbacks = klass.before_callbacks
      else:
         callbacks = klass.after_callbacks

      klass_name = klass.__name__
      if klass_name not in callbacks:
         callbacks[klass_name] = {}

      if evt_action not in callbacks[klass_name]:
         callbacks[klass_name][evt_action] = []

      callbacks[klass_name][evt_action].append(callback_name_or_callable)

   @classmethod
   def before_save(klass, callback_name):
      klass.listen("before_save", callback_name)

   @classmethod
   def after_save(klass, callback_name):
      klass.listen("after_save", callback_name)

   @classmethod
   def _listen_split_event(klass, event):
      """
      Given an event string in the format "type_method" (i.e. before_save,
      after_destroy), splits the event name separating the type and method,
      validates the event type (before or after only) and return both
      as a tuple.

      Return value: a tuple of strings representing type and method.
      """
      before = event.startswith("before_")
      after  = event.startswith("after_")

      if not(before) and not(after):
         raise RuntimeException("Not implemented event type: "+event)

      evt_type = before and event[7:] or event[6:]

      return (before and "before" or "after", evt_type)

   """

      INTANCE CALLBACK POLICY METHODS

   """
   def listen_once(self, event, callback_name_or_callable):
      """
      Adds a before or after callback to instances. Does not affect other
      instances, and the callback is fired exactly once, even if the event
      is verified multiple times.

      Instance callbacks are executed AFTER class callbacks.

      Arguments:
      - event: a string representing the event to listen to. Must be on the
      format before_<methodname> or after_<methodname> where <methodname>
      is the name of the instance method whose calls you want to listen to.
      - callback_name_or_callable: either a string representing the method to be
      called or a callable object. If a string is used, It MUST be an instance
      method. If a callable is supplied, it must accept exactly one argument,
      which will be a reference to the instance itself.

      Return value: None

      Note: the second part of the event name identifies a method name. The
      callbacks will be executed before/after that method is executed. In order
      for it to be possible, the method must have been DECORATED with
      @around_callbacks. Currently only before_save and before_update are
      supported.
      """

      evt_type, evt_action = self._listen_split_event(event)

      if evt_type is "before":
         if not hasattr(self, "before_callbacks_single"):
            self.before_callbacks_single = {}

         callbacks = self.before_callbacks_single
      else:
         if not hasattr(self, "after_callbacks_single"):
            self.after_callbacks_single = {}

         callbacks = self.after_callbacks_single

      if evt_action not in callbacks:
         callbacks[evt_action] = []

      callbacks[evt_action].append(callback_name_or_callable)
