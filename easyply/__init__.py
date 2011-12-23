"""

Implementation notes:

Each rule, such as `production: SYM another (SYM another)?` is parsed
into a Rule object. It provides means of enumeration of possible permutations
of optional parameters and so on. The class itself and the parser are defined
in `nodes` and `parser`, respectively.

"""

from parser import parse as _parse
from itertools import combinations
from nodes import NamedTerm

class NoDocstringError(Exception):
    pass

def expand_conditionals(rule, format = True):
  """
    Takes a rule (either a Rule object or a string, it case of which it's parsed
    to a Rule object) and returns a list of all possible optional parameter cases.
    The optional parameter `format` controls the output. If it's true,
    `expand_conditionals` will output a list of strings. If it's false, it will
    return a list of flattened Rule objects.
  """

  def all_subsets(set_):
    list_ = list(set_)
    for size in range(0, len(list_)+1):
      for subset in combinations(list_, size):
        yield subset

  ret = []
  if isinstance(rule, basestring):
    rule = _parse(rule)

  conditionals = rule.collect_conditionals()
  for subset in all_subsets(conditionals):
    # ensure that only terms in the subset are enabled
    if format:
      ret.append(rule.select(subset).format())
    else:
      ret.append(rule.select(subset))

  return sorted(set(ret))

def create_wrapper(rule, fn):
  """
    Takes a rule (either a Rule object or a string, see `expand_conditionals`) and
    a function and returns the given function wrapped with a decorator that provides:

      + Named parameters extraction from the `p` parameter.
      + PLY-compatible docstring (computed from the passed rule).
  """

  if isinstance(rule, basestring):
    rule = _parse(rule)

  # flattening - we need to iterate over rule terms
  rule = rule.select()

  def wrapper(p):
    kwargs = {}
    # named parameters extraction
    for i, term in enumerate(rule.terms):
      if isinstance(term, NamedTerm):
        kwargs[term.name] = p[i+1]
    p[0] = fn(**kwargs)
  
  wrapper.__doc__ = rule.format()

  return wrapper

def format(rules):
  if isinstance(rules, basestring):
    rules = parse(rules)

  return '\n'.join(rule.format() for rule in rules)

def parse(defn, fname = None):
  "Takes a docstring and returns a list of Rules contained in it."

  if not defn:
    if fname is not None:
      raise NoDocstringError("Function %s has no docstring" % fname)
    else:
      raise NoDocstringError("Provided function has no docstring")

  defn = [line.strip() for line in defn.split('\n') if line.strip()]
  return [_parse(line) for line in defn]

def process_function(fn):
  """
    Takes a function with easyply defintion stored in the docstring and
    returns a dictionary of corresponding PLY-compatible functions.
  """
  
  rules = parse(fn.__doc__, fname = fn.__name__)
  expanded = sum((expand_conditionals(rule, format = False) for rule in rules), [])

  ret = {}
  i = 0
  for rule in expanded:
    ret['p_%s_%s' % (fn.__name__, i)] = create_wrapper(rule, fn)
    i += 1
  return ret

def process_all(globals, prefix = 'px_'):
  """
    Applies `process_function` to each function which name starts with `prefix`
    (`px_` by default). `process_all` accepts either a dictionary or a class and
    updates it with new functions.
  """
   
  dict = globals.__dict__ if isinstance(globals, type) else globals
  names = [name for name in dict if name.startswith(prefix) and callable(dict[name])]
  funs = [dict[name] for name in names]
  for name in names:
    if isinstance(globals, type):
      delattr(globals, name)
    else:
      del globals[name]

  for fn in funs:
    for name, wrapper in process_function(fn).items():
      if isinstance(globals, type):
        setattr(globals, name, wrapper)
      else:
        globals[name] = wrapper
