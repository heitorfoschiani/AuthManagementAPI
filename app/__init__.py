from flask import Flask

from .logs.config import configure_logging
from .database import initialize_database
from .extensions import configure_extensions
from .api.blueprints.auth_management.register import register_auth_management_blueprint


def create_app():
    app = Flask(__name__)
    
    configure_logging()
    initialize_database()

    register_auth_management_blueprint(app)

    configure_extensions(app)
    
    return app