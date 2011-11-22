
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
    #print ComparisonMixin.__get_cmpkey(self) ,'==', ComparisonMixin.__get_cmpkey(other)
    return ComparisonMixin.__get_cmpkey(self) == ComparisonMixin.__get_cmpkey(other)

class Rule(ComparisonMixin):
  def __init__(self, name, terms):
    self.name = name
    self.terms = terms

  def __str__(self):
    return '%s: %s' % (self.name, self.terms)

  def format(self):
    return ' '.join((self.name, ':') + self.terms.format())

  def collect_conditionals(self):
    return self.terms.collect_conditionals()

  def select(self, enabled_conditionals):
    return Rule(self.name, Terms(self.terms.select(enabled_conditionals)))

  def _cmpkey(self):
    return (type(self), self.name, self.terms)

class Terms(ComparisonMixin):
  def __init__(self, terms):
    self.terms = tuple(terms)

  def append(self, term):
    self.terms += (term, )

  def __iter__(self):
    return iter(self.terms)

  def __str__(self):
    return ' '.join(str(term) for term in self.terms)

  def format(self):
    return sum((term.format() for term in self.terms), ())

  def collect_conditionals(self):
    return sum((term.collect_conditionals() for term in self.terms), ())

  def select(self, enabled_conditionals):
    return sum((term.select(enabled_conditionals) for term in self.terms), ())

  def _cmpkey(self):
    return (type(self), self.terms)

class ConditionalTerm(ComparisonMixin):
  def __init__(self, term):
    self.term = term

  def __str__(self):
    if isinstance(self.term, Terms):
      return '(%s)?' % self.term
    else:
      return str(self.term) + '?'

  def format(self):
    return self.term.format()

  def collect_conditionals(self):
    return (self, ) + self.term.collect_conditionals()

  def select(self, enabled_conditionals):
    if any(x is self for x in enabled_conditionals):
      return self.term.select(enabled_conditionals)
    else:
      return ()

  def _cmpkey(self):
    return (type(self), self.term)

class NamedTerm(ComparisonMixin):
  def __init__(self, parser_term, name):
    self.parser_term = parser_term
    self.name = name
  
  def __str__(self):
    return '{%s:%s}' % (self.parser_term, self.name)

  def format(self): return (self.parser_term, )
  def collect_conditionals(self): return ()
  def select(self, enabled_conditionals): return (self, )

  def _cmpkey(self):
    return (type(self), self.parser_term, self.name)

class Term(ComparisonMixin):
  def __init__(self, parser_term):
    self.parser_term = parser_term

  def format(self): return (self.parser_term, )
  def collect_conditionals(self): return ()
  def select(self, enabled_conditionals): return (self, )

  def __str__(self):
    return self.parser_term

  def _cmpkey(self):
    return (type(self), self.parser_term)

