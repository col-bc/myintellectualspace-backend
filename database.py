import json
import jwt
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from bcrypt import checkpw

db = SQLAlchemy()


class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    avatar_uri = db.Column(db.String(256), nullable=True, default=None)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    handle = db.Column(db.String(50), nullable=False, default=None)

    occupation = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    reset_token = db.Column(db.String(120), unique=True, nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(50), nullable=True)

    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(120), nullable=True)

    posts_ids = db.Column(db.Text, default='[]')
    interests = db.Column(db.String(120), default='[]')
    friend_ids = db.Column(db.String(120), default='[]')

    # public, private, and friends
    privacy_setting = db.Column(db.String(120), default='public')

    education_level = db.Column(db.String(50), nullable=False)
    education_major = db.Column(db.String(50), nullable=True)
    education_institution = db.Column(db.String(50), nullable=True)

    # Employer fields
    organization_name = db.Column(db.String(120), nullable=True)
    years_in_business = db.Column(db.String(2), nullable=True)

    account_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        first_name,
        last_name,
        handle,
        email,
        password_hash,
        education_level,
        account_type,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.handle = handle
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
            'id': self.id,
            'avatar_uri': self.avatar_uri,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'handle': self.handle,
            'occupation': self.occupation,
            'email': self.email,
            'reset_token': self.reset_token,
            'reset_token_expiration': self.reset_token_expiration,
            'location': self.location,
            'bio': self.bio,
            'website': self.website,
            'posts_ids': self.posts_ids,
            'interests': self.interests,
            'friend_ids': self.friend_ids,
            'privacy_setting': self.privacy_setting,
            'education_level': self.education_level,
            'education_major': self.education_major,
            'education_institution': self.education_institution,
            'organization_name': self.organization_name,
            'years_in_business': self.years_in_business,
            'account_type': self.account_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def update(self, data: dict):
        '''Updates the UserAccount object with the provided data.'''
        for key, value in data.items():
            if key == 'created_at':
                self.created_at = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif key == 'updated_at':
                self.updated_at = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                setattr(self, key, value)
        db.session.commit()
        return

    def check_password(self, hash) -> bool:
        '''Returns `True` if the provided password hash matches the password hash in the database.'''
        return checkpw(hash.encode('utf-8'), self.password_hash)

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

    content = db.Column(db.String(120), nullable=False)

    location = db.Column(db.String(120), nullable=True)
    image_uri = db.Column(db.String(120), nullable=True)

    owner_id = db.Column(db.Integer,
                         db.ForeignKey('user_account.id'),
                         nullable=False)

    liked_by = db.Column(db.Text, nullable=False, default='[]')
    comments = db.Column(db.JSON, nullable=False, default='{}')

    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, content, owner_id, location=None, image_uri=None):
        self.content = content
        self.owner_id = owner_id
        self.location = location
        self.image_uri = image_uri
        self.created_at = datetime.now()

    def __repr__(self):
        return f"<PostModel {self.id}>"

    def __str__(self):
        return f"<PostModel {self.id}>"

    def to_json(self) -> dict:
        '''Returns a dictionary representation of the PostModel object.'''
        return {
            'id':
            self.id,
            'content':
            self.content,
            'location':
            self.location,
            'image_uri':
            self.image_uri,
            'owner_id':
            self.owner_id,
            'owner_avatar':
            UserAccount.query.get(self.owner_id).avatar_uri,
            'owner_name':
            UserAccount.query.get(self.owner_id).first_name + ' ' +
            UserAccount.query.get(self.owner_id).last_name,
            'owner_handle':
            UserAccount.query.get(self.owner_id).handle,
            'liked_by':
            self.liked_by,
            'comments':
            self.comments,
            'created_at':
            self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def get_user(self) -> UserAccount:
        return UserAccount.query.get(self.owner_id)

    def like(self, user_id) -> None:
        '''Appends a user_id to the liked_by field.'''
        if user_id not in self.liked_by:
            self.liked_by = self.liked_by + ',' + user_id
            self.save()

    def add_comment(self, user_id: int, comment: str) -> None:
        '''Appends a json object to the comments field.'''
        self.comments = self.comments + ',' + json.dumps({
            'user_id': user_id,
            'comment': comment,
        })
        self.save()

    def save(self) -> None:
        '''Saves the current PostModel object (`self`) to the database.'''
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        '''Deletes the current PostModel object (`self`) from the database.'''
        db.session.delete(self)
        db.session.commit()
