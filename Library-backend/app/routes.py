# app/routes.py
from flask import Blueprint, request, jsonify
from . import storage

bp = Blueprint("api", __name__)      # <-- NAME MUST BE "api"

@bp.get("/items")
def get_items():
    """
    GET /api/items
    Optional query params:
      - name : exact-name search
      - type : filter by item type
    """
    name = request.args.get("name")
    item_type = request.args.get("type")
    items = storage.get_items(name=name, item_type=item_type)
    return jsonify(items)


@bp.post("/items")
def create_item():
    data = request.json or {}
    item = storage.add_item(data)
    return jsonify(item), 201

@bp.get("/items/<int:item_id>")
def get_item(item_id):
    item = storage.get_item(item_id)
    if not item:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item)

@bp.put("/items/<int:item_id>")
def update_item(item_id):
    data = request.json or {}
    updated = storage.update_item(item_id, data)
    if not updated:
        return jsonify({"error": "Not found"}), 404
    return jsonify(updated)

@bp.delete("/items/<int:item_id>")
def delete_item(item_id):
    ok = storage.delete_item(item_id)
    if not ok:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"status": "deleted"})
