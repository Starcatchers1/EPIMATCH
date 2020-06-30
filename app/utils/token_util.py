from datetime import datetime, timedelta
from os import urandom
import jwt

from app.models import User
from app import Config


def encode_auth_token(public_id_string):
    """
    Generates the Auth Token
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=7, seconds=5),
            'iat': datetime.utcnow(),
            'sub': public_id_string
        }
        # in bytes
        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        return token.decode('UTF-8')
    except Exception as e:
        return None


def generate_jwt_secret_key():
    """
    util function for jwt secret key
    to store in environment variables file
    """
    return urandom(24)


def check_token(token):
    try:
        data = jwt.decode(token, Config.JWT_SECRET_KEY)
        current_user = User.query.filter_by(
            public_id=data['sub']).first()
        if current_user is None:
            return None

        return current_user
    except:
        return False
