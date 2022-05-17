from datetime import datetime

import bcrypt
from database import UserAccount, db
from flask import Blueprint, g, jsonify, request
from flask_cors import CORS

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
    print(data)

    if not data:
        print('[!] Invalid request body')
        return jsonify({'error': 'Invalid data'}),400

    if not data.get('email') or not data.get('password') or not data.get('first_name') or not data.get('last_name') or not data.get('education_level') or not data.get('profile_type'):
        print('[!] Invalid request body')
        return jsonify({'error': 'Missing data'}), 400

    user = UserAccount.query.filter_by(email=data.get('email').lower()).first()
    if user:
        print('[!] User already exists')
        return jsonify({'error': 'User already exists'}), 400

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
    return jsonify({'success': 'User created'}), 201


@auth_ep.route('/login', methods=['POST'])
def login():
    '''
    `/api/auth/login`
    Verifies payload credentials against database and returns token if valid
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

    user.auth_token = user.generate_auth_token()

    print(f'[+] User logged in: {user}')
    return jsonify({'success': 'User logged in', 'token': user.auth_token}), 200


@auth_ep.route('/logout', methods=['POST'])
def logout():
    '''
    `/api/auth/logout`
    Clears token from database
    '''
    if request.method != 'POST':
        return jsonify({'message': 'Method not allowed'}), 405
    
    if not 'Authorization' in request.headers:
        return jsonify({'message': 'Authorization is missing.'}), 401
    token = request.headers['Authorization'].split(' ')[1]
    if not token:
        return jsonify({'message': 'Token is missing'}), 401
    
    user = UserAccount.query.filter_by(token=token).first()
    if not user:
        return jsonify({'message': 'Invalid token'}), 401
    user.auth_token = None
    user.token_expiration = None
    return jsonify({'message': 'Logged out'}), 200


def get_user_by_token(token) -> UserAccount:
    '''
    @params token: str
    @returns UserAccount
    Gets user account object from token
    '''
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
