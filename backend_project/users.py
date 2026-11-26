from datetime import timezone

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from .auth_utils import error_response, token_required
from .extensions import db
from .models import User

users_bp = Blueprint("users", __name__, url_prefix="/auth")

UPDATABLE_FIELDS = {"email"}


def profile_dict(user):
    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "created_at": created_at.isoformat(),
    }


@users_bp.route("/me", methods=["GET"])
@token_required
def me():
    return jsonify(profile_dict(g.current_user)), 200


@users_bp.route("/me", methods=["PATCH"])
@token_required
def update_me():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("validation_error", "request body must be JSON", 400)

    updates = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}
    if not updates:
        return error_response("validation_error", "no updatable fields provided", 400)

    user = g.current_user

    if "email" in updates:
        email = updates["email"]
        if not isinstance(email, str) or not email.strip() or "@" not in email:
            return error_response("validation_error", "email must be a valid email address", 400)

        email = email.strip().lower()

        if email != user.email:
            existing = User.query.filter(User.email == email, User.id != user.id).first()
            if existing:
                return error_response("validation_error", "email already taken", 409)
            user.email = email

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response("validation_error", "email already taken", 409)

    return jsonify(profile_dict(user)), 200