import datetime

import jwt
from app_secrets import VIDEOSDK_API_KEY, VIDEOSDK_API_SECRET
from flask import Blueprint, g, jsonify, request
from flask_cors import CORS

from endpoints.AuthEndpoint import get_user_by_token

meetings_ep = Blueprint('meetings_ep', __name__, url_prefix='/api/meetings')
CORS(meetings_ep)


@meetings_ep.before_request
def get_identity():
    if request.method == 'OPTIONS':
        return jsonify('ok'), 204

    if request.method == 'GET' or request.method == 'POST':
        user = None

    if 'Authorization' not in request.headers:
        return jsonify({'error': 'Missing authorization header'}), 401

    token = request.headers['Authorization'].split(' ')[1]
    user = get_user_by_token(token)

    if user is None:
        print(f'User not found with token {token}')
        g.user = None
        return jsonify({'error': 'Invalid token'}), 401

    g.user = user
    return


@meetings_ep.route("/jwt", methods=["GET"])
def create_meeting():
    if request.method != 'GET':
        return jsonify({'error': 'Method not allowed'}), 405

    if not g.user:
        return jsonify({'error': 'User not logged in'}), 401

    payload = {
        'iss': VIDEOSDK_API_KEY,
        'sub': g.user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, VIDEOSDK_API_SECRET, algorithm='HS256')
    return jsonify({'token': token.decode('UTF-8')}), 200

    if g.user is None:
        return jsonify({'error': 'Invalid token'}), 401

    token = jwt.encode(
        algorithm='HS256',
        payload={'apikey': VIDEOSDK_API_KEY},
        key=VIDEOSDK_API_SECRET)

    print(f'[*] Generated JWT token: <JWT {token[:3]}...{token[-4:]}>')
    return jsonify({'token': token}), 200
