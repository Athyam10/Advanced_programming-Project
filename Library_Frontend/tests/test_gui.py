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
