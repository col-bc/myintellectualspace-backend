import os

from database import db
from flask import Flask

from flask_cors import CORS

from endpoints.AuthEndpoint import auth_ep
from endpoints.UserEndpoint import user_ep


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/colby/Code/myintellectualspace-back/database.db'
    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    db.init_app(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    cors.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_ep)
    app.register_blueprint(user_ep)


def setup_database(app):
    with app.app_context():
        print('[+] Creating database tables...') 
        db.create_all()


if __name__ == '__main__':
    app = create_app()
    setup_database(app)
    app.run()
