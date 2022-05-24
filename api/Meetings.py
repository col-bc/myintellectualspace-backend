import datetime
import json
from flask import Blueprint, jsonify, request, g
import jwt
from app_secrets import VIDEOSDK_API_KEY, VIDEOSDK_API_SECRET
from flask_cors import CORS

from .Authorization import login_required

meetings_ep = Blueprint('meetings_ep', __name__, url_prefix='/api/meetings')
CORS(meetings_ep)


@meetings_ep.route("/jwt", methods=["GET"])
@login_required
def get_bearer_token():
    if request.method != 'GET':
        return jsonify({'error': 'Method not allowed'}), 405

    if not g.user:
        return jsonify({'error': 'User not logged in'}), 401

    expires = 24 * 3600
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(seconds=expires)

    payload = {
        'apikey': VIDEOSDK_API_KEY,
    }

    token = jwt.encode(payload, VIDEOSDK_API_SECRET, algorithm='HS256')
    print('[?] Generated VideoSDK json web token: ', token)
    return jsonify({'token': token}), 200
