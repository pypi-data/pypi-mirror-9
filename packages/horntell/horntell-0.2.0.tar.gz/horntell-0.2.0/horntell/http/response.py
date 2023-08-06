import json

class Response:

	def __init__(self, response):
		self.response = response
		self.content = self.response.content

	#
	#  Returns the orignal response
	#
	def get_original(self):
		return self.response

	#
	#  Gets the parsed JSON body
	#
	def get_body(self):
		if self.get_status_code() == 204:
			self.body = None
		else:
			self.body = json.loads(self.content)

		return self.body

	#
	#   Gets the HTTP Status Code
	#
	def get_status_code(self):
		return self.response.status_code
