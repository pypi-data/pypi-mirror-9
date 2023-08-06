from itertools import repeat as repeat
from itertools import izip as izip
import math

def vectorize(f):
    """
    Input: a function that takes any number of arguments
    Output: vectorized version of the input function
    Example:
      f(x, y) = x + y
      F = vectorize(f)
      F([x, y, z], [a, b, c]) = [f(x, a), f(y, b), f(z, c)]
      F([x, y, z], a) = [f(x, a), f(y, a), f(z, a)]
      F(a, b) = f(a, b)

      The returned function fails when input iterable arguments have different lengths
    """
    def decorated(*args):
      if not any(hasattr(arg, '__iter__') for arg in args):
        return f(*args)

      newargs = []
      length = None
      for a in args:
        if not hasattr(a, '__iter__'):
          newargs.append(repeat(a))
          continue
        a = a if isinstance(a, (list, tuple)) else list(a)
        if length is None:
          length = len(a)
        assert len(a) == length, "Input has different lengths %s" % str(args)
        newargs.append(a)
      return [f(*i) for i in izip(*newargs)]
    return decorated


@vectorize
def vectorMultiply(x, y):
    return x * y

@vectorize
def vectorDivide(x, y):
    return x / y

@vectorize
def vectorAdd(x, y):
    return x + y

@vectorize
def vectorSubtract(x, y):
    return x - y

def vectorInnerProd(x, y):
    return sum(vectorMultiply(x, y))

@vectorize
def vectorAbs(x):
  return abs(x)

@vectorize
def vectorInverse(x):
  return 1.0 / x
