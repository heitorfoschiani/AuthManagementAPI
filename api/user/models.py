# Importing libraries
from flask_restx import fields

# Importing python files from the project
from api.__initi__ import api


user_model = api.model('User', {
    'id': fields.Integer,
    'full_name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'username': fields.String,
})

register_user_model = api.model('RegisterUser', {
    'full_name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'username': fields.String,
    'password': fields.String,
})

authenticate_user_model = api.model('AuthenticateUser', {
    'username': fields.String,
    'password': fields.String,
})