from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    payload = {
        'response': {
            'statusCode': status_code,
            'statusText': HTTP_STATUS_CODES.get(status_code, 406)
        }
    }
    if message:
        payload['data'] = {
            'status': False,
            'message': message
        }
    response = jsonify(payload)
    response.status_code = status_code

    return response


def success_response(status_code, message=None, data=None):
    payload = {
        'response': {
            'statusCode': status_code,
            'statusText': HTTP_STATUS_CODES.get(status_code, 200)
        }
    }
    payload['data'] = {
        'status': True,
    }
    if message:
        payload['data']['message'] = message
    if data:
        payload['data']['data'] = data

    response = jsonify(payload)
    response.status_code = status_code

    return response
