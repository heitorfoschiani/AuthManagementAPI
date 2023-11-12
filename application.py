# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Phone-number: (11) 9 4825-3334

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta

from api import api
from api.user.objects import User
from api.user.resourses import ns_user
from database.dbmanagement.tables import create_dbtables


def create_app():
    application = Flask(__name__)

    if create_dbtables():
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

        api.init_app(application)
        api.add_namespace(ns_user)

        return application
    
    return None
