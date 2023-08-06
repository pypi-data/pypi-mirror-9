import os
import sys
import textwrap
import requests
import horntell
import json

from horntell.errors import NetworkError

class Client:
	name = 'requests'

	def request(self, method, url, headers, auth, post_data=None):

			try:
				try:
					result = requests.request(method,
												url,
												headers=headers,
												data=post_data,
												auth=auth,
												timeout=80)
				except TypeError, e:
					raise TypeError(
							'Warning: It looks like your installed version of the '
							'"requests" library is not compatible with horntell\'s '
							'usage thereof. (HINT: The most likely cause is that '
							'your "requests" library is out of date. You can fix '
							'that by running "pip install -U requests".) The '
							'underlying error was: %s' % (e,))

				# This causes the content to actually be read, which could cause
				# e.g. a socket timeout. TODO: The other fetch methods probably
				# are susceptible to the same and should be updated.
			except Exception, e:
				raise NetworkError()

			return result
