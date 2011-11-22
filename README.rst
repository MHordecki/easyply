=======
easyply
=======

Introduction
============

easyply is a helper library for PLY, parser generator for Python. It
acts as a middleware between your grammar definition and PLY.

What's so appealing about easyply? PLY supports rather crude parser
definitions; easyply adds some EBNF-y flavor to it. easyply is purely
a helper in everyday work - you definitely need to understand PLY first 
in order to use this library.

Goodies
=======

Currently, there are three nice additions to the normal PLY syntax:

No mandratory whitespace surrounding colon sign
-----------------------------------------------

::

  def px_rule():
    "production: SYMBOL

Named parameters
----------------

Instead of mutating and reading the mysterious ``p`` parameter,
easyply employs named parameters and return values. So::

  def px_rule(id):
    "production: {ID}
    ...
    return retval

is equivalent to::

  def p_rule(p):
    "production : ID"
    id = p[1]
    ...
    p[0] = retval

You can also use custom names for parameters, just like this::

  def px_rule(foo):
    "production: {ID:foo}"

Optional symbols
----------------

Instead of creating multiple similar rules differing only by a few symbols,
you can consolidate them into one using ``?`` symbol. Observe::

  def px_rule():
    "production: symbol1 symbol2? symbol3"
    ...

Given this code, easyply will generate two functions with the
same code and the following rules:

  + ``production: symbol1 symbol3``
  + ``production: symbol1 symbol2 symbol3``

This is especially powerful in conjunction with named parameters(note the parentheses)::

  def px_list(expression, list = ()):
    "list: ({list} COMMA)? {expression}"
    return list + expression

Neat, isn't it?

Installation
============

::
  
  pip install easyply  

Usage
=====

Basic usage is simple: Prefix all your easyply rules with ``px_`` prefix
(instead of the usual ``p_``) and call ``easyply.process_all(globals())``
before creating your PLY parser. If your want more fine grained control,
consult the API reference.

License
=======

This library is licensed under the MIT License.

Copyright © 2011 by Mike Hordecki

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


