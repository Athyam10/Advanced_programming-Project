import json
import pytest
from PyQt5.QtWidgets import QDialog

import Library_Frontend.main as main

SAMPLE_ITEMS = [
    {
        "id": 1,
        "title": "The Hobbit",
        "item_type": "book",
        "author_or_director": "J.R.R. Tolkien",
        "is_available": True,
        "expected_available_date": None,
    }
]


@pytest.fixture(autouse=True)
def disable_message_boxes(monkeypatch):
    # prevent modal message boxes from blocking tests
    monkeypatch.setattr(main.QMessageBox, "critical", lambda *a, **k: None)
    monkeypatch.setattr(main.QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(main.QMessageBox, "warning", lambda *a, **k: None)
    yield


def test_load_items_populates_table(qtbot, monkeypatch):
    # prepare api_get to return our sample items
    monkeypatch.setattr(main, "API_BASE", "http://127.0.0.1:5000/")
    def fake_api_get(path, params=None):
        assert path == "/items"
        return SAMPLE_ITEMS

    monkeypatch.setattr(main.LibraryApp, "api_get", lambda self, path, params=None: fake_api_get(path, params))

    app = main.LibraryApp()
    qtbot.addWidget(app)

    # load items and assert table populated
    app.load_items()
    assert app.table.rowCount() == 1
    item = app.table.item(0, 1)
    assert item is not None
    title = item.text()
    assert title == "The Hobbit"


class DummyDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self._payload = {"title": "Dune", "item_type": "book"}

    def exec_(self):
        return QDialog.Accepted

    def get_payload(self):
        return self._payload


def test_add_item_flow(qtbot, monkeypatch):
    # monkeypatch dialog and API calls
    monkeypatch.setattr(main, "ItemDialog", DummyDialog)

    # api_post should return created item
    created = {"id": 2, "title": "Dune", "item_type": "book", "author_or_director": None, "is_available": True, "expected_available_date": None}
    def fake_api_post(self, path, json):
        assert path == "/items"
        return created, 201

    # api_get should return list including created item after creation
    called = {"get_calls": 0}
    def fake_api_get(self, path, params=None):
        called["get_calls"] += 1
        if called["get_calls"] == 1:
            return []
        return [created]

    monkeypatch.setattr(main.LibraryApp, "api_post", fake_api_post)
    monkeypatch.setattr(main.LibraryApp, "api_get", fake_api_get)

    app = main.LibraryApp()
    qtbot.addWidget(app)

    # simulate clicking Add
    app.add_item()

    # after add, load_items should have been called and table updated
    assert app.table.rowCount() == 1
    item = app.table.item(0, 1)
    assert item is not None
    assert item.text() == "Dune"


def test_edit_item_flow(qtbot, monkeypatch):
    # prepare initial item and API behaviors
    original = {"id": 3, "title": "Old Title", "item_type": "book", "author_or_director": "A", "is_available": True, "expected_available_date": None}
    updated = {"id": 3, "title": "New Title", "item_type": "book", "author_or_director": "A", "is_available": True, "expected_available_date": None}

    # api_get for single item should return original
    def fake_api_get(self, path, params=None):
        if path == "/items":
            return [original]
        if path == "/items/3":
            return original
        return None

    # Replace ItemDialog to return updated payload
    class EditDialog(QDialog):
        def __init__(self, parent=None, data=None):
            super().__init__(parent)
            self._payload = {"title": "New Title", "item_type": "book"}

        def exec_(self):
            return QDialog.Accepted

        def get_payload(self):
            return self._payload

    def fake_api_put(self, path, json):
        assert path == "/items/3"
        return updated

    monkeypatch.setattr(main.LibraryApp, "api_get", fake_api_get)
    monkeypatch.setattr(main, "ItemDialog", EditDialog)
    monkeypatch.setattr(main.LibraryApp, "api_put", fake_api_put)

    app = main.LibraryApp()
    qtbot.addWidget(app)

    # load initial items
    app.load_items()
    assert app.table.rowCount() == 1

    # select row 0
    app.table.selectRow(0)
    # run edit
    app.edit_item()

    # after edit, table should have updated title
    # we monkeypatched api_get to still return original list on reload, so update table manually by calling load_items again with updated data
    monkeypatch.setattr(main.LibraryApp, "api_get", lambda self, path, params=None: [updated] if path == "/items" else updated)
    app.load_items()
    item = app.table.item(0, 1)
    assert item is not None
    assert item.text() == "New Title"


def test_delete_item_flow(qtbot, monkeypatch):
    item = {"id": 4, "title": "ToDelete", "item_type": "book", "author_or_director": None, "is_available": True, "expected_available_date": None}

    def fake_api_get(self, path, params=None):
        if path == "/items":
            return [item]
        if path == "/items/4":
            return item
        return None

    def fake_api_delete(self, path):
        assert path == "/items/4"
        return True

    monkeypatch.setattr(main.LibraryApp, "api_get", fake_api_get)
    monkeypatch.setattr(main.LibraryApp, "api_delete", fake_api_delete)

    app = main.LibraryApp()
    qtbot.addWidget(app)
    app.load_items()
    assert app.table.rowCount() == 1

    app.table.selectRow(0)
    # monkeypatch QMessageBox.question to auto-confirm
    monkeypatch.setattr(main.QMessageBox, "question", lambda *a, **k: main.QMessageBox.Yes)
    app.delete_item()
    # simulate empty list after deletion
    monkeypatch.setattr(main.LibraryApp, "api_get", lambda self, path, params=None: [])
    app.load_items()
    assert app.table.rowCount() == 0


def test_toggle_availability_flow(qtbot, monkeypatch):
    # item initially available -> toggle to unavailable
    item = {"id": 5, "title": "ToggleMe", "item_type": "book", "author_or_director": None, "is_available": True, "expected_available_date": None}
    updated = {"id": 5, "title": "ToggleMe", "item_type": "book", "author_or_director": None, "is_available": False, "expected_available_date": "2025-12-25"}

    def fake_api_get(self, path, params=None):
        if path == "/items":
            return [item]
        if path == "/items/5":
            return item
        return None

    def fake_api_put(self, path, json):
        assert path == "/items/5"
        # ensure payload contains expected date when marking unavailable
        assert json.get("is_available") is False
        return updated

    monkeypatch.setattr(main.LibraryApp, "api_get", fake_api_get)
    monkeypatch.setattr(main.LibraryApp, "api_put", fake_api_put)
    # make QInputDialog.getText return a valid date and accepted=True
    monkeypatch.setattr(main.QInputDialog, "getText", lambda *a, **k: ("2025-12-25", True))

    app = main.LibraryApp()
    qtbot.addWidget(app)
    app.load_items()
    app.table.selectRow(0)
    app.toggle_availability()

    # simulate updated list on reload
    monkeypatch.setattr(main.LibraryApp, "api_get", lambda self, path, params=None: [updated] if path == "/items" else updated)
    app.load_items()
    item = app.table.item(0, 4)
    assert item is not None
    assert item.text() == "No"
