from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from secrets import token_hex
from bcrypt import checkpw

db = SQLAlchemy()


class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    occupation = db.Column(db.String(50), nullable=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    auth_token = db.Column(db.String(120), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    bio = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(120), nullable=True)

    posts_ids = db.Column(db.String(120), default='[]')
    comment_ids = db.Column(db.String(120), default='[]')
    interests = db.Column(db.String(120), default='[]')
    friend_ids = db.Column(db.String(120), default='[]')

    # public, private, and friends
    privacy_setting = db.Column(db.String(120), default='public')

    education_level = db.Column(db.String(50), nullable=False)

    # Employer fields
    organization_name = db.Column(db.String(120), nullable=True)
    years_in_business = db.Column(db.String(2), nullable=True)

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
            "bio": self.bio,
            "website": self.website,
            "posts_ids": self.posts_ids,
            "comment_ids": self.comment_ids,
            "interests": self.interests,
            "friend_ids": self.friend_ids,
            "privacy_setting": self.privacy_setting,
            "education_level": self.education_level,
            "organization_name": self.organization_name,
            "years_in_business": self.years_in_business,
            "account_type": self.account_type,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "auth_token": self.auth_token,
            "token_expiration": self.token_expiration.strftime("%Y-%m-%d %H:%M:%S"),
            "occupation": self.occupation
        }

    def update(self, data: dict):
        '''Updates the UserAccount object with the provided data.'''
        for key, value in data.items():
            if key == "password_hash":
                self.password_hash = value
            elif key == "bio":
                self.bio = value
            elif key == "website":
                self.website = value
            elif key == "interests":
                self.interests = value
            elif key == "privacy_setting":
                self.privacy_setting = value
            elif key == "education_level":
                self.education_level = value
            elif key == "organization_name":
                self.organization_name = value
            elif key == "years_in_business":
                self.years_in_business = value
            elif key == "account_type":
                self.account_type = value
            elif key == "occupation":
                self.occupation = value
            elif key == "first_name":
                self.first_name = value
            elif key == "last_name":
                self.last_name = value
        db.session.commit()
        return

    def check_password(self, hash) -> bool:
        '''Returns `True` if the provided password hash matches the password hash in the database.'''
        return checkpw(hash.encode('utf-8'), self.password_hash.encode('utf-8'))

    def generate_auth_token(self) -> str:
        '''Generates a hexadecimal token for the user.'''
        self.auth_token = token_hex(64)
        self.token_expiration = datetime.now() + timedelta(days=1)
        self.save()
        return self.auth_token

    def check_token(self, token) -> bool:
        '''Returns `True` if the provided token matches the token in the database and the token is not expired.'''
        return self.auth_token == token and self.token_expiration > datetime.now()

    def add_friend(self, friend_id):
        '''Adds a friend to the list of friends.'''
        if friend_id not in self.friend_ids:
            self.friend_ids.append(friend_id)
            self.save()

    def remove_friend(self, friend_id):
        '''Removes a friend from the list of friends.'''
        if friend_id in self.friend_ids:
            self.friend_ids.remove(friend_id)
            self.save()

    def is_friend(self, friend_id):
        '''Returns `True` if the user is friends with the provided user id.'''
        return friend_id in self.friend_ids

    def shares_interest(self, interest):
        '''Returns `True` if the user shares an interest with the provided interest.'''
        return interest in self.interests

    def add_interest(self, interest):
        '''Adds an interest to the list of interests.'''
        if interest not in self.interests:
            self.interests.append(interest)
            self.save()

    def remove_interest(self, interest):
        '''Removes an interest from the list of interests.'''
        if interest in self.interests:
            self.interests.remove(interest)
            self.save()

    def add_post(self, post_id):
        '''Adds a post to the list of posts.'''
        if post_id not in self.posts_ids:
            self.posts_ids.append(post_id)
            self.save()

    def remove_post(self, post_id):
        '''Removes a post from the list of posts.'''
        if post_id in self.posts_ids:
            self.posts_ids.remove(post_id)
            self.save()

    def add_comment(self, comment_id):
        '''Adds a comment to the list of comments.'''
        if comment_id not in self.comment_ids:
            self.comment_ids.append(comment_id)
            self.save()

    def remove_comment(self, comment_id):
        '''Removes a comment from the list of comments.'''
        if comment_id in self.comment_ids:
            self.comment_ids.remove(comment_id)
            self.save()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
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

    def get_user(self) -> UserAccount:
        return UserAccount.query.get(self.owner_id)

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
