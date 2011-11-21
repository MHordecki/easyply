
from __future__ import print_function

from ply.lex import lex
from ply.yacc import yacc

from nodes import Rule, Term, ConditionalTerm, NamedTerm, Terms


t_ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_COLON = r':'

t_PAREN_BEGIN = r'\('
t_PAREN_END = r'\)'
t_CURLY_BEGIN = r'{'
t_CURLY_END = r'}'
t_QUESTION = r'\?'

def t_COMMENT(t):
  r'\#.*'
  return None

def t_error(a):
  assert False

t_ignore = ' \t'

tokens = []
name = None
tokens = [name[2:] for name in globals() if name.startswith('t_')]
tokens.remove('ignore')
tokens.remove('error')

def p_rule(p):
  "rule : rule_header terms"
  p[0] = Rule(p[1], p[2])

def p_rule_header(p):
  "rule_header : ID COLON"
  p[0] = p[1]
  
def p_terms(p):
  "terms : term"
  p[0] = Terms([p[1]])

def p_terms_append(p):
  "terms : terms term"
  p[0] = p[1]
  p[0].append(p[2])

def p_term(p):
  """
  term : conditional_term
  term : named_term
  """
  p[0] = p[1]

def p_term_literal(p):
  "term : ID"
  p[0] = Term(p[1])
  
def p_term_parens(p):
  "term : PAREN_BEGIN terms PAREN_END"
  p[0] = p[2]

def p_conditional_term(p):
  "conditional_term : term QUESTION"
  p[0] = ConditionalTerm(p[1])

def p_named_term(p):
  "named_term : CURLY_BEGIN ID COLON ID CURLY_END"
  p[0] = NamedTerm(p[2], p[4])

def p_named_term_default(p):
  "named_term : CURLY_BEGIN ID CURLY_END"
  p[0] = NamedTerm(p[2], p[2].lower())

def p_error(p):
  assert False, p

lexer = lex()
parser = yacc(picklefile = 'easyply.tab') #FIXME: rename parsetab

def parse(text):
  return parser.parse(text)

