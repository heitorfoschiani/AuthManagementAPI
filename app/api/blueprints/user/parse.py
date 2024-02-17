from flask_restx import reqparse


user_id_parse = reqparse.RequestParser()
user_id_parse.add_argument(
    "user_id", 
    type=int, 
    required=False, 
    help="The user id"
)


username_parse = reqparse.RequestParser()
username_parse.add_argument(
    "username", 
    type=str, 
    required=False, 
    help="The username"
)