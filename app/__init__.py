from flask import Flask

from app.extensions import db, migrate
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    _init_extensions(app)
    _register_blueprints(app)

    return app


def _init_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from .models import Account, Transaction  # noqa: F401


def _register_blueprints(app: Flask):
    from .routes import wallet_bp

    app.register_blueprint(wallet_bp)
