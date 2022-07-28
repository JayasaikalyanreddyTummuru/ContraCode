import basic
import Parser
import Interpreter
while True:
	text = input('contracode > ')
	lex = basic.Lexer('<stdin>', text)
	res, err = lex.tokens()
	if err:
		print("Lexical error",err.output())
	else:
		print(res)
		parser = Parser.Parser(res)
		obj = parser.parse()
		if obj.error: 
			print("Syntactic error",obj.error)
		else:
			print(obj.node)
			interpreter = Interpreter.Interpreter()
			# context = Parser.Context('<program>')
			result = interpreter.visit(obj.node)
			if result.error:
				print("Run time error",result.error)
			else:
				print(result.value)

