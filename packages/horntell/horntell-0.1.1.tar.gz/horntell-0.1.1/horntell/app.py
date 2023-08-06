import horntell

class App:

	#
	# initiailses the app and secret of the app
	#
	def init(self, key = None, secret = None):
		horntell.key    = key
		horntell.secret = secret

	#
	# sets the base url of the app
	#
	def set_base(self, base = None):
		horntell.base = base

	#
	# returns the base url of the app
	#
	def get_base(self):
		return horntell.base

	#
	# returns the key of the app
	#
	def get_key(self):
		return horntell.key

	#
	# returns the secret of the app
	#
	def get_secret(self):
		return horntell.secret
	#
	# sets the version of the app
	#
	def set_version(self, version = None):
		horntell.version = version

	#
	# returns the version of the app
	#
	def get_version(self):
		return horntell.version
