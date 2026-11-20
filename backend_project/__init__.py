from flask import Flask

from .config import config_by_name
from .extensions import db, migrate
from .health import health_bp
from .main import main_bp
from .auth import auth_bp
from .trails import trails_bp
from .admin import admin_bp


def create_app(config_name="development"):
    app = Flask(__name__)

    app.config.from_object(config_by_name[config_name])

    if not app.config.get("JWT_SECRET"):
        raise RuntimeError("JWT_SECRET is not set. Add it to your .env file.")

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # (registers models so flask db can see them)

    app.register_blueprint(main_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trails_bp)
    app.register_blueprint(admin_bp)

    return app