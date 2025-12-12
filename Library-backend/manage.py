from app import create_app, db
from app.models import Book

from app import create_app

app = create_app()


# flask shell context
@app.shell_context_processor
def make_shell_context():
	return {"db": db, "Book": Book}


if __name__ == "__main__":
    app.run(debug=True)