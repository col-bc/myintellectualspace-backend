from flask import Blueprint, request, Response, g
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
        return Response(status=202)

    if request.method == 'GET' or request.method == 'POST':
        user = None

        try:
            token = request.headers.get('Authorization').split()[1]
            user = get_user_by_token(token)
            g.user = user
        except KeyError as e:
            return Response(status=401)
        except Exception as e:
            return Response(status=401)

        if user is None:
            g.user = None
            return Response(response=json.dumps({'error': 'Invalid token'}),
                            status=401,
                            mimetype='application/json')

        g.user = user
        pass


@user_ep.route("/", methods=["GET"])
def get_user():
    if request.method != 'GET':
        return Response(status=405)

    if g.user is None:
        return Response(response=json.dumps({'error': 'Invalid token'}),
                        status=401,
                        mimetype='application/json')

    return Response(response=json.dumps(g.user.to_json()),
                    status=200,
                    mimetype='application/json')


@user_ep.route("/update", methods=["POST"])
def update_user():
    if request.method != 'POST':
        return Response(status=405)

    if g.user == None:
        return Response(response=json.dumps({'error': 'Invalid token'}),
                        status=401,
                        mimetype='application/json')

    data = request.get_json()
    if data is None:
        return Response(response=json.dumps({'error': 'No json data'}),
                        status=400,
                        mimetype='application/json')

    if not data.get('first_name') or not data.get('last_name') or not data.get('password_hash') or not data.get('education_level') or not data.get('account_type'):
        return Response(response=json.dumps({'error': 'Missing data'}),
                        status=400,
                        mimetype='application/json')

    g.user.first_name = data.get('first_name')
    g.user.last_name = data.get('last_name')
    g.user.password_hash = data.get('password_hash')
    g.user.education_level = data.get('education_level')
    g.user.account_type = data.get('account_type')
    g.user.updated_at = datetime.now()
    db.session.commit()

    return Response(
        response=json.dumps({'success': 'User data  updated',
                             'user': g.user.to_json()}),
        status=200,
        mimetype='application/json')


@user_ep.route("/delete", methods=["DELETE"])
def delete_user():
    if request.method != 'DELETE':
        return Response(status=405)

    if g.user is None:
        return Response(status=401)

    if g.user.account_type != 'admin':
        return Response(response=json.dumps({'error': 'Not authorized'}),
                        status=401,
                        mimetype='application/json')

    db.session.delete(g.user)
    db.commit()
    g.user = None
    return Response(response=json.dumps({'success': 'User deleted'}),
                    status=200,
                    mimetype='application/json')
