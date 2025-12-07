from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()




def create_app(config_object=None):
	app = Flask(__name__)
	app.config.from_object(config_object or "app.config.Config")

	db.init_app(app)
	migrate.init_app(app, db)

	# register routes
	from .routes import bp as api_bp
	app.register_blueprint(api_bp, url_prefix="/api")

	return app