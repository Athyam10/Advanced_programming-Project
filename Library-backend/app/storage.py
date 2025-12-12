# app/storage.py
import json
import os


STORAGE_FILE = "library.json"

_data = {}
_next_id = 1

# --------------------
# Internal helpers
# --------------------

def _load_from_disk():
    global _data, _next_id
    if not os.path.exists(STORAGE_FILE):
        _data = {}
        _next_id = 1
        return

    try:
        with open(STORAGE_FILE, "r") as f:
            raw = json.load(f)
        _data = raw.get("data", {})
        _next_id = raw.get("next_id", 1)
    except Exception:
        _data = {}
        _next_id = 1


def _save_to_disk():
    with open(STORAGE_FILE, "w") as f:
        json.dump({"data": _data, "next_id": _next_id}, f, indent=2)


# --------------------
# Storage API  
# --------------------

def get_items(name=None, item_type=None):
    """
    Return list of all items.
    Optional exact name match or type filter.
    """
    items = list(_data.values())

    if name:
        items = [item for item in items if item["title"].lower() == name.lower()]
    if item_type:
        items = [item for item in items if item["item_type"].lower() == item_type.lower()]

    return items


def get_item(item_id):
    return _data.get(item_id)


def add_item(data):
    """Create a new item."""
    global _next_id

    item = {
        "id": _next_id,
        "title": data.get("title", ""),
        "item_type": data.get("item_type", ""),
        "author_or_director": data.get("author_or_director"),
        "is_available": data.get("is_available", True),
        "expected_available_date": data.get("expected_available_date"),
    }

    _data[_next_id] = item
    _next_id += 1
    _save_to_disk()

    return item


def update_item(item_id, data):
    """Update an existing item."""
    if item_id not in _data:
        return None

    item = _data[item_id]

    for key in ["title", "item_type", "author_or_director", "is_available", "expected_available_date"]:
        if key in data:
            item[key] = data[key]

    _save_to_disk()
    return item


def delete_item(item_id):
    """Delete item by ID."""
    if item_id not in _data:
        return False
    del _data[item_id]
    _save_to_disk()
    return True


# Load data initially
_load_from_disk()
