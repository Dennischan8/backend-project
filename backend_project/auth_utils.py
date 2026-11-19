from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .extensions import db
from .models import User


def error_response(error, message, status):
    return jsonify({"error": error, "message": message}), status


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        parts = request.headers.get("Authorization", "").split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return error_response("unauthorized", "missing or invalid token", 401)

        try:
            payload = jwt.decode(
                parts[1], current_app.config["JWT_SECRET"], algorithms=["HS256"]
            )
            user = db.session.get(User, int(payload["sub"]))
        except (jwt.InvalidTokenError, KeyError, ValueError):
            return error_response("unauthorized", "missing or invalid token", 401)

        if user is None:
            return error_response("unauthorized", "missing or invalid token", 401)

        g.current_user = user
        return f(*args, **kwargs)

    return wrapper