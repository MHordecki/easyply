
import easyply
import ply.lex as lex
import ply.yacc as yacc



class Lexer(object):
  tokens = ('A', )

  t_A = r'\w+'

  lexer = lex.lex()


class Parser(Lexer):
  def px_test(self, a):
    '''production: {A}'''
    global _parser
    assert self is _parser
    return a

  def parse(self, text):
    easyply.process_all(self)
    self.parser = yacc.yacc(module=self)
    return self.parser.parse(text)

def test_issue2():
  global _parser
  _parser = Parser()
  assert _parser.parse('Hello') == 'Hello'

