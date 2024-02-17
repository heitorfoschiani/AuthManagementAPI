# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Phone-number: (11) 9 4825-3334

from flask import Flask

from .config import Config
from .logs import configure_logging
from .database import initialize_database
from .extensions import configure_extensions
from .api import api
from .api.blueprints.user.resources import user_namespace
from .api.blueprints.privilege.resources import privilege_namespace


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    configure_logging()
    initialize_database()
    configure_extensions(app)
    
    api.init_app(app)

    name_spaces = [user_namespace, privilege_namespace]
    list(api.add_namespace(name_space) for name_space in name_spaces)
    
    return app