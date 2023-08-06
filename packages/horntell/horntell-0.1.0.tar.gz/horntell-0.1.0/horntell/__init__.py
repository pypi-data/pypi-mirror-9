key     = None
secret  = None

base    = 'http://api.horntell.com'
version = 'v1'

#sdk
from horntell.app import App
from horntell.profile import Profile
from horntell.horn import Horn
from horntell.campaign import Campaign

from horntell.errors import (Error, InvalidRequestError, AuthenticationError, ForbiddenError, NotFoundError, NetworkError, ServiceError)
