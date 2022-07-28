from error import * 
DIGITS = '0123456789'
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTERS_DIGITS = LETTERS + "0123456789"
KEYWORDS = ['VAR','AND','OR','NOT','IF','ELIF','ELSE','FOR','TO','STEP','WHILE','THEN']

TokType_STR         = 'STR'
TokType_INT			= 'INT'
TokTypeFLOAT    	= 'FLOAT'
TokTypeIDENTIFIER	= 'IDENTIFIER'
TokTypeKEYWORD		= 'KEYWORD'
TokTypePLUS     	= 'PLUS'
TokTypeMINUS    	= 'MINUS'
TokTypeMUL      	= 'MUL'
TokTypeDIV      	= 'DIV'
TokTypePOW			= 'POW'
TokTypeEQ			= 'EQ'
TokTypeLPAREN   	= 'LPAREN'
TokTypeRPAREN   	= 'RPAREN'
TokTypeEE			= 'EE'
TokTypeNE			= 'NE'
TokTypeLT			= 'LT'
TokTypeGT			= 'GT'
TokTypeLTE			= 'LTE'
TokTypeGTE			= 'GTE'
TokTypeEOF			= 'EOF'

class Token:
	def __init__(self, type_, value=None, position_start=None, position_end=None):
		self.type = type_
		self.value = value

		if position_start:
			self.position_start = position_start.copy()
			self.position_end = position_start.copy()
			self.position_end.advance()

		if position_end:
			self.position_end = position_end.copy()

	def token_match(self, type_, value):
		if self.type == type_ and self.value == value:
			return True
		else:
			return False
	
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'



class Position:
	def __init__(self, idx, ftxt):
		self.idx = idx
		self.ftxt = ftxt

	def advance(self,):
		self.idx += 1
		return self

	def copy(self):
		return Position(self.idx, self.ftxt)






class Lexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.curr_char = None
		self.text,self.pos  = text, Position(-1, text)
		self.advance()
	
	def advance(self):
		self.pos.advance()
		if self.pos.idx < len(self.text):
			self.curr_char = self.text[self.pos.idx] 
		else:
			self.curr_char =  None

	def generate_token(self):
		all_token = []

		while self.curr_char != None:
			if self.curr_char in ' \t':
				self.advance()
			elif self.curr_char in DIGITS:
				all_token.append(self.create_number())
			elif self.curr_char in '"':
				all_token.append(self.make_string())
			elif self.curr_char in LETTERS:
				all_token.append(self.create_identifier())
			elif self.curr_char == '+':
				all_token.append(Token(TokTypePLUS, position_start=self.pos))
				self.advance()
			elif self.curr_char == '-':
				all_token.append(Token(TokTypeMINUS, position_start=self.pos))
				self.advance()
			elif self.curr_char == '*':
				all_token.append(Token(TokTypeMUL, position_start=self.pos))
				self.advance()
			elif self.curr_char == '/':
				all_token.append(Token(TokTypeDIV, position_start=self.pos))
				self.advance()
			elif self.curr_char == '^':
				all_token.append(Token(TokTypePOW, position_start=self.pos))
				self.advance()
			elif self.curr_char == '(':
				all_token.append(Token(TokTypeLPAREN, position_start=self.pos))
				self.advance()
			elif self.curr_char == ')':
				all_token.append(Token(TokTypeRPAREN, position_start=self.pos))
				self.advance()
			elif self.curr_char == '!':
				token, error = self.not_equal_sign()
				if error: return [], error
				all_token.append(token)
			elif self.curr_char == '=':
				all_token.append(self.equals_sign())
			elif self.curr_char == '<':
				all_token.append(self.less_than_sign())
			elif self.curr_char == '>':
				all_token.append(self.greater_than_sign())
			else:
				char = self.curr_char
				self.advance()
				return [], IllegalCharacterError("'" + char + "'")

		all_token.append(Token(TokTypeEOF, position_start=self.pos))
		return all_token, None

	def create_number(self):
		num_str = ''
		dot_count = 0
		position_start = self.pos.copy()

		while self.curr_char != None and self.curr_char in DIGITS + '.':
			if self.curr_char == '.':
				if dot_count == 1: 
					break
				dot_count += 1
			num_str += self.curr_char
			self.advance()

		if dot_count == 0:
			return Token(TokType_INT, int(num_str), position_start, self.pos)
		else:
			return Token(TokTypeFLOAT, float(num_str), position_start, self.pos)

	def create_identifier(self):
		id_str = ''
		position_start = self.pos.copy()

		while self.curr_char != None and self.curr_char in LETTERS_DIGITS + '_':
			id_str += self.curr_char
			self.advance()

		tok_type = TokTypeKEYWORD if id_str in KEYWORDS else TokTypeIDENTIFIER
		return Token(tok_type, id_str, position_start, self.pos)
	
	def make_string(self):
		result_str=""
		self.advance()
		position_start = self.pos.copy()
		while self.curr_char!= '"' and self.curr_char in LETTERS:
			result_str+=self.curr_char
			self.advance()
		self.advance()
		return Token(TokType_STR,result_str,position_start,self.pos)

	def not_equal_sign(self):
		position_start = self.pos.copy()
		self.advance()
		if self.curr_char == '=':
			self.advance()
			return Token(TokTypeNE, position_start=position_start, position_end=self.pos), None

		self.advance()
		return None, ExpectedCharError("'=' (after '!')")
	
	def equals_sign(self):
		tok_type = TokTypeEQ
		position_start = self.pos.copy()
		self.advance()

		if self.curr_char == '=':
			self.advance()
			tok_type = TokTypeEE

		return Token(tok_type, position_start=position_start, position_end=self.pos)

	def less_than_sign(self):
		tok_type = TokTypeLT
		position_start = self.pos.copy()
		self.advance()

		if self.curr_char == '=':
			self.advance()
			tok_type = TokTypeLTE

		return Token(tok_type, position_start=position_start, position_end=self.pos)

	def greater_than_sign(self):
		tok_type = TokTypeGT
		position_start = self.pos.copy()
		self.advance()

		if self.curr_char == '=':
			self.advance()
			tok_type = TokTypeGTE

		return Token(tok_type, position_start=position_start, position_end=self.pos)