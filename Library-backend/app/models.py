from . import db


class Book(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128), nullable=False)
	author = db.Column(db.String(128), nullable=False)

	def __repr__(self):
		return f"<Book {self.title!r} by {self.author!r}>"

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class LibraryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    author = db.Column(db.String(128), nullable=False)
    # Add other fields as needed
