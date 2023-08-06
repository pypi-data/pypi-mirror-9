import horntell
from horntell.http import request

class Profile:

	def __init__(self):
		self.request = request.Request()

	#
	# Returns a profile
	#
	def find(self, uid):
		return self.request.request(
			'get', '/profiles/' + uid)
	#
	# Creates a profile
	#
	def create(self, profile = None):
		return self.request.request(
			'post', '/profiles', profile)

	#
	# Updates a profile
	#
	def update(self, uid, profile = None):
		return self.request.request(
			'put', '/profiles/' + uid, profile)
	#
	# Deletes a profile
	#
	def delete(self, uid):
		return self.request.request(
			'delete', '/profiles/' + uid)
