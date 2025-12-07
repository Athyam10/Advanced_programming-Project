from app import create_app, db

app = create_app()


if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True)

from app import create_app, db
from app.models import LibraryItem
import os


app = create_app()


# flask shell context
@app.shell_context_processor
def make_shell_context():
    return {"db": db, "LibraryItem": LibraryItem}


if __name__ == "__main__":
    app.run(debug=True)