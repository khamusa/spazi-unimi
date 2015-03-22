import types
from . import ODMAttrs

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
      klass = type(self) is type and self or self.__class__
      klass_name = klass.__name__
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

class ODMModel(ODMAttrs):

   before_callbacks = {}
   after_callbacks  = {}

   """

      GENERAL CLASS METHODS

   """

   @classmethod
   def set_pm(klass, pm):
      """
      Sets the class Persistence Manager to be used
      """
      ODMModel._pm = pm

   @classmethod # can actually be called on instances
   def get_collection(klass_or_instance):
      """
      Explicit reference to ODMModel so that the method behaves
      the same being called both on instances and class
      """
      return ODMModel._pm.get_collection(klass_or_instance.collection_name())

   @classmethod # can actually be called on instances
   def collection_name(klass_or_instance):
      return klass_or_instance.__name__.lower()

   @classmethod # can actually be called on instances
   def sanitize_id(klass_or_instance, id):
      return ODMAttrs.sanitize_id(id)

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
         self._pm.save(self.collection_name(), self.as_dict())

   @classmethod
   def clean(self):
      self._pm.clean_collection(self.collection_name())

   @around_callbacks
   def destroy(self):
      self._pm.destroy_by_id(self.collection_name(), self.attr("_id"))

   @classmethod
   def find(klass, id):
      """
      Retrieves from database a document and returns an instance representing it.

      Returns none if query returns no results
      """
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

      Return value: a generator of ODMModel objects.
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
      fodmat before_<methodname> or after_<methodname> where <methodname>
      is the name of the instance method whose calls you want to listen to.
      - callback_name_or_callable: either a string representing the method to be
      called or a callable object. If a string is used, It MUST be an instance
      method. If a callable is supplied, it must accept exactly one argument,
      which will be a reference to the instance itself.

      Return value: None

      Usage:
      ODMModel.listen("after_save", "nice_method")
      ODMModel.listen("before_destroy", "other_beautiful_method")

      Example:
      >>> from model import ODMModel
      >>> from mock import MagicMock
      >>> ODMModel.set_pm(MagicMock())
      >>> b = ODMModel({ "_id": 123 })
      >>> before = lambda s: print("Before Save executed")
      >>> after  = lambda s: print("After Save executed")
      >>> ODMModel.listen("before_save", before)
      >>> ODMModel.listen("after_save", after)
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
   def _listen_split_event(klass, event):
      """
      Given an event string in the fodmat "type_method" (i.e. before_save,
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
      fodmat before_<methodname> or after_<methodname> where <methodname>
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
