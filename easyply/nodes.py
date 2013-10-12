
from itertools import product, chain

class ComparisonMixin(object):
  @staticmethod
  def __get_cmpkey(obj):
    if not hasattr(obj, '_cmpkey'):
      raise NotImplementedError
    return obj._cmpkey()

  def __lt__(self, other):
    return ComparisonMixin.__get_cmpkey(self) < ComparisonMixin.__get_cmpkey(other)

  def __hash__(self):
    return hash(ComparisonMixin.__get_cmpkey(self))

  def __eq__(self, other):
    return ComparisonMixin.__get_cmpkey(self) == ComparisonMixin.__get_cmpkey(other)

class Node(object):
  "Common interface for AST nodes."

  def format(self, pure_ply = True):
    """
      Returns a textual representation of the node. When `pure_ply` is set,
      the returned string is a valid PLY rule. Otherwise, the resulting string
      may contain easyply syntax.
    """
    raise NotImplementedError

  def expand_optionals(self):
    """
      Returns an iterable of copies of the node with all possible optional
      term resolutions inside.
    """

class Rule(ComparisonMixin):
  def __init__(self, name, terms):
    self.name = name
    self.terms = terms

  def format(self, pure_ply = True):
    return ('%s : %s' % (self.name, self.terms.format(pure_ply))).strip()

  def expand_optionals(self):
    for case in self.terms.expand_optionals():
      yield Rule(self.name, case)

  def flatten(self):
    """
      Returns a copy of the rule with all child nodes flattened, ie.
      no nested nodes such as Terms, OrTerm, etc.
    """
    return Rule(self.name, Terms(self.terms.flatten()))

  def _cmpkey(self):
    return (type(self), self.name, self.terms)

class Terms(ComparisonMixin):
  def __init__(self, terms):
    self.terms = tuple(terms)
    assert all(not isinstance(x, tuple) for x in self.terms)

  def append(self, term):
    self.terms += (term, )

  def __iter__(self):
    return iter(self.terms)

  def format(self, pure_ply = True):
    return ' '.join(term.format(pure_ply) for term in self.terms)

  def expand_optionals(self):
    terms = [term.expand_optionals() for term in self.terms]
    for case in product(*terms):
      yield Terms(x for x in case if x) # removing Nones from OptionalTerm

  def flatten(self):
    return tuple(chain.from_iterable(term.flatten() for term in self.terms))

  def _cmpkey(self):
    return (type(self), self.terms)

class OptionalTerm(ComparisonMixin):
  def __init__(self, term):
    self.term = term

  def format(self, pure_ply = True):
    if pure_ply:
      return self.term.format(pure_ply)

    if isinstance(self.term, Terms):
      return '(%s)?' % self.term.format(pure_ply)
    else:
      return str(self.term.format(pure_ply)) + '?'

  def flatten(self): return self.term.flatten()

  def expand_optionals(self):
    return chain((None, ), self.term.expand_optionals())

  def _cmpkey(self):
    return (type(self), self.term)

class OrTerm(ComparisonMixin):
  def __init__(self, cases):
    self.cases = tuple(cases)

  def expand_optionals(self):
    return sum((tuple(case.expand_optionals()) for case in self.cases), ())

  def format(self, pure_ply = True):
    assert not pure_ply

    return ' | '.join(case.format(pure_ply) for case in self.cases)

class NamedTerm(ComparisonMixin):
  def __init__(self, parser_term, name):
    self.parser_term = parser_term
    self.name = name

  def format(self, pure_ply = True):
    if pure_ply:
      return self.parser_term

    return '{%s:%s}' % (self.parser_term, self.name)

  def expand_optionals(self): return (self, )
  def flatten(self): return (self, )

  def _cmpkey(self):
    return (type(self), self.parser_term, self.name)

class Term(ComparisonMixin):
  def __init__(self, parser_term):
    self.parser_term = parser_term

  def format(self, pure_ply = True): return self.parser_term
  def expand_optionals(self): return (self, )
  def flatten(self): return (self, )

  def _cmpkey(self):
    return (type(self), self.parser_term)

