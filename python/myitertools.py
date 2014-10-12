from itertools import tee, chain

def pairwise(iterable):
   """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
   a, b = tee(iterable)
   next(b, None)
   return zip(a, b)

def circular_pairwise(iterable):
   """s -> (s0,s1), (s1,s2), (s2, s3), ... (sn, s0) """
   return chain(pairwise(iterable), [(iterable[-1], iterable[0])])