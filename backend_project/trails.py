from datetime import timezone

from flask import Blueprint, g, jsonify, request

from .auth_utils import error_response, token_required
from .extensions import db
from .models import Trail

trails_bp = Blueprint("trails", __name__, url_prefix="/trails")

DIFFICULTIES = {"easy", "moderate", "hard"}


def trail_to_dict(trail):
    created_at = trail.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return {
        "id": trail.id,
        "name": trail.name,
        "location": trail.location,
        "distance_miles": trail.distance_miles,
        "difficulty": trail.difficulty,
        "notes": trail.notes,
        "priority": trail.priority,
        "created_at": created_at.isoformat(),
    }


@trails_bp.route("", methods=["POST"])
@token_required
def create_trail():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("validation_error", "request body must be JSON", 400)

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return error_response("validation_error", "name is required", 400)

    location = data.get("location")
    if location is not None and not isinstance(location, str):
        return error_response("validation_error", "location must be a string", 400)

    distance = data.get("distance_miles")
    if distance is not None and (
        isinstance(distance, bool) or not isinstance(distance, (int, float)) or distance < 0
    ):
        return error_response("validation_error", "distance_miles must be a non-negative number", 400)

    difficulty = data.get("difficulty")
    if difficulty is not None and difficulty not in DIFFICULTIES:
        return error_response("validation_error", "difficulty must be easy, moderate, or hard", 400)

    notes = data.get("notes")
    if notes is not None and not isinstance(notes, str):
        return error_response("validation_error", "notes must be a string", 400)

    priority = data.get("priority", False)
    if not isinstance(priority, bool):
        return error_response("validation_error", "priority must be true or false", 400)

    trail = Trail(
        owner_id=g.current_user.id,
        name=name.strip(),
        location=location,
        distance_miles=distance,
        difficulty=difficulty,
        notes=notes,
        priority=priority,
    )
    db.session.add(trail)
    db.session.commit()

    return jsonify(trail_to_dict(trail)), 201


@trails_bp.route("", methods=["GET"])
@token_required
def list_trails():
    trails = (
        Trail.query.filter_by(owner_id=g.current_user.id)
        .order_by(Trail.priority.desc(), Trail.created_at.desc())
        .all()
    )
    return jsonify([trail_to_dict(t) for t in trails]), 200

UPDATABLE_FIELDS = {"name", "location", "distance_miles", "difficulty", "notes", "priority"}


def get_owned_trail(trail_id):
    return Trail.query.filter_by(id=trail_id, owner_id=g.current_user.id).first()


@trails_bp.route("/<int:trail_id>", methods=["GET"])
@token_required
def get_trail(trail_id):
    trail = get_owned_trail(trail_id)
    if trail is None:
        return error_response("not_found", "trail not found", 404)
    return jsonify(trail_to_dict(trail)), 200


@trails_bp.route("/<int:trail_id>", methods=["PATCH"])
@token_required
def update_trail(trail_id):
    trail = get_owned_trail(trail_id)
    if trail is None:
        return error_response("not_found", "trail not found", 404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("validation_error", "request body must be JSON", 400)

    updates = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}
    if not updates:
        return error_response("validation_error", "no updatable fields provided", 400)

    if "name" in updates:
        name = updates["name"]
        if not isinstance(name, str) or not name.strip():
            return error_response("validation_error", "name must be a non-empty string", 400)
        trail.name = name.strip()

    if "location" in updates:
        location = updates["location"]
        if location is not None and not isinstance(location, str):
            return error_response("validation_error", "location must be a string", 400)
        trail.location = location

    if "distance_miles" in updates:
        distance = updates["distance_miles"]
        if distance is not None and (
            isinstance(distance, bool) or not isinstance(distance, (int, float)) or distance < 0
        ):
            return error_response("validation_error", "distance_miles must be a non-negative number", 400)
        trail.distance_miles = distance

    if "difficulty" in updates:
        difficulty = updates["difficulty"]
        if difficulty is not None and difficulty not in DIFFICULTIES:
            return error_response("validation_error", "difficulty must be easy, moderate, or hard", 400)
        trail.difficulty = difficulty

    if "notes" in updates:
        notes = updates["notes"]
        if notes is not None and not isinstance(notes, str):
            return error_response("validation_error", "notes must be a string", 400)
        trail.notes = notes

    if "priority" in updates:
        priority = updates["priority"]
        if not isinstance(priority, bool):
            return error_response("validation_error", "priority must be true or false", 400)
        trail.priority = priority

    db.session.commit()
    return jsonify(trail_to_dict(trail)), 200


@trails_bp.route("/<int:trail_id>", methods=["DELETE"])
@token_required
def delete_trail(trail_id):
    trail = get_owned_trail(trail_id)
    if trail is None:
        return error_response("not_found", "trail not found", 404)

    db.session.delete(trail)
    db.session.commit()
    return "", 204