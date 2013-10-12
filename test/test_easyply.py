
from easyply import expand_optionals, create_wrapper, process_function, process_all, parse, NoDocstringError

def assert_eq_list(a, b):
  a = sorted(a)
  b = sorted(b)
  assert a == b

def assert_expand(rule, result):
  assert_eq_list(expand_optionals(rule), result)
  assert_eq_list(expand_optionals(rule, format = False), parse('\n'.join(result)))

def test_printing():
  rule = parse('r: w1 (w1 {w2:name})?')[0]
  assert rule.format(pure_ply = False)  == 'r : w1 (w1 {w2:name})?'
  assert rule.format(pure_ply = True) == 'r : w1 w1 w2'
  assert rule.format() == 'r : w1 w1 w2'

def test_expand():
  assert_eq_list(expand_optionals('r: g1 g2'), ('r : g1 g2', ))
  assert_eq_list(expand_optionals('r: g1 g2?'), ('r : g1', 'r : g1 g2'))
  assert_eq_list(expand_optionals('r: {g1:name}? g2'), ('r : g2', 'r : g1 g2'))
  assert_eq_list(expand_optionals('r: g1? g2?'), ('r :', 'r : g1', 'r : g1 g2', 'r : g2'))
  assert_expand('r: s? r s?', ('r : r', 'r : s r', 'r : r s', 'r : s r s'))

def test_expand_parens():
  assert_expand('r : w1 (w2 w3)?', ('r : w1', 'r : w1 w2 w3'))

def test_expand_nested():
  assert_expand('r: w1 (n1 n2? n3)?',
      ('r : w1', 'r : w1 n1 n2 n3', 'r : w1 n1 n3'))
  assert_expand('r: w1 (r1 o1? r2 o2?)? w2',
      ('r : w1 w2', 'r : w1 r1 r2 w2', 'r : w1 r1 o1 r2 w2', 'r : w1 r1 r2 o2 w2',
        'r : w1 r1 o1 r2 o2 w2'))

def test_expand_or():
  assert_expand('r: w1 | w2',
      ('r : w1', 'r : w2'))
  assert_expand('r: w1 (w2 | w3) w4 | w5 w6',
      ('r : w1 w2 w4', 'r : w1 w3 w4', 'r : w5 w6'))
  assert_expand('r: w1 w2 | w3 | w4 w5 | w6',
      ('r : w1 w2', 'r : w3', 'r : w4 w5', 'r : w6'))

def test_wrapping():
  called = [False]
  def fn1(arg1):
    "r : {g1:arg1} g2"
    assert arg1 == 'hello!'
    called[0] = True

  wrapper = create_wrapper(fn1.__doc__, fn1)
  wrapper([None, 'hello!'])
  assert wrapper.__doc__ == 'r : g1 g2'
  assert called[0]

def test_wrapping_in_group():
  called = [False]
  def fn1(arg):
    "r : w1 ({g1:arg} g2)"
    assert arg == 'hello!'
    called[0] = True

  wrapper = create_wrapper(fn1.__doc__, fn1)
  wrapper([None, 'foo', 'hello!', 'bar'])
  assert wrapper.__doc__ == 'r : w1 g1 g2'
  assert called[0]

def test_process_function():
  def fn1():
    "r : g1 g2?"

  functions = process_function(fn1)
  assert len(functions) == 2

def test_process_function_many_rules():
  def fn2():
    """
    r : g1 g2?
    r : g3
    """

  functions = process_function(fn2)
  assert len(functions) == 3

def test_process_all():
  def px_fn1(): "r: g1 g2?"
  def p_skip_me(): "r: g1 g2?"
  def skip_me(): "r: g1 g2?"

  globals_ = {'px_fn1': px_fn1, 'p_skip_me': p_skip_me, 'skip_me': skip_me}
  process_all(globals_)
  assert len(globals_) == 5
  assert 'px_fn1' in globals_
  assert 'skip_me' in globals_
  assert 'p_skip_me' in globals_
  assert globals_['skip_me'] is skip_me
  assert globals_['p_skip_me'] is p_skip_me
  assert 'p_px_fn1_0' in globals_
  assert 'p_px_fn1_1' in globals_

def test_process_all_with_class():
  class MyClass(object):
    def px_fn1(self): "r: g1 g2?"
    def p_skip_me(self): "r: g1 g2?"
    def skip_me(self): "r: g1 g2?"
    px_skip_me = "r: g1 g2?"

  old_skip_me = MyClass.skip_me
  old_p_skip_me = MyClass.p_skip_me
  old_px_skip_me = MyClass.px_skip_me

  process_all(MyClass)

  assert hasattr(MyClass, 'skip_me')
  assert hasattr(MyClass, 'p_skip_me')
  assert MyClass.skip_me == old_skip_me
  assert MyClass.p_skip_me == old_p_skip_me
  assert MyClass.px_skip_me == old_px_skip_me
  assert hasattr(MyClass, 'p_px_fn1_0')
  assert hasattr(MyClass, 'p_px_fn1_1')

def test_exception_when_no_docstring():
  def px_fn():
    pass
  globals_ = { 'px_fn': px_fn }
  exception_raised = False
  try:
    process_all(globals_)
  except NoDocstringError:
    exception_raised = True
  assert exception_raised

def test_exception_when_empty_docstring():
  def px_fn():
    ""
    pass
  globals_ = { 'px_fn': px_fn }
  exception_raised = False
  try:
    process_all(globals_)
  except NoDocstringError:
    exception_raised = True
  assert exception_raised

def test_two_rules():
  rule = """ r1: SYM1 SYM2
  r2: SYM2 SYM3"""

  parsed = parse(rule)

  assert len(parsed) == 2
  assert parsed[0].format() == 'r1 : SYM1 SYM2'
  assert parsed[1].format() == 'r2 : SYM2 SYM3'

def test_multiline_rule():
  rule = """ production: SYM1 SYM2
  SYM3 SYM4
  """

  parsed = parse(rule)

  assert len(parsed) == 1
  assert parsed[0].format() == 'production : SYM1 SYM2 SYM3 SYM4'

def test_multiline_rule_with_another_rule():
  rule = """ production: SYM1 SYM2
  SYM3 SYM4
  production2: S1 S2
  """

  parsed = parse(rule)

  assert len(parsed) == 2
  assert parsed[0].format() == 'production : SYM1 SYM2 SYM3 SYM4'
  assert parsed[1].format() == 'production2 : S1 S2'

"""
In the future, maybe...
def test_multiline_rule_crazy_cornercase():
  rule = " "" production: SYM1 SYM2 {
             foo:        bar} SYM3
             production2: S1 S2
  "" "

  parsed = parse(rule)

  assert len(parsed) == 2
  assert parsed[0].format() == 'production : SYM1 SYM2 foo SYM4'
  assert parsed[1].format() == 'production2 : S1 S2'
"""

def test_multirule():
  rule = """production: SYM1 SYM2
                  | SYM2 SYM2 SYM2"""

  parsed = parse(rule)

  assert len(parsed) == 1
  assert parsed[0].format(pure_ply = False) == 'production : SYM1 SYM2 | SYM2 SYM2 SYM2'

