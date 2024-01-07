from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from .api.namespaces.user import User


def configure_extensions(app):
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
    
    app.config["jwt"] = jwt
    app.config["flask_bcrypt"] = Bcrypt(app)
    CORS(app)