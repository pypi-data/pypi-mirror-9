"""GCL utility functions."""

import gcl

class ExpressionWalker(object):
  """Defines the interface for walk()."""

  def enterTuple(self, tuple, path):
    """Called for every tuple.

    If this returns False, the elements of the tuple will not be recursed over
    and leaveTuple() will not be called.
    """
    pass

  def leaveTuple(self, tuple, path):
    pass

  def visitError(self, key, ex, path):
    pass

  def visitScalar(self, key, value, path):
    pass


def walk(tuple, walker, path=None):
  """Walks the _evaluated_ tree of the given GCL tuple.

  The appropriate methods of walker will be invoked for every element in the
  tree.
  """
  path = path or []
  if not isinstance(tuple, gcl.Tuple):
    raise ValueError('Argument to walk() must be a GCL tuple')

  if walker.enterTuple(tuple, path) is False:
    return  # Do nothing

  keys = sorted(tuple.keys())
  for key in keys:
    try:
      value = tuple[key]
    except Exception as e:
      walker.visitError(key, e, path)
      continue

    if isinstance(value, gcl.Tuple):
      walk(value, walker, path + [key])
    else:
      walker.visitScalar(key, value, path)

  walker.leaveTuple(tuple, path)
