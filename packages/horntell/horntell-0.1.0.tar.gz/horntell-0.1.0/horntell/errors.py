# Exceptions
class Error(Exception):

	def __init__(self, message=None, code=None,
				 type=None):
		super(Error, self).__init__(message)

		self.code = code
		self.type = type


class InvalidRequestError(Error):
	pass

class AuthenticationError(Error):
	pass

class ForbiddenError(InvalidRequestError):
	pass

class NotFoundError(InvalidRequestError):
	pass

class NetworkError(Error):
	def __init__(self, message=None, code=None, type=None):
		super(NetworkError, self).__init__(message, code, type)
		self.message="Could not connect to Horntell. Please check your network connection and try again. If the problem persists, please get in touch with us at hello@horntell.com."
		self.type='network_error'

class ServiceError(Error):
	pass
