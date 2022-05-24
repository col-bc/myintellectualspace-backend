import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate

from database import db
from api.Authorization import auth_ep
from api.User import user_ep
from api.Post import post_ep
from api.Meetings import meetings_ep

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'three blind mice and a giant red riding hood'

# Database settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config[
    "SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{os.path.join(os.getcwd(), "database.sqlite")}'

# Uploads settings
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOADS_AVATAR_FOLDER'] = os.path.join(os.getcwd(),
                                                   "static/avatars")
app.config['UPLOADS_POSTS_FOLDER'] = os.path.join(os.getcwd(), "static/posts")

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors.init_app(app)

db.init_app(app)
migrate = Migrate(app, db)


@app.before_first_request
def handle_preflight():
    if request.method == 'OPTIONS':
        return jsonify('ok'), 204


def register_blueprints(app):
    app.register_blueprint(auth_ep)
    app.register_blueprint(user_ep)
    app.register_blueprint(post_ep)
    app.register_blueprint(meetings_ep)


def setup_database(app):
    with app.app_context():
        db.init_app(app)
        if not os.path.exists(os.path.join(os.getcwd(), "database.db")):
            print("[+] Creating database tables.")
            db.create_all()


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_APP'] = 'app.py'
    register_blueprints(app)
    setup_database(app)
    app.run()
