from flask import Blueprint, request, jsonify, g
from flask_cors import CORS
from database import db
from .AuthEndpoint import get_user_by_token
import json
from datetime import datetime


user_ep = Blueprint("user_ep", __name__, url_prefix="/api/user")
CORS(user_ep)


@user_ep.before_request
def get_identity():
    if request.method == 'OPTIONS':
        return jsonify({'ok': 'ok'}), 204

    if request.method == 'GET' or request.method == 'POST':
        user = None

    if 'Authorization' not in request.headers:
        return jsonify({'error': 'Missing authorization header'}), 401

    token = request.headers['Authorization'].split(' ')[1]
    user = get_user_by_token(token)

    if user is None:
        g.user = None
        return jsonify({'error': 'Invalid token'}), 401

    g.user = user
    return


@user_ep.route("/", methods=["GET"])
def get_user():
    '''Returns the user object for the currently logged in user.'''
    if request.method != 'GET':
        return jsonify({'error': 'Method not allowed'}), 405

    return jsonify(g.user.to_json()), 200


@user_ep.route("/update", methods=["POST"])
def update_user():
    '''Updates the user object for the currently logged in user.'''
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    data = request.get_json()
    if data is None:
        print('[!] No data provided')
        return jsonify({'error': 'No json data'}), 400

    new_user_data = g.user.to_json()

    for key in data:
        if key == 'email' or key == 'auth_token' or key == 'token_expiration' or key == 'created_at' or key == 'updated_at' or key not in g.user.to_json().keys():
            print(f'[!] Will not update {key} from this endpoint')
            pass
        else:
            new_user_data[key] = data[key]
    g.user.update(new_user_data)
    db.session.commit()
    return jsonify({'success': 'User data  updated',
                             'user': g.user.to_json()}), 200


@user_ep.route("/delete", methods=["DELETE"])
def delete_user():
    if request.method != 'DELETE':
        return jsonify({'error': 'Method not allowed'}), 405

    db.session.delete(g.user)
    db.session.commit()
    g.user = None
    return jsonify({'success': 'User deleted'}), 200
