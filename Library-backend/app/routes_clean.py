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
