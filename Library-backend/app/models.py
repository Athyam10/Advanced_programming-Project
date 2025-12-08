from . import db


class Book(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128), nullable=False)
	author = db.Column(db.String(128), nullable=False)

	def __repr__(self):
		return f"<Book {self.title!r} by {self.author!r}>"


class LibraryItem(db.Model):
	__tablename__ = 'library_items'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255), nullable=False)
	item_type = db.Column(db.String(50), nullable=False)  # 'book', 'magazine', 'film', etc.
	author_or_director = db.Column(db.String(255), nullable=True)
	is_available = db.Column(db.Boolean, default=True, nullable=False)
	expected_available_date = db.Column(db.Date, nullable=True)

	def to_dict(self):
		return {
			'id': self.id,
			'title': self.title,
			'item_type': self.item_type,
			'author_or_director': self.author_or_director,
			'is_available': self.is_available,
			'expected_available_date': self.expected_available_date.isoformat() if self.expected_available_date else None,
		}
