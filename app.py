from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta

import database.dbconnection as dbconnection
from api.user.objects import User
from api import api
from api.user.objects import get_user
from api.user.resourses import ns_user


def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = "my-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=6)
    app.config["flask_bcrypt"] = Bcrypt(app)
    app.config["jwt"] = JWTManager(app)

    jwt = app.config["jwt"]

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        
        user = get_user(identity)
        return user

    CORS(app)

    api.init_app(app)
    api.add_namespace(ns_user)

    return app