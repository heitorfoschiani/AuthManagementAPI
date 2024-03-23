from flask import Flask

from .config import Config
from .logs import configure_logging
from .database import initialize_database
from .extensions import configure_extensions
from .api.blueprints.auth_management.register import register_auth_management_blueprint


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    configure_extensions(app)
    configure_logging()
    initialize_database()

    register_auth_management_blueprint(app)
    
    return app