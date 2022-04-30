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

    if 'Authorization' not in request.headers:
        return Response(status=401)

    token = request.headers['Authorization'].split(' ')[1]
    user = get_user_by_token(token)

    if user is None:
        g.user = None
        return Response(response=json.dumps({'error': 'Invalid token'}),
                        status=401,
                        mimetype='application/json')

    g.user = user
    return 


@user_ep.route("/", methods=["GET"])
def get_user():
    '''Returns the user object for the currently logged in user.'''
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
    '''Updates the user object for the currently logged in user.'''
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

    for key in data:
        if key != 'email' and key not in g.user.to_json().keys():
            return Response(response=json.dumps({'error': 'Invalid field'}),
                            status=400,
                            mimetype='application/json')

    g.user.update(data)

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


@user_ep.route("/tasks", methods=["GET"])
def get_outstanding_tasks():
    if request.method != 'GET':
        return Response(status=405)

    if g.user is None:
        return Response(status=401)

    if g.user.account_type != 'admin':
        return Response(response=json.dumps({'error': 'Not authorized'}),
                        status=401,
                        mimetype='application/json')

    tasks = ['interests', 'bio', 'friends', 'posts', 'comments', 'likes']
    outstanding_tasks = []
    if g.user.interests is None:
        outstanding_tasks.append('interests')
    if g.user.bio is None:
        outstanding_tasks.append('bio')
    if g.user.friend_its is None:
        outstanding_tasks.append('friends')
    if g.user.post_ids is None:
        outstanding_tasks.append('posts')
    if g.user.comment_ids is None:
        outstanding_tasks.append('comments')
    if g.user.like_ids is None:
        outstanding_tasks.append('likes')
    if outstanding_tasks:
        return Response(response=json.dumps({'outstanding_tasks': outstanding_tasks}),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=json.dumps({'outstanding_tasks': []}),
                        status=200,
                        mimetype='application/json')
