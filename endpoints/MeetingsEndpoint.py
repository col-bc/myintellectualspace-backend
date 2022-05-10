import datetime
import json
from flask import Blueprint, request, Response, g
import jwt
from app_secrets import VIDEOSDK_API_KEY, VIDEOSDK_API_SECRET
from database import db
from flask_cors import CORS

from endpoints.AuthEndpoint import get_user_by_token

meetings_ep = Blueprint('meetings_ep', __name__, url_prefix='/api/meetings')
CORS(meetings_ep)


@meetings_ep.before_request
def get_identity():
    if request.method == 'OPTIONS':
        return Response(status=202)

    if request.method == 'GET' or request.method == 'POST':
        user = None

    if 'Authorization' not in request.headers:
        return Response(status=401)

    token = request.headers['Authorization'].split(' ')[1]
    user = get_user_by_token(token)

    if user is None:
        print(f'User not found with token {token}')
        g.user = None
        return Response(response=json.dumps({'error': 'Invalid token'}),
                        status=401,
                        mimetype='application/json')

    g.user = user
    return


@meetings_ep.route("/jwt", methods=["GET"])
def create_meeting():
    if request.method != 'GET':
        return Response(status=405)

    if g.user is None:
        return Response(response=json.dumps({'error': 'Invalid token'}),
                        status=401,
                        mimetype='application/json')

    expires = 24 * 3600
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(seconds=expires)
    token = jwt.encode(
        algorithm='HS256',
        payload={'apikey': VIDEOSDK_API_KEY},
        key=VIDEOSDK_API_SECRET)

    print(token, type(token))
    return Response(response=json.dumps({'token': token}),
                    content_type='application/json',
                    status=200)
