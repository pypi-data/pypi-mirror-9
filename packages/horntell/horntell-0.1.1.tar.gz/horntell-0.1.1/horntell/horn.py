import horntell
from horntell.http import request

class Horn:

	def __init__(self):
		self.request = request.Request()

	#
	# Sends horn to a profile
	#
	def to_profile(self, uid, horn):
		return self.request.request(
			'post', '/profiles/' + uid + '/horns', horn)
	#
	# Sends horn to multiple profiles
	#
	def to_profiles(self, profiles, horn):
		horn['profile_uids'] = profiles

		return self.request.request(
			'post', '/profiles/horns', horn)
