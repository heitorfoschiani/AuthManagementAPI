# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Phone-number: (11) 9 4825-3334

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta
import logging

from api import api
from api.namespaces.user.objects import User
from database.dbmanagement.tables import create_dbtables
from api.namespaces.user.resources import ns_user
from api.namespaces.privilege.resources import ns_privilege


def create_app():
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s %(levelname)s %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S", 
        filename="logs/app.log", 
    )

    logging.info("Initializing the application")
    
    try:
        create_dbtables()

        application = Flask(__name__)

        application.config["JWT_SECRET_KEY"] = "my-secret-key"
        application.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
        application.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=6)
        application.config["flask_bcrypt"] = Bcrypt(application)
        application.config["jwt"] = JWTManager(application)

        jwt = application.config["jwt"]

        @jwt.user_identity_loader
        def user_identity_lookup(user):
            return user.id
        
        @jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            identity = jwt_data["sub"]

            user = User.get({
                "user_id": identity
            }) 
            return user

        CORS(application)

        api.init_app(application,)

        name_spaces = (ns_user, ns_privilege)
        for name_space in name_spaces:
            api.add_namespace(name_space)
    except Exception as e:
        logging.critical(f"Application terminated due to an initialization error: {e}")
        return None
    
    return application
