# app/__init__.py
from flask import Flask
def create_app(config_object=None):
    app = Flask(__name__)

    if config_object:
        app.config.from_object(config_object)

    # ---- Register API blueprint CLEANLY ----
    try:
        from .routes import bp as api_bp
    except Exception as e:
        raise RuntimeError(f"Failed to import API blueprint: {e}")

    # Register only if not already registered
    if "api" not in app.blueprints:
        app.register_blueprint(api_bp, url_prefix="/api")

    # Health check route (used by some tests)
    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
