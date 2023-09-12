# Importing libraries
from flask import abort, current_app
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, current_user
from flask_restx import Resource, Namespace
from flask_bcrypt import Bcrypt

# Importing python files from the project
from dbconnection import connect_to_postgres, table_userinfos_exists, create_table_userinfos
from app.models import User, register_user_model, user_model, authenticate_user_model

authorizations = {
    "jsonWebToken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}
ns = Namespace(
    'api-authentication-menagement', 
    authorizations=authorizations
)

@ns.route('/user')
class UserAPI(Resource):
    @ns.expect(register_user_model)
    def post(self):
        # creating user object
        user = User(user_id=0, full_name=ns.payload['full_name'], email=ns.payload['email'], phone=ns.payload['phone'], username=ns.payload['username'])

        # checking if the table "userinfos" exists into postgres
        if not table_userinfos_exists():
            # creating table "userinfos" into postgress
            create_table = create_table_userinfos()
            if not create_table:
                abort(500, 'Error on create table userinfos')

        # checking if username or email already exists
        if user.username_exists():
            abort(401, f'{user.username} already exists')
        elif user.email_exists():
            abort(401, f'{user.email} already exists')

        # encrypting the password
        bcrypt = Bcrypt(current_app)
        hashed_password = bcrypt.generate_password_hash(ns.payload['password'])
        password = hashed_password.decode('utf-8')

        # registering user
        user_id = user.register(password)
        if user_id:
            user.id = user_id
        
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        response = {
            'user_id': user.id,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

        return response, 200

@ns.route('/authentication')
class Authentication(Resource):
    @ns.expect(authenticate_user_model)
    def post(self):
        # The post method of this end-point authanticate the user and returns an access token followed by a refresh token

        # extracting username and passowrd of the user
        try:
            conn = connect_to_postgres()
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, full_name, email, phone, username, password FROM userinfos WHERE username = %s', (ns.payload['username'],))
            user_data = cursor.fetchone()
        except Exception as e:
            abort(500, f'Error fetching user: {e}')
        finally:
            conn.close()

        # checking if user exist
        if user_data:
            # checking password
            bcrypt = Bcrypt(current_app)
            if bcrypt.check_password_hash(user_data[5].encode('utf-8'), ns.payload['password']):
                # authenticating user
                user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
                access_token = create_access_token(identity=user)
                refresh_token = create_refresh_token(identity=user)
                response = {
                    'username': True,
                    'password': True,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
                status_code = 200
            else:
                # reporting invalid password
                response = {
                    'username': True,
                    'password': False,
                    'access_token': None,
                    'refresh_token': None,
                }
                status_code = 401
        else:
            # reporting non-existent user
            response = {
                'username': False,
                'password': False,
                'access_token': None,
                'refresh_token': None,
            }
            status_code = 404

        return response, status_code
    
    @ns.doc(security="jsonWebToken")
    @ns.marshal_with(user_model)
    @jwt_required()
    def get(self):
        # The post method of this end-point  returns the authenticated user informations
        return current_user
    
@ns.route('/refresh-authentication')
class RefreshAuthentication(Resource):
    @jwt_required()
    def post(self):
        identity = get_jwt_identity()

        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, full_name, email, phone, username FROM userinfos WHERE user_id = %s', (identity,))
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            return {
                'access_token': None,
                'refresh_token': None,
            }, 404

        user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        return {
            'access_token': access_token, 
            'refresh_token': refresh_token,
        }, 200
