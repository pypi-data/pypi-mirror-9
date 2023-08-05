# Copyright (c) 2015, Sven Thiele <sthiele78@gmail.com>
#
# This file is part of modulefinder.
#
# modulefinder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# modulefinder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with modulefinder.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

from pyasp.misc import *
class Lexer:
	tokens = (
		'IDENT',
		'PLUS',
		'MINUS',
	)

	# Tokens

	t_IDENT = r'[a-zA-Z][a-zA-Z0-9_:\-\[\]/]*'

	t_PLUS = r'1'
	t_MINUS = r'-1'


	def __init__(self):
		import pyasp.ply.lex as lex
		self.lexer = lex.lex(object = self, optimize=1, lextab='sif_parser_lextab')

	# Ignored characters
	t_ignore = " \t"

	def t_newline(self, t):
		r'\n+'
		t.lexer.lineno += t.value.count("\n")
		
	def t_error(self, t):
		print "Illegal character '%s'" % t.value[0]
		t.lexer.skip(1)


class Parser:
	tokens = Lexer.tokens

	precedence = ( )

	def __init__(self):
		self.aux_node_counter=0
		self.accu = {}
		self.args = []
		self.lexer = Lexer()
		import pyasp.ply.yacc as yacc
		self.parser = yacc.yacc(module=self,optimize=1)

	def p_statement_expr(self, t):
		'''statement : node_expression PLUS node_expression 
		| node_expression MINUS node_expression'''
		#print 'edge',t[1], t[2], t[3]
		if (self.accu.has_key(t[3])):
                  (pos,neg) = self.accu[t[3]]
                  if t[2]=='1':
		    pos.append(t[1])
                  if t[2]=='-1':
                    neg.append(t[1])
                  #print self.accu[t[1]]
		else :
		  if t[2]=='1':
		    self.accu[t[3]]=([t[1]],[])
		  if t[2]=='-1':  
		  #print 'add',t[1],[t[3]]
		    self.accu[t[3]]=([],[t[1]])


	def p_node_expression(self, t):
		'''node_expression : IDENT'''
		if len(t)<3 : 
				t[0]=t[1]
				#print "single node ", t[1]
		else : t[0] = "unknown"

			
	def p_error(self, t):
		print "Syntax error at '%s'" % t

	def parse(self, line):
		self.parser.parse(line, lexer=self.lexer.lexer)
		return self.accu
