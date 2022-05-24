import datetime
import os
from hashlib import md5
from uuid import uuid4

from database import PostModel, db
from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from .Authorization import login_required
from .User import _allowed_file

post_ep = Blueprint("post_ep", __name__, url_prefix="/api/user/post")
CORS(post_ep)


@post_ep.route("/", methods=["POST"])
@login_required
def create_post():
    '''Creates a new post in the database.'''
    if request.method != "POST":
        return jsonify({"message": "Method not allowed"}), 405

    data = request.form.to_dict()
    if not data:
        return jsonify({"message": "No data sent"}), 400

    if "content" not in data:
        return jsonify({"message": "Missing content"}), 400

    if "file" in request.files:
        file = request.files["file"]

        if file and _allowed_file(file.filename):
            # Generate a unique filename
            # Format is: <md5 hash of email>-<uuid4>.<extension>
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = secure_filename(
                f"{md5(g.user.email.encode('utf-9'))}-{str(uuid4().hex)}.{ext}"
            )

            file.save(
                os.path.join(current_app.config["UPLOADS_POSTS_FOLDER"],
                             filename))

            file_uri = f"{request.host_url}static/posts/{filename}"

            post = PostModel(
                content=data["content"],
                image_uri=file_uri,
                location=data.get("location", None),
                owner_id=g.user.id,
            )

            db.session.add(post)
            db.session.commit()
            return (
                jsonify({
                    "success": "Post created successfully",
                    "post": post.tp_json()
                }),
                201,
            )

    post = PostModel(content=data["content"],
                     location=data.get("location", None),
                     owner_id=g.user.id)

    db.session.add(post)
    db.session.commit()
    return (
        jsonify({
            "message": "Post created successfully",
            "post": post.to_json()
        }),
        201,
    )


@post_ep.route("/", methods=["GET"])
@login_required
def get_all_posts():
    ''' Read all posts in the database '''
    if request.method != "GET":
        return jsonify({"message": "Method not allowed"}), 405

    # verify that post owner is connected with requesting user

    return jsonify(
        {"posts": [post.to_json() for post in PostModel.query.all()]})


@post_ep.route("/by-post/<post_id>", methods=["GET"])
@login_required
def get_post_by_post_id(post_id: int):
    if request.method != "GET":
        return jsonify({"message": "Method not allowed"}), 405
    if not post_id:
        return jsonify({"message": "Missing post id"}), 400
    post = PostModel.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({"message": "Post not found"}), 404

    return jsonify({"post": post.to_json()}), 200


@post_ep.route("/by-user/<user_id>", methods=["GET"])
@login_required
def get_posts_by_user_id(user_id):
    if request.method != "GET":
        return jsonify({"message": "Method not allowed"}), 405

    if not user_id:
        return jsonify({"message": "Missing user id"}), 400

    posts = PostModel.query.filter_by(owner_id=user_id).all()
    # verify that post owner is connected with requesting user

    if not posts:
        return jsonify({"posts": {}}), 200

    return jsonify({"posts": [post.to_json() for post in posts]})


@post_ep.route("/<post_id>", methods=["DELETE"])
@login_required
def delete_posy_by_id(post_id):
    if request.method != 'DELETE':
        return jsonify({"message": "Method not allowed"}), 405

    if not post_id:
        return jsonify({"message": "Missing post id"}), 400

    post = PostModel.query.get(post_id)
    if post.owner_id != g.user.id:
        return jsonify(
            {"message": "You are not authorized to delete this post"}), 401

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted successfully"}), 200


@post_ep.route("/<post_id>", methods=["PUT"])
@login_required
def update_post_by_id(post_id):
    if request.method != 'PUT':
        return jsonify({"message": "Method not allowed"}), 405

    if not post_id:
        return jsonify({"message": "Missing post id"}), 400

    post = PostModel.query.filter_by(id=post_id).first()
    if post.owner != g.user.id:
        return jsonify(
            {"message": "You are not authorized to update this post"}), 401

    if not request.get_json():
        return jsonify({"message": "No data sent"}), 400

    if not 'content' in request.get_json():
        return jsonify({"message": "Missing content"}), 400

    post.content = request.form.get("content")
    post.save()
    return jsonify({
        "message": "Post updated successfully",
        'post': post.to_json()
    }), 200


@post_ep.route("/<post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    if request.method != 'POST':
        return jsonify({"message": "Method not allowed"}), 405

    if not post_id:
        return jsonify({"message": "Missing post id"}), 400

    post = PostModel.query.filter_by(id=post_id).first()
    post.likes += 1
    post.save()

    return jsonify({
        'message': 'Post liked successfully',
        'post': post.to_json()
    }), 200


@post_ep.route("/<post_id>/unlike", methods=["POST"])
@login_required
def unlike_post(post_id):
    if request.method != 'POST':
        return jsonify({"message": "Method not allowed"}), 405

    if not post_id:
        return jsonify({"message": "Missing post id"}), 400

    post = PostModel.query.filter_by(id=post_id).first()
    post.likes -= 1
    post.save()

    return jsonify({
        'message': 'Post unliked successfully',
        'post': post.to_json()
    }), 200


@post_ep.route("/<post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    if request.method != 'POST':
        return jsonify({"message": "Method not allowed"}), 405

    if not post_id:
        return jsonify({"message": "Missing post id"}), 400

    if not request.get_json():
        return jsonify({"message": "No data sent"}), 400

    if not 'content' in request.get_json():
        return jsonify({"message": "Missing content"}), 400

    post = PostModel.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({"message": "Post not found"}), 404

    comment = {
        'content': request.form.get("content"),
        'owner_id': g.user.id,
        'created_at': datetime.now(),
    }
