
#-----------------------------------------------------------
# Custom Ecupasssdocs exceptions
#-----------------------------------------------------------
class EcudocException (Exception):
	pass

class EcudocDocumentNotFoundException (EcudocException):
	pass

class EcudocConnectionNotOpenException (EcudocException):
	defaultMessage = "No se pudo conectar a CODEBIN"

	def __init__(self, message=None):
		self.message = message or self.defaultMessage
