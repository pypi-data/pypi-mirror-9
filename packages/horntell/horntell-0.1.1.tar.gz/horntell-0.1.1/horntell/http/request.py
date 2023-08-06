import json
import horntell
from horntell.http import client
from horntell.errors import (Error, InvalidRequestError, AuthenticationError, ForbiddenError, NotFoundError, NetworkError, ServiceError)
from horntell.http.response import Response

class Request(object):
	def __init__(self):
		self.client = client.Client()
		self.key    = horntell.key
		self.secret = horntell.secret
		self.base   = horntell.base


	#
	# Manages all the processing of the request
	#
	def request(self, method, endpoint, params=None):

		# creating an request
		result = self.request_raw(
			method, endpoint, params)

		# interpreting response
		response = self.interpret_response(result)

		return Response(response)


	#
	# Handling all the errors from api
	#
	def handle_api_error(self, body, code, resp):
		try:
			err = resp['error']
		except (KeyError, TypeError):
			raise Error(
				"Invalid response object from API: %r (HTTP response code "
				"was %d)" % (body, code), code)
		if code == 400:
			raise InvalidRequestError(
				err.get('message'), code, err.get('type'))
		elif code == 401:
			raise AuthenticationError(
				err.get('message'), code, err.get('type'))
		elif code == 403:
			raise ForbiddenError(
				err.get('message'), code, err.get('type'))
		elif code == 404:
			raise NotFoundError(
				err.get('message'), code, err.get('type'))
		elif code == 500:
			raise ServiceError(
				err.get('message'), code, err.get('type'))
		else:
			raise Error(err.get('message'), code, err.get('type'))


	#
	# Handles the requset to be send
	#
	def request_raw(self, method, endpoint, params=None):

		auth = (self.key, self.secret)
		url = self.base + endpoint

		headers = {
			'Accept': 'application/vnd.horntell.'+ horntell.version +'+json',
			'Content-Type' : 'application/json'
		}


		# encoding the parameters
		params = json.dumps(params)

		return self.client.request(
			method, url, headers, auth, params)

	#
	# Interprets the response
	#
	def interpret_response(self, result):
		body = result.content
		code = result.status_code

		if (code == 204):
			return result


		# Decodes the response
		try:
			if hasattr(body, 'decode'):
				body = body.decode('utf-8')
			resp = json.loads(body)
		except Exception, e:
			raise Error(
				"Invalid response body from API: %s "
				"(HTTP response code was %d)" % (body, code), code)


		# Handles the exception thrown from api
		if not (200 <= code < 300):
			self.handle_api_error(body, code, resp)

		return result