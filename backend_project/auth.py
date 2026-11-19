from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, current_app, jsonify, request

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def error_response(error, message, status):
    return jsonify({"error": error, "message": message}), status


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("validation_error", "request body must be JSON", 400)

    email = data.get("email")
    password = data.get("password")

    if email is None or (isinstance(email, str) and not email.strip()):
        return error_response("validation_error", "email is required", 400)

    if password is None or (isinstance(password, str) and not password):
        return error_response("validation_error", "password is required", 400)

    if not isinstance(email, str) or "@" not in email:
        return error_response("validation_error", "email must be a valid email address", 400)

    if not isinstance(password, str) or len(password) < 8:
        return error_response("validation_error", "password must be at least 8 characters", 400)

    email = email.strip().lower()

    if User.query.filter_by(email=email).first():
        return error_response("validation_error", "email already taken", 409)

    user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response("validation_error", "email already taken", 409)

    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": created_at.isoformat(),
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("validation_error", "request body must be JSON", 400)

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not email.strip() or not isinstance(password, str) or not password:
        return error_response("validation_error", "email and password are required", 400)

    user = User.query.filter_by(email=email.strip().lower()).first()

    if user is None or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    secret = current_app.config["JWT_SECRET"]
    lifetime = current_app.config["JWT_LIFETIME_SECONDS"]
    exp = datetime.now(timezone.utc) + timedelta(seconds=lifetime)

    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": exp,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify({"access_token": token}), 200