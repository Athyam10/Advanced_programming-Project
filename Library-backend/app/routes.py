from flask import Blueprint, jsonify
from .models import Book

bp = Blueprint('api', __name__)


@bp.route('/health')
def health():
    return jsonify({"status": "ok"})


@bp.route('/books')
def list_books():
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])
from flask import Blueprint, jsonify
from .models import Book

bp = Blueprint('api', __name__)


@bp.route('/health')
def health():
    return jsonify({"status": "ok"})


@bp.route('/books')
def list_books():
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])
from flask import Blueprint, jsonify
from .models import Book

bp = Blueprint('api', __name__)


@bp.route('/health')
def health():
    return jsonify({"status": "ok"})


@bp.route('/books')
def list_books():
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])
from flask import Blueprint, jsonify
from .models import Book

bp = Blueprint('api', __name__)


@bp.route('/health')
def health():
	return jsonify({"status": "ok"})


@bp.route('/books')
def list_books():
	books = Book.query.all()
	return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])

from flask import Blueprint, request, jsonify, current_app


# parse expected_available_date if provided
exp = json_data.get("expected_available_date")
if exp:
try:
item.expected_available_date = datetime.fromisoformat(exp).date()
except Exception:
return jsonify({"message": "expected_available_date must be ISO date (YYYY-MM-DD)"}), 400


from flask import Blueprint, jsonify
from .models import Book

bp = Blueprint('api', __name__)


@bp.route('/health')
def health():
    return jsonify({"status": "ok"})


@bp.route('/books')
def list_books():
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])
