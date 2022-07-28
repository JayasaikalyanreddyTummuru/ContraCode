# Error Class
class Error:
	def __init__(self, error_name, ErrorDetail):
		self.error_name = error_name
		self.ErrorDetail = ErrorDetail
	
	def as_string(self):
		res  = f'{self.error_name}: {self.ErrorDetail}\n'
		return res

# Classes which inherits the Error class for specific errors.
class IllegalCharacterError(Error):
	def __init__(self, ErrorDetail):
		super().__init__( 'Illegal Char: ', ErrorDetail)
# Expected Char Error
class ExpectedCharError(Error):
	def __init__(self, ErrorDetail):
		super().__init__( 'Expected Char: ', ErrorDetail)
#Invalid Syntax Exception
class InvalidSyntaxException(Error):
	def __init__(self, ErrorDetail=''):
		super().__init__( 'Invalid Syntax', ErrorDetail)
# Run time Error
class RTError(Error):
	def __init__(self, ErrorDetail, context):
		super().__init__( 'Runtime Error', ErrorDetail)
		self.context = context
