from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
from database import UserAccount, db
from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import CORS

from logs.Logger import log_access

auth_ep = Blueprint('auth_ep', __name__, url_prefix='/api/auth')
CORS(auth_ep)


@auth_ep.route('/register', methods=['POST'])
def register():
    '''
    `/api/user/register`
    Validates the payload and creates a new user account in the database.
    '''
    if request.method != 'POST':
        print('[!] Invalid request method')
        return jsonify({'error': 'Method not allowed'}), 405

    data = request.get_json()

    if not data:
        print('[!] Invalid request body')
        return jsonify({'error': 'Invalid data'}), 400

    if not data.get('email') or not data.get('password') or not data.get(
            'first_name') or not data.get('last_name') or not data.get(
                'education_level') or not data.get(
                    'profile_type') or not data.get('handle'):
        print('[!] Invalid request body')
        return jsonify({'error': 'Missing data'}), 400

    user = UserAccount.query.filter_by(email=data.get('email').lower()).first()
    if user:
        print('[!] User already exists')
        return jsonify({'error': 'User already exists'}), 400
    
    user = UserAccount.query.filter_by(
        handle=data.get('handle')).first()
    if user:
        print('[!] Vanity name already exists')
        return jsonify({'error': 'Handle already in use'}), 400

    pw_hash = bcrypt.hashpw(
        data.get('password').encode('utf-8'), bcrypt.gensalt())

    user = UserAccount(
        first_name=data.get('first_name').capitalize(),
        last_name=data.get('last_name').capitalize(),
        handle=data.get('handle').lower(),
        email=data.get('email').lower(),
        password_hash=pw_hash,
        education_level=data.get('education_level').capitalize(),
        account_type=data.get('profile_type').capitalize(),
    )
    user.created_at = datetime.now()
    user.updated_at = datetime.now()

    db.session.add(user)
    db.session.commit()

    print('[+] User created')
    return jsonify({'success': 'User created'}), 201


@auth_ep.route('/login', methods=['POST'])
def login():
    '''
    `/api/auth/login`
    Verifies payload credentials against database and returns jwt if valid
    '''
    if request.method != 'POST':
        print('[!] Invalid request method')
        return jsonify({'error': 'Method not allowed'}), 405

    data = request.get_json()
    if not data:
        print('[!] Invalid request body')
        return jsonify({'error': 'Invalid data'}), 400

    if not data.get('email') or not data.get('password'):
        print('[!] Invalid request body')
        return jsonify({'error': 'Missing data'}), 400

    user = UserAccount.query.filter_by(email=data.get('email').lower()).first()

    if not user:
        print('[!] User does not exist')
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.check_password(data.get('password')):
        print('[!] Invalid password')
        return jsonify({'error': 'Invalid credentials'}), 401

    jwt = issue_jwt(user)
    log_access(f'{user} logged in from {request.remote_addr}')

    print(f'[+] User logged in: {user}')
    return jsonify({'success': 'User logged in', 'token': jwt}), 200


def issue_jwt(user: UserAccount) -> str:
    '''Issues a json web token for uses in bearer authorization.'''
    payload = {
        'sub': f'{user.id}',
        'email': f'{user.email}',
        'exp': datetime.utcnow() + timedelta(days=1),
    }
    token = jwt.encode(payload=payload,
                       key=current_app.config['SECRET_KEY'],
                       algorithm='HS256')
    return token


def get_user_by_jwt(token) -> UserAccount or None:
    '''Returns UserAccount object if token is valid.'''
    try:
        payload = jwt.decode(token.encode('utf-8'),
                             current_app.config['SECRET_KEY'],
                             algorithms=['HS256'])

        user = UserAccount.query.get(payload['sub'])
        if user: print(f'[?] Login successful by {user} via JWT')
        return user
    except jwt.exceptions.InvalidTokenError as e:
        print('[!] JWT invalid: ', e)
        return None


def login_required(func):
    '''
    Decorator for checking if a user is logged in.
    Assigns `g.user` to the user if the token is valid.
    '''

    @wraps(func)
    def wrapped(*args, **kwargs):
        if not request.headers.get('Authorization'):
            print('[!] Missing authorization header')
            return jsonify({'error': 'Missing authorization header'}), 401
        if not request.headers.get('Authorization').startswith('Bearer '):
            print('[!] Invalid authorization header')
            return jsonify({'error': 'Invalid token format'}), 401
        token = request.headers.get('Authorization').split(' ')[1]
        user = get_user_by_jwt(token)
        if not user:
            print('[!] Invalid authorization header')
            return jsonify({'error': 'Invalid authorization header'}), 401
        g.user = user
        return func(*args, **kwargs)

    return wrapped
