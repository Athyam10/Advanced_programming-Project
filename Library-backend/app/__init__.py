from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    db.init_app(app)
    from .routes_fixed import bp as routes_bp
    app.register_blueprint(routes_bp)
    return app
