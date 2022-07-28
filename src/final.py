from error import *
from Lexer import  * 

class NumberNode:
	def __init__(self, tok):
		self.tok = tok

		self.position_start = self.tok.position_start
		self.position_end = self.tok.position_end

	def __repr__(self):
		return f'{self.tok}'

class VariableAccessNode:
	def __init__(self, token_variable):
		self.token_variable = token_variable

		self.position_start = self.token_variable.position_start
		self.position_end = self.token_variable.position_end

class VariableAssignNode:
	def __init__(self, token_variable, value_node):
		self.token_variable = token_variable
		self.value_node = value_node

		self.position_start = self.token_variable.position_start
		self.position_end = self.value_node.position_end

class BinaryOperandNode:
	def __init__(self, node_left, operand_token, node_right):
		self.node_left = node_left
		self.operand_token = operand_token
		self.node_right = node_right

		self.position_start = self.node_left.position_start
		self.position_end = self.node_right.position_end

	def __repr__(self):
		return f'({self.node_left}, {self.operand_token}, {self.node_right})'

class UnaryOperandNode:
	def __init__(self, operand_token, node):
		self.operand_token = operand_token
		self.node = node

		self.position_start = self.operand_token.position_start
		self.position_end = node.position_end

	def __repr__(self):
		return f'({self.operand_token}, {self.node})'

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.position_start = self.cases[0][0].position_start
		self.position_end = (self.else_case or self.cases[len(self.cases) - 1][0]).position_end

class ForNode:
	def __init__(self, token_variable, node_start_value, node_end_value, node_step_value, body_node):
		self.token_variable = token_variable
		self.node_start_value = node_start_value
		self.node_end_value = node_end_value
		self.node_step_value = node_step_value
		self.body_node = body_node

		self.position_start = self.token_variable.position_start
		self.position_end = self.body_node.position_end

class WhileNode:
	def __init__(self, condition_node, body_node):
		self.condition_node = condition_node
		self.body_node = body_node

		self.position_start = self.condition_node.position_start
		self.position_end = self.body_node.position_end

class ParsingResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.counterForAdvance = 0

	def next_advance(self):
		self.counterForAdvance += 1

	def register(self, res):
		self.counterForAdvance += res.counterForAdvance
		if res.error: 
			self.error = res.error
		return res.node

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		if not self.error or self.counterForAdvance == 0:
			self.error = error
		return self
class Parser:
	def __init__(self, all_token):
		self.all_token = all_token
		self.idx_tok = -1
		self.advance()

	def advance(self, ):
		self.idx_tok += 1
		if self.idx_tok < len(self.all_token):
			self.current_tok = self.all_token[self.idx_tok]
		return self.current_tok

	def parse(self):
		res = self.expression()
		if not res.error and self.current_tok.type != TokTypeEOF:
			return res.failure(InvalidSyntaxException("Excepted Arithmetic or comparison operators"))
		return res
