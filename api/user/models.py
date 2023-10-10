from flask_restx import fields

from api import api


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

edit_user_model = api.model('RegisterUser', {
    'email': fields.String,
    'phone': fields.String,
    'username': fields.String,
    'password': fields.String,
})

authenticate_user_model = api.model('AuthenticateUser', {
    'username': fields.String,
    'password': fields.String,
})

privilege_model = api.model('Privilege', {
    'privilege': fields.String,
})