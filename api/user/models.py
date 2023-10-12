from flask_restx import fields

from api import api


user_model = api.model("User", {
    "id": fields.Integer,
    "full_name": fields.String,
    "email": fields.String,
    "phone": fields.String,
    "username": fields.String,
})

register_user_model = api.model("RegisterUser", {
    "full_name": fields.String(description="The user's full name", required=True),
    "email": fields.String(description="The user's main email", required=True),
    "phone": fields.String(required=True),
    "username": fields.String(required=True),
    "password": fields.String(required=True),
})

edit_user_model = api.model("RegisterUser", {
    "id": fields.Integer(required=True),
    "email": fields.String(required=False),
    "phone": fields.String(required=False),
    "username": fields.String(required=False),
    "password": fields.String(required=False),
})

authenticate_user_model = api.model("AuthenticateUser", {
    "username": fields.String,
    "password": fields.String,
})

privilege_model = api.model("Privilege", {
    "privilege": fields.String,
})