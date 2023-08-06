import fn
def hash_join(left_key, right_key, merge_op, left, right):
  """
  Preform a join similar to a SQL join. Implementation note
  the list of objects on the right will be hashed using the 
  value produced by the right_key function and stored in memory.
  If using two iterators with one that does not fit completely in memory
  it should be used as the left value.

  TODO: Allow right_key to map multiple values to the same key.

  :param left_key: function that returns the value used for the left comparison
  :param right_key: function that returns the right side value from
  :param merge_op: function that will merege the left and right objects
  :param left: iterator of objects 
  :param right: iterator of objecs that will be hashed

  Example:

  >>> t1 = ((1,'a'),)
  >>> t2 = (('b', 1),)
  >>> hash_join(
  ...  lambda a: a[0],
  ...  lambda b: b[1],
  ...  lambda a,b: a+b,
  ...  t1,
  ...  t2
  ... )
  """
  probe = dict(fn.fmap(
    fn.juxt(right_key, fn.identity),
    right
  ))
  
  for left_rec in left:
    right_rec = probe.get(left_key(left_rec))
    
    rec = merge_op(left_rec, right_rec)
    if rec:
      yield rec 
