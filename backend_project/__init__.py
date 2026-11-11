from flask import Flask

from .config import config_by_name
from .extensions import db, migrate
from .main import main_bp
from .health import health_bp


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_bp)
    app.register_blueprint(health_bp)
    
    return app