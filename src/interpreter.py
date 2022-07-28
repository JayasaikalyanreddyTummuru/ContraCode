from Lexer import *
from error import RTError
from final import Number

class RunTimeResult:
	def __init__(self):
		self.val = None
		self.error = None
  
	def success(self, val):
		self.val = val
		return self
	def register(self, res):
		if res.error: self.error = res.error
		return res.val
	def failure(self, error):
		self.error = error
		return self


class Interpreter:
	def visit(self, first_node, context):
		nameOfMethod = f'visit_{type(first_node).__name__}'
		method = getattr(self, nameOfMethod, self.methodNotVisited)
		return method(first_node, context)

	def methodNotVisited(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_NumberNode(self, node, context):
		return RunTimeResult().success(
			Number(node.tok.value).set_context(context).setting_position(node.position_start, node.position_end)
		)

	def visit_VariableAccessNode(self, node, context):
		res = RunTimeResult()
		variable_name = node.token_variable.value
		value = context.symbol_table.get(variable_name)

		if not value:
			return res.failure(RTError("'{variable_name}' name is not defined",context))

		value = value.copy().setting_position(node.position_start, node.position_end)
		return res.success(value)

	def visit_VariableAssignNode(self, node, context):
		res = RunTimeResult()
		variable_name = node.token_variable.value
		value = res.register(self.visit(node.value_node, context))
		if res.error: return res

		context.symbol_table.set(variable_name, value)
		return res.success(value)

	def visit_BinaryOperandNode(self, node, context):
		res = RunTimeResult()
		left = res.register(self.visit(node.node_left, context))
		if res.error: return res
		right = res.register(self.visit(node.node_right, context))
		if res.error: return res

		if node.operand_token.type == TokTypePLUS:
			result, error = left.addTo(right)
		elif node.operand_token.type == TokTypeMINUS:
			result, error = left.substractedBy(right)
		elif node.operand_token.type == TokTypeMUL:
			result, error = left.multipliedBy(right)
		elif node.operand_token.type == TokTypeDIV:
			result, error = left.dividedBy(right)
		
		elif node.operand_token.type == TokTypeEE:
			result, error = left.get_comparison_eq(right)
		elif node.operand_token.type == TokTypeNE:
			result, error = left.get_comparison_ne(right)
		elif node.operand_token.type == TokTypeLT:
			result, error = left.get_comparison_lt(right)
		elif node.operand_token.type == TokTypeGT:
			result, error = left.get_comparison_gt(right)
		elif node.operand_token.token_match(TokTypeKEYWORD, 'AND'):
			result, error = left.anded_by(right)
		elif node.operand_token.token_match(TokTypeKEYWORD, 'OR'):
			result, error = left.ored_by(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.setting_position(node.position_start, node.position_end))

	def visit_UnaryOperandNode(self, node, context):
		res = RunTimeResult()
		number = res.register(self.visit(node.node, context))
		if res.error: return res

		error = None

		if node.operand_token.type == TokTypeMINUS:
			number, error = number.multipliedBy(Number(-1))
		elif node.operand_token.token_match(TokTypeKEYWORD, 'NOT'):
			number, error = number.notted()

		if error:
			return res.failure(error)
		else:
			return res.success(number.setting_position(node.position_start, node.position_end))

	def visit_IfNode(self, node, context):
		res = RunTimeResult()

		for condition, expr in node.cases:
			condition_value = res.register(self.visit(condition, context))
			if res.error: return res

			if condition_value.is_true():
				expr_value = res.register(self.visit(expr, context))
				if res.error: return res
				return res.success(expr_value)

		if node.else_case:
			else_value = res.register(self.visit(node.else_case, context))
			if res.error: return res
			return res.success(else_value)

		return res.success(None)

	def visit_ForNode(self, node, context):
		res = RunTimeResult()

		start_value = res.register(self.visit(node.node_start_value, context))
		if res.error: return res

		end_value = res.register(self.visit(node.node_end_value, context))
		if res.error: return res

		if node.node_step_value:
			step_value = res.register(self.visit(node.node_step_value, context))
			if res.error: return res
		else:
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: i < end_value.value
		else:
			condition = lambda: i > end_value.value
		
		while condition():
			context.symbol_table.set(node.token_variable.value, Number(i))
			i += step_value.value

			res.register(self.visit(node.body_node, context))
			if res.error: return res

		return res.success(None)

	def visit_WhileNode(self, node, context):
		res = RunTimeResult()

		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.error: return res

			if not condition.is_true(): break

			res.register(self.visit(node.body_node, context))
			if res.error: return res

		return res.success(None)



