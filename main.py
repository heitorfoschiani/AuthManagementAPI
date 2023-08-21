# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Number: (11) 9 4825-3334

# Importing libraries
from flask import Flask, jsonify, abort, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, current_user
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta

# Importing python files from the project
import dbconnection
from user_management import User, table_userinfos_exists, create_table_userinfos


# Starting app
app = Flask(__name__)

CORS(app)

bcrypt = Bcrypt(app)


# User Authentcation Menagement
app.config["JWT_SECRET_KEY"] = "my-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=6)
jwt = JWTManager(app)

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
    cursor.execute('SELECT user_id, full_name, email, phone, username FROM userinfos WHERE user_id = %s', (identity,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
    
    return None


# User menagement routes
@app.route('/user', methods=['POST']) 
def register_user():
    js = request.get_json()

    # checking if the user information was sent into the request
    if not js:
        abort(400, 'Missing user infoormations')

    required_fields = ['full_name', 'email', 'phone', 'username', 'password']
    user_infos = {}
    for field in required_fields:
        if field not in js:
            abort(400, f'Missing {field}')
        user_infos[field] = js[field].lower() if field in ['email', 'username'] else js[field]

    # creating user object
    user = User(0, user_infos['full_name'], user_infos['email'], user_infos['phone'], user_infos['username'])

    # encrypting the password
    hashed_password = bcrypt.generate_password_hash(user_infos['password'])
    password = hashed_password.decode('utf-8')

    # checking if the table "userinfos" exists into postgres
    if not table_userinfos_exists():
        # creating table "userinfos" into postgress
        create_table = create_table_userinfos()
        if not create_table:
            abort(500, 'Error to create table user')

    # checking if username or email already exists
    if user.username_exists():
        abort(401, f'{user.username} already exists')
    elif user.email_exists():
        abort(401, f'{user.email} already exists')

    # registering user
    user_id = user.register(password)
    if user_id != 0:
        user.id = user_id

    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    response = jsonify(
        access_token=access_token, 
        refresh_token=refresh_token
    )

    return response, 200

@app.route('/user/authenticate', methods=['POST'])
def authenticate_user():
    js = request.get_json()

    # checking if the user information was sent in the request
    if not js:
        abort(400, 'Missing user information')

    required_fields = ['username', 'password']
    user_infos = {}
    for field in required_fields:
        if field not in js:
            abort(400, f'Missing {field}')
        user_infos[field] = js[field].lower() if field == 'username' else js[field]

    # extracting username and passowrd of the user
    try:
        conn = dbconnection.connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, full_name, email, phone, username, password FROM userinfos WHERE username = %s', (user_infos['username'],))
        user_data = cursor.fetchone()
    except Exception as e:
        abort(500, f'Error fetching user: {e}')
    finally:
        conn.close()

    # checking if user exist
    if user_data:
        # checking password
        if bcrypt.check_password_hash(user_data[5].encode('utf-8'), user_infos['password']):
            # authenticating user
            user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            response = jsonify(
                username=True,
                password=True,
                access_token=access_token,
                refresh_token=refresh_token,
            )
            status_code = 200
        else:
            # reporting invalid password
            response = jsonify(
                username=True,
                password=False,
                access_token=None,
            )
            status_code = 401
    else:
        # reporting non-existent user
        response = jsonify(
            username=False,
            password=False,
            access_token=None,
        )
        status_code = 404

    return response, status_code

@app.route('/user/refresh-authentication', methods=['POST'])
@jwt_required(refresh=True)
def refresh_authentication():
    identity = get_jwt_identity()

    conn = dbconnection.connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, full_name, email, phone, username FROM userinfos WHERE user_id = %s', (identity,))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        return jsonify(access_token=None), 404

    user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route('/user', methods=['GET'])
@jwt_required()
def get_authentcated_user_infos():
    return jsonify(
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        username=current_user.username,
    ), 200


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True,
    )