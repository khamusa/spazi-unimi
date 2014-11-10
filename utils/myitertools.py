from itertools import tee, chain

def pairwise(iterable):
   """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
   a, b = tee(iterable)
   next(b, None)
   return zip(a, b)

def circular_pairwise(iterable):
   """s -> (s0,s1), (s1,s2), (s2, s3), ... (sn, s0) """
   return chain(pairwise(iterable), [(iterable[-1], iterable[0])])


def partition(pred, iterable):
 'Use a predicate to partition entries into false entries and true entries'
 # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
 t1, t2 = tee(iterable)
 return filterfalse(pred, t1), filter(pred, t2)
