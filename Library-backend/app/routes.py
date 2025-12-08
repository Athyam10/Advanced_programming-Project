from flask import Blueprint, jsonify
from .models import Book

bp = Blueprint('api', __name__)


@bp.route('/health')
def health():
    return jsonify({"status": "ok"})


@bp.route('/books')
def list_books():
    """Return list of books stored in the database.

    Each book is represented as a small dict with `id`, `title`, and `author`.
    """
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])


@bp.route('/')
def index():
    """Root endpoint — brief HTML with links to API endpoints for browser users."""
    return (
        '<html><head><title>Library API</title></head>'
        '<body><h1>Library API</h1>'
        '<ul>'
        '<li><a href="/health">/health</a></li>'
        '<li><a href="/books">/books</a></li>'
        '</ul></body></html>'
    )

