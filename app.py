# Importing libraries
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta

# Importing python files from the project
import database.dbconnection as dbconnection
from api.user.objects import User
from api import api
from api.user.resourses import ns_user


def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = "my-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=30)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=6)
    app.config["flask_bcrypt"] = Bcrypt(app)
    app.config["jwt"] = JWTManager(app)

    jwt = app.config['jwt']

    # Callback function to get user identity (id) for JWT
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    # Callback function to load user from the database using JWT
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data['sub']

        conn = dbconnection.connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, full_name, email, phone, username FROM users WHERE user_id = %s', (identity,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
        
        return None

    CORS(app)

    api.init_app(app)
    api.add_namespace(ns_user)

    return app