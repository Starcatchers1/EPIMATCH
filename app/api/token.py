from flask_httpauth import HTTPTokenAuth

from ..utils.token_util import check_token
from .errors import error_response


token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(token):
    return check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status, 'Token is invalid')
