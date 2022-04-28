from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from secrets import token_hex

db = SQLAlchemy()


class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    auth_token = db.Column(db.String(120), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    posts_ids = db.Column(db.String(120), default='[]')

    education_level = db.Column(db.String(50), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, first_name, last_name, email, password_hash, education_level, account_type
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.education_level = education_level
        self.account_type = account_type

    def __repr__(self) -> str:
        return f"<UserAccount {self.id}>"

    def __str__(self) -> str:
        return f"<UserAccount {self.id}>"

    def to_json(self) -> dict:
        '''Returns a dictionary representation of the UserAccount object.'''
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "auth_token": self.auth_token,
            "token_expiration": self.token_expiration.strftime("%Y-%m-%d %H:%M:%S"),
            "education_level": self.education_level,
            "account_type": self.account_type,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def check_password(self, hash) -> bool:
        '''Returns `True` if the provided hash matches the hash in the database.'''
        return self.password_hash == hash

    def generate_auth_token(self) -> str:
        '''Generates a hexadecimal token for the user.'''
        self.auth_token = token_hex(64)
        self.token_expiration = datetime.now() + timedelta(days=1)
        self.save()
        return self.auth_token

    def check_token(self, token) -> bool:
        '''Returns `True` if the provided token matches the token in the database and the token is not expired.'''
        return self.auth_token == token and self.token_expiration > datetime.now()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()


class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(120), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey(
        'user_account.id'), nullable=False)

    liked_by = db.Column(db.String(120), nullable=False)
    comment_ids = db.Column(db.String(120), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, title, body, owner_id, liked_by, comment_ids):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        self.liked_by = liked_by
        self.comment_ids = comment_ids
        self.created_at = datetime.now()

    def __repr__(self):
        return f"<PostModel {self.id}>"

    def __str__(self):
        return f"<PostModel {self.id}>"

    def to_json(self) -> dict:
        '''Returns a dictionary representation of the PostModel object.'''
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'owner_id': self.owner_id,
            'liked_by': self.liked_by,
            'comment_ids': self.comment_ids,
            'created_at': self.created_at
        }

    def like(self, user_id) -> None:
        '''Appends a user_id to the liked_by field.'''
        if user_id not in self.liked_by:
            self.liked_by = self.liked_by + ',' + user_id
            self.save()

    def add_comment(self, comment_id) -> None:
        '''Appends a comment_id to the comment_ids field.'''
        if comment_id not in self.comment_ids:
            self.comment_ids = self.comment_ids + ',' + comment_id
            self.save()

    def save(self) -> None:
        '''Saves the PostModel object to the database.'''
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()
