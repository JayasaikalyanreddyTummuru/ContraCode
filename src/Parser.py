import basic
import Error
class NumberNode:
	def __init__(self, tok):
		self.tok = tok
	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class IfNode:
	def __init__(self, if_cases, else_case):
		self.cases = if_cases
		self.else_case = else_case

		self.pos_start = self.if_cases[0][0].pos_start
		self.pos_end = (self.else_case or self.if_cases[len(self.if_cases) - 1][0]).pos_end

class ForNode:
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
		self.var_name_tok = var_name_tok
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.body_node.pos_end

class WhileNode:
	def __init__(self, condition, body):
		self.condition = condition
		self.body = body

		self.pos_start = self.condition.pos_start
		self.pos_end = self.body.pos_end


class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.advance_count = 0

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self

	def register_advancement(self):
		self.advance_count += 1


class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self, current_char=None):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.token_type != basic.TT_EOF:
			return res.failure(Error.InvalidSyntaxError("Expected '+', '-', '*' or '/'"))
		return res


	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.token_type in (basic.TT_PLUS, basic.TT_MINUS):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))
		
		elif tok.token_type in (basic.TT_INT, basic.TT_FLOAT):
			res.register(self.advance())
			return res.success(NumberNode(tok))

		elif tok.token_type == basic.TT_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.token_type == basic.TT_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(Error.InvalidSyntaxError("Expected ')'" ))

		elif tok.token_match (basic.TT_KEYWORD, 'IF'):
			if_expr = res.register(self.if_expr(tok))
			if res.error: return res
			return res.success(if_expr)
		
		elif tok.token_match (basic.TT_KEYWORD, 'FOR'):
			for_expr = res.register(self.for_expr())
			if res.error: return res
			return res.success(for_expr)

		elif tok.token_match (basic.TT_KEYWORD, 'WHILE'):
			while_expr = res.register(self.while_expr())
			if res.error: return res
			return res.success(while_expr)

		return res.failure(Error.InvalidSyntaxError("Expected int or float"))

	def term(self):
		return self.bin_op(self.factor, (basic.TT_MUL, basic.TT_DIV))

	def expr(self):
		return self.bin_op(self.term, (basic.TT_PLUS, basic.TT_MINUS))
	


	def bin_op(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.token_type in ops:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)
	

	def if_expr(self, tok):
		res = ParseResult()
		self.tok = tok
		cases = []
		else_case = None

		if not self.current_tok.token_match(basic.TT_KEYWORD,'IF'):
			return res.failure(Error.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'IF'"
			))

		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.token_match(basic.TT_KEYWORD, 'THEN'):
			return res.failure(Error.InvalidSyntaxError(f"Expected 'THEN'"))

		res.register_advancement()
		self.advance()

		expr = res.register(self.expr())
		if res.error: return res
		cases.append((condition, expr))

		while self.current_tok.token_match(basic.TT_KEYWORD,'ELSEIF'):
			res.register_advancement()
			self.advance()

			condition = res.register(self.expr())
			if res.error: return res

			if not self.current_tok.token_match(basic.TT_KEYWORD, 'THEN'):
				return res.failure(Error.InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Expected 'THEN'"
				))

			res.register_advancement()
			self.advance()

			expr = res.register(self.expr())
			if res.error: return res
			cases.append((condition, expr))

		if self.current_tok.token_match(basic.TT_KEYWORD, 'ELSE'):
			res.register_advancement()
			self.advance()

			else_case = res.register(self.expr())
			if res.error: return res

		return res.success(IfNode(cases, else_case))

	def for_expr(self):
		res = ParseResult()

		if not self.current_tok.token_match(basic.TT_KEYWORD, 'FOR'):
			return res.failure(Error.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'FOR'"
			))

		res.register_advancement()
		self.advance()

		if self.current_tok.type != basic.TT_IDENTIFIER:
			return res.failure(Error.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected identifier"
			))

		var_name = self.current_tok
		res.register_advancement()
		self.advance()

		if self.current_tok.type != basic.TT_EQ:
			return res.failure(basic.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected '='"
			))
		
		res.register_advancement()
		self.advance()

		start_value = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.token_matche(basic.TT_KEYWORD, 'TO'):
			return res.failure(Error.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'TO'"
			))
		
		res.register_advancement()
		self.advance()

		end_value = res.register(self.expr())
		if res.error: return res

		if self.current_tok.token_matche(basic.TT_KEYWORD, 'STEP'):
			res.register_advancement()
			self.advance()

			step_value = res.register(self.expr())
			if res.error: return res
		else:
			step_value = None

		if not self.current_tok.token_matche(basic.TT_KEYWORD, 'THEN'):
			return res.failure(Error.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'THEN'"
			))

		res.register_advancement()
		self.advance()

		body = res.register(self.expr())
		if res.error: return res

		return res.success(ForNode(var_name, start_value, end_value, step_value, body))


	def while_expr(self):
		res = ParseResult()

		if not self.current_tok.token_matche(basic.TT_KEYWORD, 'WHILE'):
			return res.failure(Error.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'WHILE'"
			))

		res.register_advancement()
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.token_matche(basic.TT_KEYWORD, 'THEN'):
			return res.failure(Error.InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'THEN'"
			))

		res.register_advancement()
		self.advance()

		body = res.register(self.expr())
		if res.error: return res

		return res.success(WhileNode(condition, body))


class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self




