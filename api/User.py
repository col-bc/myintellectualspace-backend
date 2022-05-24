import os
from hashlib import md5

from database import db, UserAccount
from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from .Authorization import login_required

user_ep = Blueprint("user_ep", __name__, url_prefix="/api/user")
CORS(user_ep)


def _allowed_file(filename):
    """Checks if the file's extention is allowed."""
    return ("." in filename and filename.rsplit(".", 1)[1].lower()
            in current_app.config["ALLOWED_EXTENSIONS"])


@user_ep.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Returns the user object for the currently logged in user."""
    if request.method != "GET":
        return jsonify({"error": "Method not allowed"}), 405

    return jsonify(g.user.to_json()), 200


@user_ep.route("/handle/<handle>", methods=["GET"])
@login_required
def get_user_by_handle(handle):
    if request.method != "GET":
        return jsonify({"error": "Method not allowed"}), 405

    if not handle:
        return jsonify({"error": "Missing handle"}), 400

    user = UserAccount.query.filter_by(handle=handle).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_json()), 200


@user_ep.route("/<user_id>", methods=["GET"])
@login_required
def get_user_by_id(user_id):
    if request.method != 'GET':
        return jsonify({"error": "Method not allowed"}), 405
    if not user_id or not user_id.isdigit():
        return jsonify({"error": "Invalid user id"}), 400
    user = db.session.query(db.User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404
    #verify users are friends
    return jsonify(user.to_json()), 200


@user_ep.route("/update", methods=["POST"])
@login_required
def update_user():
    """Updates the user object for the currently logged in user."""
    if request.method != "POST":
        return jsonify({"error": "Method not allowed"}), 405

    data = request.get_json()
    if data is None:
        print("[!] No data provided")
        return jsonify({"error": "No json data"}), 400

    new_user_data = g.user.to_json()

    for key in data:
        if (key == "email" or key == "auth_token" or key == "token_expiration"
                or key == "created_at" or key == "updated_at"
                or key not in g.user.to_json().keys()):
            print(f"[!] Will not update {key} from this endpoint")
            pass
        else:
            new_user_data[key] = data[key]
    g.user.update(new_user_data)
    db.session.commit()
    return jsonify({
        "success": "User data  updated",
        "user": g.user.to_json()
    }), 200


@user_ep.route("/set-avatar", methods=["POST"])
@login_required
def get_profile_picture():
    """Uploads a profile picture for the currently logged in user."""
    if request.method != "POST":
        return jsonify({"error": "Method not allowed"}), 405
    print(request.data)

    if not "file" in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file provided"}), 400

    if file and _allowed_file(file.filename):

        # Generate a unique filename
        # Format is: <md5 hash of email>-<user_id>.<extension>
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = secure_filename(
            f"{md5(g.user.email.encode('utf-8')).hexdigest()}-{g.user.id}.{ext}"
        )

        # delete the old file if exists
        if os.path.exists(f"{filename}"):
            with open(f"{filename}.{ext}") as f:
                os.remove(file.name)

        # TODO:
        # Send file to virus total for scanning

        file.save(
            os.path.join(current_app.config["UPLOADS_AVATAR_FOLDER"],
                         filename))
        g.user.avatar_uri = f"{request.host_url}static/avatars/{filename}"
        print("[+] Profile picture updated to " + g.user.avatar_uri)
        db.session.commit()
        return (
            jsonify({
                "success": "Profile picture updated",
                "user": g.user.to_json()
            }),
            201,
        )

    return jsonify({"error": "Invalid file"}), 400


@user_ep.route("/delete-avatar", methods=["POST"])
@login_required
def delete_avatar():
    if request.method != "POST":
        return jsonify({"error": "Method not allowed"}), 405

    filename = g.user.avatar.rsplit("/", 1)[1]
    if os.path.exists(filename):
        with open(f"{current_app.config['UPLOAD_FOLDER']}/{filename}",
                  "rb") as f:
            os.remove(f.name)
            f.close()

            g.user.avatar_uri = None

            return (
                jsonify({
                    "success": "Profile picture deleted",
                    "user": g.user.to_json()
                }),
                200,
            )

    return jsonify({"error": "Profile picture not found"}), 404


@user_ep.route("/delete", methods=["DELETE"])
@login_required
def delete_user():
    if request.method != "DELETE":
        return jsonify({"error": "Method not allowed"}), 405

    db.session.delete(g.user)
    db.session.commit()
    g.user = None
    return jsonify({"success": "User deleted"}), 200
