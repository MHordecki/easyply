"""

Implementation & usage notes:

Each rule, such as `production: SYM another (SYM another)?` is parsed
into a Rule object. It provides means of enumeration of possible expansions
of optional parameters and so on. The class itself and the parser are defined
in `nodes` and `parser`, respectively.

easyply is rather forgiving when it comes to input parameters and
employs implicit conversions where possible. In general, functions
accept either:

  + rulesets, which can be one of the following:
    + Rule object, passed as-is
    + list of Rule objects, passed as-is
    + string, parsed by `parser.parse` into a list of Rule objects
    + list of strings, each parsed by `parser.parse`
  + rule, which is a simply a ruleset containing one Rule object. It's
    coerced in the same way as the ruleset case and then checked
    for length. In case of length different than 1, `SingleRuleExpectedError`
    is raised.
"""

from parser import parse as _parse
from itertools import combinations, chain
from functools import wraps
from nodes import NamedTerm
from types import MethodType

class NoDocstringError(Exception):
    pass

class SingleRuleExpectedError(Exception):
  pass

def _coerce_to_ruleset(ruleset):
  def coerce_to_rule(rule):
    if isinstance(rule, basestring):
      return _parse(rule)
    else:
      return (rule, )

  if not isinstance(ruleset, (list, tuple)):
    ruleset = (ruleset, )

  return list(chain.from_iterable(coerce_to_rule(rule) for rule in ruleset))

def _coerce_to_single_rule(rule):
  ruleset = _coerce_to_ruleset(rule)
  if len(ruleset) != 1:
    raise SingleRuleExpectedError(rule)

  return ruleset[0]

def expand_optionals(ruleset, format = True, pure_ply = True):
  """
    Takes a ruleset (see Implementation Notes) and returns a list of all
    possible optional term resolutions.
    The optional parameter `format` controls the output. If it's true,
    `expand_optionals` will output a list of strings. Otherwise a list of
    flattened Rule objects is returned.
  """

  def process_rule(rule):
    rules = rule.expand_optionals()
    if format:
      return list(set(rule.flatten().format(pure_ply) for rule in rules))
    else:
      return list(set(rule.flatten() for rule in rules))

  ruleset = _coerce_to_ruleset(ruleset)
  return list(chain.from_iterable(process_rule(rule) for rule in ruleset))


def create_wrapper(rule, fn):
  """
    Takes a rule (either a Rule object or a string, see `expand_optionals`) and
    a function and returns the given function wrapped with a decorator that provides:

      + Named parameters extraction from the `p` parameter.
      + PLY-compatible docstring (computed from the passed rule).
  """

  rule = _coerce_to_single_rule(rule)

  # flattening - we need to iterate over rule terms
  rule = rule.flatten()

  @wraps(fn)
  def wrapper(p):
    kwargs = {}
    # named parameters extraction
    for i, term in enumerate(rule.terms):
      if isinstance(term, NamedTerm):
        kwargs[term.name] = p[i+1]
    p[0] = fn(**kwargs)

  wrapper.__doc__ = rule.format(pure_ply = True)

  return wrapper

def parse(defn, fname = None):
  "Takes a docstring and returns a parsed ruleset."

  if not defn:
    if fname is not None:
      raise NoDocstringError("Function %s has no docstring" % fname)
    else:
      raise NoDocstringError("Provided function has no docstring")

  return _parse(defn.strip())
  defn = [line.strip() for line in defn.split('\n') if line.strip()]
  return list(chain.from_iterable(_parse(line) for line in defn))

def process_function(fn):
  """
    Takes a function with easyply defintion stored in the docstring and
    returns a dictionary of corresponding PLY-compatible functions.
  """

  ruleset = parse(fn.__doc__, fname = fn.__name__)
  expanded = expand_optionals(ruleset, format = False)

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

  if isinstance(globals, dict):
    names = [name for name in globals
             if name.startswith(prefix) and callable(globals[name])]
    for name in names:
      fn = globals[name]
      for name, wrapper in process_function(fn).items():
        globals[name] = wrapper
  else:
    # is an object
    names = [name for name in dir(globals)
             if name.startswith(prefix) and callable(getattr(globals, name))]
    for name in names:
      fn = getattr(globals, name)
      for name, wrapper in process_function(fn).items():
        setattr(globals, name, wrapper)


