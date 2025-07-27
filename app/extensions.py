from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from .config import Config
from .api.blueprints.auth_management.namespaces.user import User
from .database.connection import PostgresConnection


def configure_extensions(app, enviroment: str, config_class=Config):
    jwt = JWTManager(app)

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
    
    app.config.from_object(config_class)
    app.config["jwt"] = jwt
    app.config["flask_bcrypt"] = Bcrypt(app)
    app.config["enviroment"] = enviroment
    app.config["postgres_connection"] = PostgresConnection(enviroment)
    
    CORS(app)