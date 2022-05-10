from datetime import datetime
from flask_cors import CORS
from flask import Blueprint, request, Response, g
import json
from database import db, UserAccount
import bcrypt

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
        return Response(
            response=json.dumps({'error': 'Method not allowed'}),
            status=405,
            mimetype='application/json'
        )
    data = request.get_json()
    print(data)

    if not data:
        print('[!] Invalid request body')
        return Response(
            response=json.dumps({'error': 'Invalid data'}),
            status=400,
            mimetype='application/json'
        )

    if not data.get('email') or not data.get('password') or not data.get('first_name') or not data.get('last_name') or not data.get('education_level') or not data.get('profile_type'):
        print('[!] Invalid request body')
        return Response(
            response=json.dumps({'error': 'Missing data'}),
            status=400,
            mimetype='application/json'
        )

    user = UserAccount.query.filter_by(email=data.get('email').lower()).first()
    if user:
        print('[!] User already exists')
        return Response(
            response=json.dumps({'error': 'User already exists'}),
            status=400,
            mimetype='application/json'
        )

    pw_hash = bcrypt.hashpw(
        data.get('password').encode('utf-8'), bcrypt.gensalt())

    user = UserAccount(
        first_name=data.get('first_name').capitalize(),
        last_name=data.get('last_name').capitalize(),
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
    return Response(
        response=json.dumps({'success': 'User created'}),
        status=201,
        mimetype='application/json'
    )


@auth_ep.route('/login', methods=['POST'])
def login():
    '''
    `/api/auth/login`
    Verifies payload credentials against database and returns token if valid
    '''
    if request.method != 'POST':
        print('[!] Invalid request method')
        return Response(
            response=json.dumps({'error': 'Method not allowed'}),
            status=405,
            mimetype='application/json'
        )
    data = request.get_json()

    if not data:
        print('[!] Invalid request body')
        return Response(
            response=json.dumps({'error': 'Invalid data'}),
            status=400,
            mimetype='application/json'
        )

    if not data.get('email') or not data.get('password'):
        print('[!] Invalid request body')
        return Response(
            response=json.dumps({'error': 'Missing data'}),
            status=400,
            mimetype='application/json'
        )

    user = UserAccount.query.filter_by(email=data.get('email').lower()).first()

    if not user:
        print('[!] User does not exist')
        return Response(
            response=json.dumps({'error': 'Invalid credentials'}),
            status=401,
            mimetype='application/json'
        )

    if not user.check_password(data.get('password')):
        print('[!] Invalid password')
        return Response(
            response=json.dumps({'error': 'Invalid credentials'}),
            status=401,
            mimetype='application/json'
        )

    user.auth_token = user.generate_auth_token()

    print(f'[+] User logged in: {user}')
    return Response(
        response=json.dumps(
            {'success': 'User logged in', 'token': user.auth_token}),
        status=200,
        mimetype='application/json'
    )


def get_user_by_token(token) -> UserAccount:
    user = UserAccount.query.filter_by(auth_token=token).first()
    if not user:
        print('[!] Invalid token')
        return None
    if user.check_token(token):
        print(
            f'[+] Access granted via token: {user} <Token ...{token[-5:]}>')
        return user
    else:
        return None
