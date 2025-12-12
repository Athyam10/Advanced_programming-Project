from flask import Blueprint, jsonify, request, abort
from .models import Book, LibraryItem
from datetime import datetime

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


@bp.route('/items', methods=['GET'])
def list_items():
    """Return all library items as JSON list."""
    items = LibraryItem.query.order_by(LibraryItem.title).all()
    return jsonify([i.to_dict() for i in items])


@bp.route('/items', methods=['POST'])
def create_item():
    json_data = request.get_json() or {}
    title = json_data.get('title')
    item_type = json_data.get('item_type')
    if not title or not item_type:
        return jsonify({'message': 'title and item_type are required'}), 400

    author = json_data.get('author_or_director')
    is_available = bool(json_data.get('is_available', True))
    exp = json_data.get('expected_available_date')
    exp_date = None
    if exp:
        try:
            exp_date = datetime.fromisoformat(exp).date()
        except Exception:
            return jsonify({'message': 'expected_available_date must be YYYY-MM-DD'}), 400

    item = LibraryItem()
    item.title = title
    item.item_type = item_type
    item.author_or_director = author
    item.is_available = is_available
    item.expected_available_date = exp_date
    from . import db
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = LibraryItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = LibraryItem.query.get_or_404(item_id)
    json_data = request.get_json() or {}
    for field in ('title', 'item_type', 'author_or_director'):
        if field in json_data:
            setattr(item, field, json_data[field])

    if 'is_available' in json_data:
        item.is_available = bool(json_data['is_available'])
        if item.is_available:
            item.expected_available_date = None

    if 'expected_available_date' in json_data:
        exp = json_data['expected_available_date']
        if exp:
            try:
                item.expected_available_date = datetime.fromisoformat(exp).date()
                item.is_available = False
            except Exception:
                return jsonify({'message': 'expected_available_date must be YYYY-MM-DD'}), 400
        else:
            item.expected_available_date = None

    from . import db
    db.session.commit()
    return jsonify(item.to_dict())


@bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = LibraryItem.query.get_or_404(item_id)
    from . import db
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'deleted'}), 204


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

