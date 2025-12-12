# app/storage.py
import json
import os
from threading import Lock
from typing import Dict, Any, List, Optional

# Path for the JSON file (relative to the app root)
STORAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "library.json")
STORAGE_FILE = os.path.abspath(STORAGE_FILE)

_lock = Lock()
_data: Dict[int, Dict[str, Any]] = {}
_next_id = 1

def _load_from_disk():
    global _data, _next_id
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # raw expected as dict of string-id -> item
            _data = {int(k): v for k, v in raw.items()}
            if _data:
                _next_id = max(_data.keys()) + 1
            else:
                _next_id = 1
        except Exception:
            # if file corrupt or unreadable, start fresh
            _data = {}
            _next_id = 1
    else:
        _data = {}
        _next_id = 1

def _save_to_disk():
    # atomic-ish write
    tmp = STORAGE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in _data.items()}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STORAGE_FILE)

# initialize on import
_load_from_disk()

def list_items(only_available: Optional[bool] = None, type_filter: Optional[str] = None) -> List[Dict]:
    """Return list of items optionally filtered by availability and type."""
    res = list(_data.values())
    if only_available is not None:
        res = [i for i in res if bool(i.get("is_available", True)) == bool(only_available)]
    if type_filter:
        res = [i for i in res if i.get("item_type") == type_filter]
    return res

def find_by_name_exact(name: str) -> Optional[Dict]:
    for item in _data.values():
        if item.get("title") == name:
            return item
    return None

def get_item(item_id: int) -> Optional[Dict]:
    return _data.get(item_id)

def create_item(payload: Dict) -> Dict:
    global _next_id
    with _lock:
        item_id = _next_id
        _next_id += 1
        # standardize the stored object
        item = {
            "id": item_id,
            "title": payload.get("title"),
            "item_type": payload.get("item_type"),
            "author_or_director": payload.get("author_or_director"),
            "is_available": bool(payload.get("is_available", True)),
            "expected_available_date": payload.get("expected_available_date") or None,
            # you can add more fields like published_date/isbn/description
        }
        _data[item_id] = item
        _save_to_disk()
        return item

def update_item(item_id: int, payload: Dict) -> Optional[Dict]:
    with _lock:
        if item_id not in _data:
            return None
        item = _data[item_id]
        for k, v in payload.items():
            # whitelist allowed fields
            if k in ("title", "item_type", "author_or_director",
                     "is_available", "expected_available_date"):
                # cast booleans correctly
                if k == "is_available":
                    item[k] = bool(v)
                else:
                    item[k] = v
        # if set available true, clear expected date
        if item.get("is_available"):
            item["expected_available_date"] = None
        _save_to_disk()
        return item

def delete_item(item_id: int) -> bool:
    with _lock:
        if item_id in _data:
            del _data[item_id]
            _save_to_disk()
            return True
        return False
