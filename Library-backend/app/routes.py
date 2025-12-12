# app/routes.py
from flask import Blueprint, request, jsonify, abort
from datetime import datetime
from . import create_app  # if needed elsewhere
from .storage import list_items, find_by_name_exact, get_item, create_item, update_item, delete_item

bp = Blueprint("api", __name__)

@bp.route('/items', methods=['GET'])
def all_items():
    """
    Query params supported:
      - type: filter by item_type (exact match)
      - available: 'true' or 'false' to filter by availability
      - name: exact name match (if present, return the single item as list)
    """
    name = request.args.get("name")
    if name:
        item = find_by_name_exact(name)
        if not item:
            return jsonify([])  # assignment asks to display if found (exact match) - return empty list if not found
        return jsonify([item])

    type_filter = request.args.get("type")
    available = request.args.get("available")
    available_bool = None
    if available is not None:
        if available.lower() in ("true", "1"):
            available_bool = True
        else:
            available_bool = False

    items = list_items(only_available=available_bool, type_filter=type_filter)
    return jsonify(items)

@bp.route('/items/<int:item_id>', methods=['GET'])
def get_single(item_id):
    item = get_item(item_id)
    if not item:
        abort(404)
    return jsonify(item)

@bp.route('/items', methods=['POST'])
def create_new():
    data = request.get_json() or {}
    title = data.get("title")
    item_type = data.get("item_type")
    if not title or not item_type:
        return jsonify({"message": "title and item_type are required"}), 400

    # optional fields
    author = data.get("author_or_director")
    is_available = bool(data.get("is_available", True))
    exp = data.get("expected_available_date")
    # validate expected date format (YYYY-MM-DD) if provided
    if exp:
        try:
            _ = datetime.fromisoformat(exp).date()
        except Exception:
            return jsonify({"message": "expected_available_date must be YYYY-MM-DD"}), 400

    payload = {
        "title": title,
        "item_type": item_type,
        "author_or_director": author,
        "is_available": is_available,
        "expected_available_date": exp or None
    }
    item = create_item(payload)
    return jsonify(item), 201

@bp.route('/items/<int:item_id>', methods=['PUT'])
def update_existing(item_id):
    data = request.get_json() or {}
    # validate expected_available_date format if present
    exp_date = data.get("expected_available_date")
    if exp_date:
        try:
            _ = datetime.fromisoformat(exp_date).date()
        except Exception:
            return jsonify({"message": "expected_available_date must be YYYY-MM-DD"}), 400

    updated = update_item(item_id, data)
    if not updated:
        abort(404)
    return jsonify(updated)

@bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_existing(item_id):
    ok = delete_item(item_id)
    if not ok:
        abort(404)
    # return 204 No Content to match assignment style
    return jsonify({}), 204
