"""
Library Manager Frontend (PyQt)
Features:
- List items from /api/items
- Add new item (POST /api/items)
- Edit item (PUT /api/items/<id>)
- Delete item (DELETE /api/items/<id>)
- Toggle availability and set expected_available_date
"""

import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QCheckBox, QFormLayout,
    QInputDialog
)
from PyQt5.QtCore import Qt, QDate
from dateutil import parser as dateparser

API_BASE = "http://127.0.0.1:5000/"  # change if needed


def iso_date_or_none(qdate: QDate):
    if not qdate.isValid():
        return None
    return qdate.toString("yyyy-MM-dd")


def parse_iso_date(s):
    if not s:
        return None
    try:
        d = dateparser.parse(s).date()
        return d.isoformat()
    except Exception:
        return None


class ItemDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Add / Edit Item")
        self.resize(450, 350)
        self.data = data or {}

        layout = QFormLayout()
        self.title_in = QLineEdit(self.data.get("title", ""))
        self.type_in = QComboBox()
        self.type_in.addItems(["book", "magazine", "film", "other"])
        if "item_type" in self.data:
            try:
                idx = self.type_in.findText(self.data["item_type"])
                if idx >= 0:
                    self.type_in.setCurrentIndex(idx)
            except Exception:
                pass

        self.author_in = QLineEdit(self.data.get("author_or_director", ""))
        self.published_date_in = QDateEdit()
        self.published_date_in.setCalendarPopup(True)
        self.published_date_in.setDisplayFormat("yyyy-MM-dd")

        if "published_date" in self.data and self.data["published_date"]:
            parsed = parse_iso_date(self.data["published_date"])
            if parsed:
                y, m, d = map(int, parsed.split("-"))
                self.published_date_in.setDate(QDate(y, m, d))
        else:
            # leave as invalid so it prints nothing unless set
            self.published_date_in.setDate(QDate.currentDate())

        self.isbn_in = QLineEdit(self.data.get("isbn", ""))
        self.desc_in = QTextEdit(self.data.get("description", ""))
        self.available_in = QCheckBox("Is available?")
        self.available_in.setChecked(self.data.get("is_available", True))

        self.expected_date_in = QDateEdit()
        self.expected_date_in.setCalendarPopup(True)
        self.expected_date_in.setDisplayFormat("yyyy-MM-dd")
        if self.data.get("expected_available_date"):
            parsed = parse_iso_date(self.data["expected_available_date"])
            if parsed:
                y, m, d = map(int, parsed.split("-"))
                self.expected_date_in.setDate(QDate(y, m, d))
        else:
            self.expected_date_in.setDate(QDate.currentDate())

        layout.addRow("Title:", self.title_in)
        layout.addRow("Type:", self.type_in)
        layout.addRow("Author/Director:", self.author_in)
        layout.addRow("Published date:", self.published_date_in)
        layout.addRow("ISBN:", self.isbn_in)
        layout.addRow("Description:", self.desc_in)
        layout.addRow(self.available_in)
        layout.addRow("Expected available date:", self.expected_date_in)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addRow(btn_layout)

        self.setLayout(layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_payload(self):
        # collect values and return dict suitable for API
        published = iso_date_or_none(self.published_date_in.date()) if self.published_date_in.date().isValid() else None
        expected = iso_date_or_none(self.expected_date_in.date()) if self.expected_date_in.date().isValid() else None

        payload = {
            "title": self.title_in.text().strip(),
            "item_type": self.type_in.currentText(),
            "author_or_director": self.author_in.text().strip() or None,
            "published_date": published,
            "isbn": self.isbn_in.text().strip() or None,
            "description": self.desc_in.toPlainText().strip() or None,
            "is_available": bool(self.available_in.isChecked()),
            "expected_available_date": expected if not self.available_in.isChecked() and expected else None
        }
        # remove None to keep payload small
        return {k: v for k, v in payload.items() if v is not None}


class LibraryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Manager (PyQt Client)")
        self.resize(900, 500)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.toggle_avail_btn = QPushButton("Toggle Availability")

        for w in (self.refresh_btn, self.add_btn, self.edit_btn, self.delete_btn, self.toggle_avail_btn):
            hbox.addWidget(w)

        vbox.addLayout(hbox)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Type", "Author/Director", "Available", "Expected date"])
        self.table.setColumnHidden(0, True)  # hide ID column but keep it available for actions
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        # Track column widths set by user
        header = self.table.horizontalHeader()
        if header:
            header.sectionResized.connect(self.on_column_resized)
        self.user_column_widths = {}  # store user-set column widths
        vbox.addWidget(self.table)

        self.setLayout(vbox)

        # connect
        self.refresh_btn.clicked.connect(self.load_items)
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        self.toggle_avail_btn.clicked.connect(self.toggle_availability)

        # initial load
        self.load_items()

    def api_get(self, path, params=None):
        try:
            r = requests.get(API_BASE + path, params=params, timeout=6)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network error", f"GET {path} failed:\n{e}")
            return None

    def api_post(self, path, json):
        try:
            r = requests.post(API_BASE + path, json=json, timeout=6)
            r.raise_for_status()
            return r.json(), r.status_code
        except requests.RequestException as e:
            # try to extract response JSON if available
            msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    msg = e.response.text
                except Exception:
                    pass
            QMessageBox.critical(self, "Network error", f"POST {path} failed:\n{msg}")
            return None, getattr(e, "response", None)

    def api_put(self, path, json):
        try:
            r = requests.put(API_BASE + path, json=json, timeout=6)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network error", f"PUT {path} failed:\n{e}")
            return None

    def api_delete(self, path):
        try:
            r = requests.delete(API_BASE + path, timeout=6)
            if r.status_code not in (200, 204):
                r.raise_for_status()
            return True
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network error", f"DELETE {path} failed:\n{e}")
            return False

    def load_items(self):
        # Save current column widths before clearing rows
        saved_widths = []
        for col in range(self.table.columnCount()):
            saved_widths.append(self.table.columnWidth(col))

        self.table.setRowCount(0)
        data = self.api_get("/items")
        if data is None:
            return
        # data is a list
        for item in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            id_item = QTableWidgetItem(str(item.get("id")))
            title_item = QTableWidgetItem(item.get("title", ""))
            type_item = QTableWidgetItem(item.get("item_type", ""))
            author_item = QTableWidgetItem(item.get("author_or_director") or "")
            avail_item = QTableWidgetItem("Yes" if item.get("is_available", True) else "No")
            expected_item = QTableWidgetItem(item.get("expected_available_date") or "")

            # align
            # align
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            avail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, title_item)
            self.table.setItem(row, 2, type_item)
            self.table.setItem(row, 3, author_item)
            self.table.setItem(row, 4, avail_item)
            self.table.setItem(row, 5, expected_item)

        # Restore user-set column widths if they exist, otherwise auto-resize
        if self.user_column_widths:
            for col, width in self.user_column_widths.items():
                if col < self.table.columnCount():
                    self.table.setColumnWidth(col, width)
        else:
            self.table.resizeColumnsToContents()

    def get_selected_item_id(self):
        sel = self.table.selectedItems()
        if not sel:
            return None
        # first column is hidden ID
        row = sel[0].row()
        id_item = self.table.item(row, 0)
        if id_item:
            return int(id_item.text())
        return None

    def on_column_resized(self, col, old_size, new_size):
        """Called when user manually resizes a column. Store the new width."""
        self.user_column_widths[col] = new_size

    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            payload = dialog.get_payload()
            if not payload.get("title") or not payload.get("item_type"):
                QMessageBox.warning(self, "Validation", "Title and type are required.")
                return
            data, status = self.api_post("/items", json=payload)
            if data:
                QMessageBox.information(self, "Created", f"Item created: {data.get('title')}")
                self.load_items()

    def edit_item(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            QMessageBox.warning(self, "No selection", "Select a row first.")
            return
        # get item details from the server (or reuse row contents)
        item = self.api_get(f"/items/{item_id}")
        if item is None:
            return
        dialog = ItemDialog(self, data=item)
        if dialog.exec_() == QDialog.Accepted:
            payload = dialog.get_payload()
            updated = self.api_put(f"/items/{item_id}", json=payload)
            if updated:
                QMessageBox.information(self, "Updated", f"Item updated: {updated.get('title')}")
                self.load_items()

    def delete_item(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            QMessageBox.warning(self, "No selection", "Select a row first.")
            return
        ok = QMessageBox.question(self, "Confirm delete", "Are you sure you want to delete the selected item?")
        if ok != QMessageBox.Yes:
            return
        if self.api_delete(f"/items/{item_id}"):
            QMessageBox.information(self, "Deleted", "Item deleted.")
            self.load_items()

    def toggle_availability(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            QMessageBox.warning(self, "No selection", "Select a row first.")
            return
        item = self.api_get(f"/items/{item_id}")
        if item is None:
            return
        currently_available = item.get("is_available", True)
        if currently_available:
            # ask for expected date to set when it will be available
            expected, ok = QInputDialog.getText(self, "Mark unavailable", "Enter expected available date (YYYY-MM-DD):")
            if not ok:
                return
            # simple validation
            expected_parsed = parse_iso_date(expected)
            if not expected_parsed:
                QMessageBox.warning(self, "Bad date", "Please provide a valid date in YYYY-MM-DD.")
                return
            payload = {"is_available": False, "expected_available_date": expected_parsed}
        else:
            payload = {"is_available": True, "expected_available_date": None}

        updated = self.api_put(f"/items/{item_id}", json=payload)
        if updated:
            self.load_items()
            QMessageBox.information(self, "Updated", "Availability updated.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LibraryApp()
    w.show()
    sys.exit(app.exec_())
