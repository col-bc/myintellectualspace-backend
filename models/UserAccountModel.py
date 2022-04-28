from app import db
from secrets import token_hex
from datetime import datetime, timedelta

"""
UserAccountModel is a class that defines the structure of the user account table in the database.

Methods:
    to_json() -> dict
        Returns a dictionary representation of the UserAccountModel object.
        
    check_password(hash) -> bool 
        Returns True if the passed hash matches the database hash.
        
    generate_auth_token(user_id) -> str
        Generates a JWT token for the user.
    
    token_is_valid(token) -> bool
        Returns True if the token matches the token in the database and the token is not expired.
        
    save() -> None
        Saves the UserAccountModel object to the database.
    
"""


class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    auth_token = db.Column(db.String(120), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
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
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "auth_token": self.auth_token,
            "token_expiration": self.token_expiration,
            "education_level": self.education_level,
            "account_type": self.account_type,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def check_password(self, hash) -> bool:
        return self.password_hash == hash

    def generate_auth_token(self) -> str:
        self.auth_token = token_hex(64)
        self.token_expiration = datetime.now() + timedelta(days=1)
        self.save()
        return self.auth_token

    def isTokenValid(self, token) -> bool:
        return self.auth_token == token and self.token_expiration > datetime.now()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()
