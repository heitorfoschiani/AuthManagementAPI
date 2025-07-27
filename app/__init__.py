from flask import Flask

from .logs.config import configure_logging
from .database import initialize_database
from .extensions import configure_extensions
from .api.blueprints.auth_management.register import register_auth_management_blueprint


def create_app(enviroment: str="Production"):
    app = Flask(__name__)
    
    configure_extensions(app, enviroment)
    initialize_database(app)
    configure_logging()

    register_auth_management_blueprint(app)
    
    return app


if __name__ == "__main__":
    create_app()