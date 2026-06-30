import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config_by_name

db = SQLAlchemy()


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    _configure_logging(app)

    db.init_app(app)

    from app.routes import tasks_bp
    app.register_blueprint(tasks_bp)

    from app.errors import register_error_handlers
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


def _configure_logging(app):
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app.logger.setLevel(level)
