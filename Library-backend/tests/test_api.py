# tests/test_api.py
import sys, os
# ensure backend folder on sys.path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app import create_app
...

import os
import json
import shutil
import pytest
import importlib

from app import create_app

# Path to the backend folder (adjust if your structure differs)
HERE = os.path.dirname(os.path.dirname(__file__))  # Project/Library-backend/tests -> Project/Library-backend
STORAGE_FILE_PATH = os.path.join(HERE, "library.json")


@pytest.fixture
def app():
    """
    Create Flask test app and ensure the JSON storage is reset before tests.
    Also register the API blueprint if create_app() did not.
    """
    from app import create_app

    app = create_app()
    app.config["TESTING"] = True

    # ---- Ensure blueprint is registered ----
    try:
        from app.routes import bp as api_bp
        # register only if not already present
        if "/api" not in str(app.url_map):
            app.register_blueprint(api_bp, url_prefix="/api")
    except Exception as e:
        print("Blueprint registration failed:", e)

    # ---- Reset JSON storage before tests ----
    with app.app_context():
        try:
            from app import storage as storage_mod
        except Exception:
            import app.storage as storage_mod

        # remove on-disk library.json if it exists
        try:
            if os.path.exists(STORAGE_FILE_PATH):
                os.remove(STORAGE_FILE_PATH)
        except Exception:
            pass

        # reset in-memory storage
        storage_mod._data = {}
        storage_mod._next_id = 1

    yield app

    # ---- Teardown after tests ----
    try:
        if os.path.exists(STORAGE_FILE_PATH):
            os.remove(STORAGE_FILE_PATH)
    except Exception:
        pass

@pytest.fixture
def client(app):
    return app.test_client()


def test_items_initially_empty(client):
    """GET /items should return an empty list when storage is empty"""
    res = client.get("/api/items")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert data == []


def test_create_and_get_item(client):
    """POST /items should create an item, then GET /items and GET /items/<id> should work"""
    payload = {"title": "Test Book", "item_type": "book", "author_or_director": "Author"}
    res = client.post("/api/items", json=payload)
    assert res.status_code == 201
    created = res.get_json()
    assert created["title"] == "Test Book"
    assert created["item_type"] == "book"
    assert "id" in created

    # list should include the created item
    res2 = client.get("/api/items")
    assert res2.status_code == 200
    items = res2.get_json()
    assert isinstance(items, list) and len(items) == 1
    assert items[0]["title"] == "Test Book"

    # get by id
    item_id = created["id"]
    res3 = client.get(f"/api/items/{item_id}")
    assert res3.status_code == 200
    item = res3.get_json()
    assert item["title"] == "Test Book"
    assert item["id"] == item_id


def test_search_by_exact_name_and_category_filter(client):
    """Test exact-name search (?name=...) and category filter (?type=...)"""
    # create two items
    a = {"title": "UniqueTitle", "item_type": "book"}
    b = {"title": "SomeFilm", "item_type": "film"}
    r1 = client.post("/api/items", json=a)
    assert r1.status_code == 201
    r2 = client.post("/api/items", json=b)
    assert r2.status_code == 201

    # exact-name search should return single-item list
    res = client.get("/api/items", query_string={"name": "UniqueTitle"})
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list) and len(data) == 1
    assert data[0]["title"] == "UniqueTitle"

    # type filter for 'film' should return only the film
    res2 = client.get("/api/items", query_string={"type": "film"})
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert isinstance(data2, list)
    assert all(item["item_type"] == "film" for item in data2)


def test_delete_item(client):
    """Create an item then delete it"""
    payload = {"title": "ToDelete", "item_type": "book"}
    res = client.post("/api/items", json=payload)
    assert res.status_code == 201
    created = res.get_json()
    item_id = created["id"]

    # delete
    res2 = client.delete(f"/api/items/{item_id}")
    # Some implementations return 204 No Content, some return 200 with {}. Accept either but ensure not 500.
    assert res2.status_code in (200, 204)

    # item should no longer exist
    res3 = client.get(f"/api/items/{item_id}")
    assert res3.status_code == 404


def test_update_item_put(client):
    """Test updating an item via PUT /items/<id>"""
    payload = {"title": "Updatable", "item_type": "book"}
    res = client.post("/api/items", json=payload)
    assert res.status_code == 201
    created = res.get_json()
    item_id = created["id"]

    # update title and availability
    upd = {"title": "UpdatedTitle", "is_available": False, "expected_available_date": "2025-12-31"}
    res2 = client.put(f"/api/items/{item_id}", json=upd)
    assert res2.status_code == 200
    updated = res2.get_json()
    assert updated["title"] == "UpdatedTitle"
    assert updated["is_available"] is False
    assert updated["expected_available_date"] == "2025-12-31"