#--------------------------------------------------------------------

	def IF_Expression(self):
		res = ParsingResult()
		cases = []
		else_case = None

		if not self.current_tok.token_match(TokTypeKEYWORD, 'IF'):
			return res.failure(InvalidSyntaxException("Expected IF"))

		res.next_advance()
		self.advance()

		condition = res.register(self.expression())
		if res.error: 
			return res

		if not self.current_tok.token_match(TokTypeKEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxException("Expected THEN"))

		res.next_advance()
		self.advance()

		expr = res.register(self.expression())
		if res.error: 
			return res
		cases.append((condition, expr))

		while self.current_tok.token_match(TokTypeKEYWORD, 'ELIF'):
			res.next_advance()
			self.advance()

			condition = res.register(self.expression())
			if res.error: 
				return res

			if not self.current_tok.token_match(TokTypeKEYWORD, 'THEN'):
				return res.failure(InvalidSyntaxException("Expected THEN"))

			res.next_advance()
			self.advance()

			expr = res.register(self.expression())
			if res.error: 
				return res
			cases.append((condition, expr))

		if self.current_tok.token_match(TokTypeKEYWORD, 'ELSE'):
			res.next_advance()
			self.advance()

			else_case = res.register(self.expression())
			if res.error: 
				return res

		return res.success(IfNode(cases, else_case))

	def FOR_Expression(self):
		res = ParsingResult()

		if not self.current_tok.token_match(TokTypeKEYWORD, 'FOR'):
			return res.failure(InvalidSyntaxException("Unexpected Syntax"))

		res.next_advance()
		self.advance()

		if self.current_tok.type != TokTypeIDENTIFIER:
			return res.failure(InvalidSyntaxException("identifier expected"))

		variable_name = self.current_tok
		res.next_advance()
		self.advance()

		if self.current_tok.type != TokTypeEQ:
			return res.failure(InvalidSyntaxException("equal sign expected"))
		
		res.next_advance()
		self.advance()

		start_value = res.register(self.expression())
		if res.error: 
			return res

		if not self.current_tok.token_match(TokTypeKEYWORD, 'TO'):
			return res.failure(InvalidSyntaxException("Expected TO"))
		
		res.next_advance()
		self.advance()

		end_value = res.register(self.expression())
		if res.error: 
			return res

		if self.current_tok.token_match(TokTypeKEYWORD, 'STEP'):
			res.next_advance()
			self.advance()

			step_value = res.register(self.expression())
			if res.error: 
				return res
		else:
			step_value = None

		if not self.current_tok.token_match(TokTypeKEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxException("Expected THEN"))

		res.next_advance()
		self.advance()

		body = res.register(self.expression())
		if res.error: 
			return res

		return res.success(ForNode(variable_name, start_value, end_value, step_value, body))

	def WHILE_expression(self):
		res = ParsingResult()

		if not self.current_tok.token_match(TokTypeKEYWORD, 'WHILE'):
			return res.failure(InvalidSyntaxException("Expected WHILE"))

		res.next_advance()
		self.advance()

		condition = res.register(self.expression())
		if res.error: 
			return res

		if not self.current_tok.token_match(TokTypeKEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxException("Expected THEN"))

		res.next_advance()
		self.advance()

		body = res.register(self.expression())
		if res.error: 
			return res

		return res.success(WhileNode(condition, body))

	def element(self):
		res = ParsingResult()
		tok = self.current_tok

		if tok.type in (TokType_INT, TokTypeFLOAT):
			res.next_advance()
			self.advance()
			return res.success(NumberNode(tok))

		elif tok.type == TokTypeIDENTIFIER:
			res.next_advance()
			self.advance()
			return res.success(VariableAccessNode(tok))
		
		elif tok.token_match(TokTypeKEYWORD, 'IF'):
			IF_Expression = res.register(self.IF_Expression())
			if res.error: 
				return res
			return res.success(IF_Expression)

		elif tok.token_match(TokTypeKEYWORD, 'FOR'):
			FOR_Expression = res.register(self.FOR_Expression())
			if res.error: 
				return res
			return res.success(FOR_Expression)

		elif tok.token_match(TokTypeKEYWORD, 'WHILE'):
			WHILE_expression = res.register(self.WHILE_expression())
			if res.error: 
				return res
			return res.success(WHILE_expression)

		return res.failure(InvalidSyntaxException("Invalid syntax"))

	def power(self):
		return self.binary_operand(self.element, (TokTypePOW, ), self.factor)

	def factor(self):
		res = ParsingResult()
		tok = self.current_tok

		if tok.type in (TokTypePLUS, TokTypeMINUS):
			res.next_advance()
			self.advance()
			factor = res.register(self.factor())
			if res.error: 
				return res
			return res.success(UnaryOperandNode(tok, factor))

		return self.power()

	def term(self):
		return self.binary_operand(self.factor, (TokTypeMUL, TokTypeDIV))

	def arithematic_expression(self):
		return self.binary_operand(self.term, (TokTypePLUS, TokTypeMINUS))

	def comparator_Expression(self):
		res = ParsingResult()

		if self.current_tok.token_match(TokTypeKEYWORD, 'NOT'):
			operand_token = self.current_tok
			res.next_advance()
			self.advance()

			node = res.register(self.comparator_Expression())
			if res.error: 
				return res
			return res.success(UnaryOperandNode(operand_token, node))
		
		node = res.register(self.binary_operand(self.arithematic_expression, (TokTypeEE, TokTypeNE, TokTypeLT, TokTypeGT, TokTypeLTE, TokTypeGTE)))
		
		if res.error:
			return res.failure(InvalidSyntaxException("Invalid syntax"))

		return res.success(node)

	def expression(self):
		res = ParsingResult()

		if self.current_tok.token_match(TokTypeKEYWORD, 'VAR'):
			res.next_advance()
			self.advance()

			if self.current_tok.type != TokTypeIDENTIFIER:
				return res.failure(InvalidSyntaxException("Identifier expected"))

			variable_name = self.current_tok
			res.next_advance()
			self.advance()

			if self.current_tok.type != TokTypeEQ:
				return res.failure(InvalidSyntaxException("Expected equals"))

			res.next_advance()
			self.advance()
			expr = res.register(self.expression())
			if res.error: 
				return res
			return res.success(VariableAssignNode(variable_name, expr))

		node = res.register(self.binary_operand(self.comparator_Expression, ((TokTypeKEYWORD, 'AND'), (TokTypeKEYWORD, 'OR'))))

		if res.error:
			return res.failure(InvalidSyntaxException("Invalid syntax"))

		return res.success(node)

	#-----------------------------------------------

	def binary_operand(self, function_a, ops, function_b=None):
		if function_b == None:
			function_b = function_a
		
		result = ParsingResult()
		left = result.register(function_a())
		if result.error: 
			return result

		while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
			operand_token = self.current_tok
			result.next_advance()
			self.advance()
			right = result.register(function_b())
			if result.error: return result
			left = BinaryOperandNode(left, operand_token, right)

		return result.success(left)


class Number:
	def __init__(self, value):
		self.value = value
		self.setting_position()
		self.set_context()

	def setting_position(self, position_start=None, position_end=None):
		self.position_start = position_start
		self.position_end = position_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def addTo(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None

	def substractedBy(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None

	def multipliedBy(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None

	def dividedBy(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError('Division by zero',self.context)

			return Number(self.value / other.value).set_context(self.context), None

	def get_comparison_eq(self, other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).set_context(self.context), None

	def get_comparison_ne(self, other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).set_context(self.context), None

	def get_comparison_lt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).set_context(self.context), None

	def get_comparison_gt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).set_context(self.context), None

	def anded_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).set_context(self.context), None

	def ored_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).set_context(self.context), None

	def notted(self):
		return Number(1 if self.value == 0 else 0).set_context(self.context), None

	def copy(self):
		copy = Number(self.value)
		copy.setting_position(self.position_start, self.position_end)
		copy.set_context(self.context)
		return copy

	def is_true(self):
		return self.value != 0
	
	def __repr__(self):
		return str(self.value)


