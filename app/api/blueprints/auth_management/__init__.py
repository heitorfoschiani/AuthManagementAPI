from flask import Blueprint
from flask_restx import Api

from app.auth import authorizations


auth_management_blueprint = Blueprint(
    "auth_management", 
    __name__, 
    url_prefix="/auth-management"
)


auth_management_api = Api(
    auth_management_blueprint, 
    title="API Authentication Management", 
    version="1.0", 
    description="A secure Flask API that requires user authentication and manages access", 
    authorizations=authorizations, 
)