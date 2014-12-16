def subtract_dict(d, valid_keys):
   """Returns a new dictionary by removing from d any keys that is not
   present in valid_keys, which may be a set, list or another dict (any
   iterable, actually)"""
   return { k: d[k] for k in d if k in valid_keys }
