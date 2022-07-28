from Error import *
import string
TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EOF		= 'EOF'
DIGITS      = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
TT_KEYWORD = 'KEYWORD',
TT_IDENTIFIER = 'IDENTIFIER',
TT_EQ = 'EQ'
TT_EE = 'EE'

KEYWORDS = [
	'IF',
	'THEN',
	'ELSEIF',
	'ELSE',
	'FOR',
	'TO',
	'STEP',
	'WHILE'
]

class Token:
	def __init__(self, token_type, val=None):
		self.token_type = token_type
		self.val = val
	
	def __repr__(self):
		if self.val: 
			return f'{self.token_type}:{self.val}'
		elif not self.val:
			return self.token_type
	
	def token_match(self, token_type, value):
		return self.token_type == token_type and self.val == value

class Lexer:
	def __init__(self, filename, input_txt):
		self.position = -1
		self.filename = filename
		self.input_txt = input_txt
		self.char_pos = None
		self.advance()
	
	def advance(self):
		self.position+=1
		if self.position < len(self.input_txt):
			self.char_pos = self.input_txt[self.position] 
		else:
			self.char_pos=None
   

	def tokens(self):
		tokens_res = []

		while self.char_pos != None:
			if self.char_pos in ' \t':
				self.advance()
			elif self.char_pos == '=':
					tokens_res.append(self.make_equals())
			elif self.char_pos in DIGITS:
				tokens_res.append(self.num())
			elif self.char_pos in LETTERS:
				tokens_res.append(self.make_identifier())
			elif self.char_pos == '+':
				tokens_res.append(Token(TT_PLUS))
				self.advance()
			elif self.char_pos == '-':
				tokens_res.append(Token(TT_MINUS))
				self.advance()
			elif self.char_pos == '*':
				tokens_res.append(Token(TT_MUL))
				self.advance()
			elif self.char_pos == '/':
				tokens_res.append(Token(TT_DIV))
				self.advance()
			elif self.char_pos == '(':
				tokens_res.append(Token(TT_LPAREN))
				self.advance()
			elif self.char_pos == ')':
				tokens_res.append(Token(TT_RPAREN))
				self.advance()
			else:
				chr = self.char_pos
				self.advance()
				return [], IllegalCharError("'" + chr + "'")

		tokens_res.append(Token(TT_EOF))
		return tokens_res, None

	def num(self):
		res_str = ''
		count = 0

		while self.char_pos != None and self.char_pos in DIGITS + '.':
			if self.char_pos == '.':
				if count == 1: 
					break
				else:
					count += 1
					res_str += '.'
			else:
				res_str += self.char_pos
			self.advance()

		if count == 0:
			return Token(TT_INT, int(res_str))
		else:
			return Token(TT_FLOAT, float(res_str))

	def make_identifier(self):
		id_str = ''
		pos_start = self.position
		while self.char_pos != None and self.char_pos in LETTERS_DIGITS + '_':
				id_str += self.char_pos
				self.advance()

		tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
		return Token(tok_type, id_str)

	def make_equals(self):
		tok_type = TT_EQ
		pos_start = self.position
		self.advance()

		if self.char_pos == '=':
			self.advance()
			tok_type = TT_EE

		return Token(tok_type)

# class Position:
#     def __init__(self, idx, ln, col, fn, ftxt):
#         self.idx = idx
#         self.ln = ln
#         self.col = col
#         self.fn = fn
#         self.ftxt = ftxt
#     def advance(self, current_char=None):
#         self.idx += 1
#         self.col += 1
#         if current_char == '\n':
#             self.ln += 1
#             self.col = 0
#         return self
#     def copy(self):
#         return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)