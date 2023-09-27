from flask import abort, current_app
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, current_user
from flask_restx import Namespace, Resource, reqparse
from flask_bcrypt import Bcrypt

from database.dbconnection import connect_to_postgres
from api.user.objects import User
from api.user.models import register_user_model, user_model, authenticate_user_model


authorizations = {
    'jsonWebToken': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
ns_user = Namespace(
    'user', 
    authorizations=authorizations
)


user_id_parse = reqparse.RequestParser()
user_id_parse.add_argument(
    'user_id', 
    type=int, 
    required=False, 
    help='The user id'
)

@ns_user.route('/')
class RegisterUser(Resource):
    @ns_user.expect(register_user_model)
    def post(self):
        # The post method of this end-ponis registers a new user into the server

        user = User(
            id = 0, 
            full_name = ns_user.payload['full_name'], 
            email = ns_user.payload['email'], 
            phone = ns_user.payload['phone'], 
            username = ns_user.payload['username'],
        )

        if user.username_exists():
            abort(401, f'{user.username} already exists')
        elif user.email_exists():
            abort(401, f'{user.email} already exists')

        bcrypt = Bcrypt(current_app)
        hashed_password = bcrypt.generate_password_hash(ns_user.payload['password'])
        password = hashed_password.decode('utf-8')

        if not user.register(password):
            abort(500, 'Error when register user')

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        dict_response = {
            'id': user.id,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

        return dict_response

    @ns_user.marshal_with(user_model)
    @ns_user.expect(user_id_parse)
    @ns_user.doc(security='jsonWebToken')
    @jwt_required()
    def get(self):
        # The get method of this end-point returns the current user by the acess_token send

        args = user_id_parse.parse_args()

        user_id = args['user_id']

        if not user_id or user_id == current_user.id:
            return current_user
        
        privileges_allowed = ['administrator', 'manager']

        if not any(item in privileges_allowed for item in current_user.privilege()):
            abort(401, 'The user does not have permission to access this informations')

        try:
            conn = connect_to_postgres()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, full_name, email, phone, username FROM users WHERE id = %s', 
                (user_id,)
            )
            user_data = cursor.fetchone()
            if not user_data:
                abort(404, 'User not fonded')
        except Exception as e:
            abort(500, f'Error fetching user: {e}')
        finally:
            conn.close()

        user = User(
            id = user_data[0], 
            full_name = user_data[1], 
            email = user_data[2], 
            phone = user_data[3], 
            username= user_data[4]
        )

        return user
    
    @ns_user.marshal_with(user_model)
    @ns_user.expect(user_id_parse)
    @ns_user.doc(security='jsonWebToken')
    @jwt_required()
    def put(self):
        # The put method of this end-point edit an user info into the server by the user_id informed

        pass

    @ns_user.marshal_with(user_model)
    @ns_user.doc(security='jsonWebToken')
    @jwt_required()
    def delete(self):
        # The put method of this end-point delete an user info into the server by the user_id informed

        pass

@ns_user.route('/authenticate')
class Authenticate(Resource):
    @ns_user.expect(authenticate_user_model)
    def post(self):
        # The post method of this end-point authanticate the user and returns an access token followed by a refresh token

        try:
            conn = connect_to_postgres()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, full_name, email, phone, username, password FROM users WHERE username = %s', 
                (ns_user.payload['username'],)
            )
            user_data = cursor.fetchone()
        except Exception as e:
            abort(500, f'Error fetching user: {e}')
        finally:
            conn.close()

        if user_data:
            bcrypt = current_app.config['flask_bcrypt']
            if bcrypt.check_password_hash(user_data[5].encode('utf-8'), ns_user.payload['password']):
                user = User(
                    id = user_data[0], 
                    full_name = user_data[1], 
                    email = user_data[2], 
                    phone = user_data[3], 
                    username= user_data[4]
                )
                access_token = create_access_token(identity=user)
                refresh_token = create_refresh_token(identity=user)
                response = {
                    'user_id': user.id,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
                status_code = 200
            else:
                abort(401, 'incorrect password')
        else:
            abort(404, 'non-existing username')

        return response, status_code
    
@ns_user.route('/refresh-authentication')
class RefreshAuthentication(Resource):
    @ns_user.doc(security="jsonWebToken")
    @jwt_required(refresh=True)
    def post(self):
        # The post method of this end-point create an new acess_token for the authenticaded user

        identity = get_jwt_identity()

        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, full_name, email, phone, username FROM users WHERE id = %s', 
            (identity,)
        )
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            return {
                'user_id': None,
                'access_token': None,
                'refresh_token': None,
            }, 404

        user = User(
            id = user_data[0], 
            full_name = user_data[1], 
            email = user_data[2], 
            phone = user_data[3], 
            username= user_data[4]
        )
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        return {
            'user_id': user.id,
            'access_token': access_token, 
            'refresh_token': refresh_token,
        }
