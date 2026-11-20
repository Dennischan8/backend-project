from flask import Blueprint, g, jsonify

from .auth_utils import admin_required, token_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/ping", methods=["GET"])
@token_required
@admin_required
def ping():
    return jsonify({"status": "ok", "admin": g.current_user.email}), 200