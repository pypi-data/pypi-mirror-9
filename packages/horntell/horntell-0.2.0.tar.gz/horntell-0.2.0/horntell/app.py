import horntell
import hmac
import hashlib

class App:

	key     = None
	secret  = None
	base    = 'http://api.horntell.com'
	version = 'v1'

	#
	# initiailses the app and secret of the app
	#
	@classmethod
	def init(cls, key = None, secret = None):
		cls.key    = key
		cls.secret = secret

	#
	# sets the base url of the app
	#
	@classmethod
	def set_base(cls, base = None):
		cls.base = base

	#
	# returns the base url of the app
	#
	@classmethod
	def get_base(cls):
		return cls.base

	#
	# returns the key of the app
	#
	@classmethod
	def get_key(cls):
		return cls.key

	#
	# returns the secret of the app
	#
	@classmethod
	def get_secret(cls):
		return cls.secret
	#
	# sets the version of the app
	#
	@classmethod
	def set_version(cls, version = None):
		cls.version = version

	#
	# returns the version of the app
	#
	@classmethod
	def get_version(cls):
		return cls.version
	#
	# returns the hash hmac sha256
	#
	@classmethod
	def hash(cls, uid):
		return hmac.new(cls.secret, uid, hashlib.sha256).hexdigest()
