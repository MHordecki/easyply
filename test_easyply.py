
from easyply import expand_conditionals, create_wrapper, process_function, process_all

def assert_eq(a, b):
  assert a == b, "%r != %r" % (a, b)

def test_expand():
  assert_eq(set(expand_conditionals('r: g1 g2')), set(('r : g1 g2', )))
  assert_eq(set(expand_conditionals('r: g1 g2?')), set(('r : g1', 'r : g1 g2')))
  assert_eq(set(expand_conditionals('r: {g1:name}? g2')), set(('r : g2', 'r : g1 g2')))
  assert_eq(set(expand_conditionals('r: g1? g2?')), set(('r :', 'r : g1', 'r : g1 g2', 'r : g2')))

def test_expand_parens():
  assert_eq(set(expand_conditionals('r : w1 (w2 w3)?')), set(('r : w1', 'r : w1 w2 w3')))

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
  def p_fn1(): "r: g1 g2?"
  def skip_me(): "r: g1 g2?"

  globals_ = {'p_fn1': p_fn1, 'skip_me': skip_me}
  process_all(globals_)
  assert_eq(len(globals_), 3)
  assert 'skip_me' in globals_
  assert globals_['skip_me'] is skip_me
  assert 'p_fn1_0' in globals_
  assert 'p_fn1_1' in globals_

import nose
nose.main()
