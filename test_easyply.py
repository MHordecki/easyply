
from easyply import expand_conditionals, create_wrapper, process_function, process_all, parse, format

def assert_eq(a, b):
  assert a == b, "%r != %r" % (a, b)

def assert_eq_list(a, b):
  a = sorted(a)
  b = sorted(b)
  if not isinstance(a[0], basestring) and 0:
    for i, (ai, bi) in enumerate(zip(a, b)):
      print i, ai, bi, ai == bi
    print a[0].terms.terms[0] == b[0].terms.terms[0]
    print a[0].terms.terms
    print b[0].terms.terms
    print a[0].terms.terms == b[0].terms.terms
    print [str(x) for x in a], [str(x) for x in b]
  assert_eq(a, b)

def assert_expand(rule, result):
  assert_eq_list(expand_conditionals(rule), result)
  assert_eq_list(expand_conditionals(rule, format = False), parse('\n'.join(result)))

def test_printing():
  rule = parse('r: w1 (w1 {w2:name})?')[0]
  assert_eq(str(rule), 'r: w1 (w1 {w2:name})?')
  assert_eq(rule.format(), 'r : w1 w1 w2')
  
def test_expand():
  assert_eq_list(expand_conditionals('r: g1 g2'), ('r : g1 g2', ))
  assert_eq_list(expand_conditionals('r: g1 g2?'), ('r : g1', 'r : g1 g2'))
  assert_eq_list(expand_conditionals('r: {g1:name}? g2'), ('r : g2', 'r : g1 g2'))
  assert_eq_list(expand_conditionals('r: g1? g2?'), ('r :', 'r : g1', 'r : g1 g2', 'r : g2'))
  assert_expand('r: s? r s?', ('r : r', 'r : s r', 'r : r s', 'r : s r s'))

def test_expand_parens():
  assert_expand('r : w1 (w2 w3)?', ('r : w1', 'r : w1 w2 w3'))

def test_expand_nested():
  assert_expand('r: w1 (n1 n2? n3)?',
      ('r : w1', 'r : w1 n1 n2 n3', 'r : w1 n1 n3'))
  assert_expand('r: w1 (r1 o1? r2 o2?)? w2',
      ('r : w1 w2', 'r : w1 r1 r2 w2', 'r : w1 r1 o1 r2 w2', 'r : w1 r1 r2 o2 w2',
        'r : w1 r1 o1 r2 o2 w2'))

def test_wrapping():
  called = [False]
  def fn1(arg1):
    "r : {g1:arg1} g2"
    assert_eq(arg1, 'hello!')
    called[0] = True
  
  wrapper = create_wrapper(fn1.__doc__, fn1)
  wrapper([None, 'hello!'])
  assert_eq(wrapper.__doc__, 'r : g1 g2')
  assert called[0]

def test_wrapping_in_group():
  called = [False]
  def fn1(arg):
    "r : w1 ({g1:arg} g2)"
    assert_eq(arg, 'hello!')
    called[0] = True
  
  wrapper = create_wrapper(fn1.__doc__, fn1)
  wrapper([None, 'foo', 'hello!', 'bar'])
  assert_eq(wrapper.__doc__, 'r : w1 g1 g2')
  assert called[0]

def test_process_function():
  def fn1():
    "r : g1 g2?"
  
  functions = process_function(fn1)
  assert_eq(len(functions), 2)

def test_process_function_many_rules():
  def fn2():
    """
    r : g1 g2?
    r : g3
    """
  
  functions = process_function(fn2)
  assert_eq(len(functions), 3)

def test_process_all():
  def px_fn1(): "r: g1 g2?"
  def p_skip_me(): "r: g1 g2?"
  def skip_me(): "r: g1 g2?"

  globals_ = {'px_fn1': px_fn1, 'p_skip_me': p_skip_me, 'skip_me': skip_me}
  process_all(globals_)
  assert_eq(len(globals_), 4)
  assert 'skip_me' in globals_
  assert 'p_skip_me' in globals_
  assert globals_['skip_me'] is skip_me
  assert globals_['p_skip_me'] is p_skip_me
  assert 'p_px_fn1_0' in globals_
  assert 'p_px_fn1_1' in globals_

import nose
nose.main()
