# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Phone-number: (11) 9 4825-3334

from flask import Flask

from .config import Config
from .logs import configure_logging
from .database import initialize_database
from .extensions import configure_extensions
from .api.blueprints.auth_management import auth_management_api, auth_management_blueprint
from .api.blueprints import register_auth_management


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    configure_logging()
    initialize_database()
    configure_extensions(app)

    register_auth_management(
        app=app,
        api=auth_management_api, 
        blueprint=auth_management_blueprint
    )
    
    return app