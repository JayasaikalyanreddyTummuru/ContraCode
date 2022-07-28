from final import Parser
from Lexer import Lexer 
from interpreter import Interpreter
from final import Number

class Context:
	def __init__(self, nameDisplayed, parentNode=None, entry_position=None):
		self.nameDisplayed = nameDisplayed
		self.parentNode = parentNode
		self.entry_position = entry_position
		self.symbol_table = None


class SymbolTable:
	def __init__(self):
		self.symbols = {}
		self.parent = None

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]

globalSymbolTable = SymbolTable()
globalSymbolTable.set("NULL", Number(0))
globalSymbolTable.set("FALSE", Number(0))
globalSymbolTable.set("TRUE", Number(1))

def run(fn, text):
	lexer = Lexer(fn, text)
	all_token, error = lexer.generate_token()
	if error: 
		all_token = None
		return all_token, error
	print(all_token)
	parser = Parser(all_token)
	parsed_output = parser.parse()
	if parsed_output.error: 
		return None, parsed_output.error

	interpreter = Interpreter()
	context = Context('<program>')
	context.symbol_table = globalSymbolTable
	result = interpreter.visit(parsed_output.node, context)

	return result.val, result.error




while True:
	text = input('ContraCode > ')
	result, error = run('<stdin>', text)

	if error: print(error)
	elif result: print(result)




