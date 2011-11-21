
class Rule(object):
  def __init__(self, name, terms):
    self.name = name
    self.terms = terms

  def format(self):
    return ('%s : ' % (self.name) + ' '.join(self.terms.render())).strip()

  def collect_conditionals(self):
    return self.terms.collect_conditionals()

  def select(self, enabled_conditionals):
    return Rule(self.name, Terms(self.terms.select(enabled_conditionals)))

class Terms(object):
  def __init__(self, terms):
    self.terms = terms

  def append(self, term):
    self.terms.append(term)

  def __iter__(self):
    return iter(self.terms)

  def render(self):
    return sum((term.render() for term in self.terms), ())

  def collect_conditionals(self):
    return sum((term.collect_conditionals() for term in self.terms), ())

  def select(self, enabled_conditionals):
    return sum((term.select(enabled_conditionals) for term in self.terms), ())

class ConditionalTerm(object):
  def __init__(self, term):
    self.term = term
    self.enabled = False

  def enable(self): self.enabled = True
  def disable(self): self.enabled = False

  def render(self):
    if self.enabled:
      return self.term.render()
    else:
      return ()

  def collect_conditionals(self): return (self, )
  def select(self, enabled_conditionals):
    if self in enabled_conditionals:
      return self.term.select(enabled_conditionals)
    else:
      return ()

class NamedTerm(object):
  def __init__(self, parser_term, name):
    self.parser_term = parser_term
    self.name = name
  def render(self): return (self.parser_term, )

  def collect_conditionals(self): return ()
  def select(self, enabled_conditionals): return (self, )

class Term(object):
  def __init__(self, parser_term):
    self.parser_term = parser_term

  def collect_conditionals(self): return ()
  def render(self): return (self.parser_term, )
  def select(self, enabled_conditionals): return (self, )

