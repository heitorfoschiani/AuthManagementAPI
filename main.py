# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Number: (11) 9 4825-3334

# Importing libraries
from flask import Flask, jsonify, abort, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, current_user
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

# Importing python files from the project 
import dbconnection


# Starting app
app = Flask(__name__)

CORS(app)

bcrypt = Bcrypt(app)


# User Authentcation Menagement
app.config["JWT_SECRET_KEY"] = "my-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=30)
jwt = JWTManager(app)

# User object
class User:
    def __init__(self, user_id, full_name, email, phone, username):
        self.id = user_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.username = username

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
@app.route('/register-user', methods=['POST'])
def register_user():
    js = request.get_json()

    # checking if the user information was sent in the request
    if not js:
        abort(400, 'Missing user infoormations')

    required_fields = ['full_name', 'email', 'phone', 'username', 'password']
    user_infos = {}
    for field in required_fields:
        if field not in js:
            abort(400, f'Missing {field}')
        user_infos[field] = js[field].lower() if field in ['email', 'username'] else js[field]

    # connecting to the database
    conn = dbconnection.connect_to_postgres()
    cursor = conn.cursor()

    # checking if the table "userinfos" exists
    cursor.execute(
        '''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = 'userinfos'
            );
        '''
    )
    if not cursor.fetchone()[0]:
        # creating database if it not exist
        try:
            cursor.execute(
                '''
                    CREATE TABLE userinfos(
                        user_id SERIAL PRIMARY KEY, 
                        full_name VARCHAR(255), 
                        email VARCHAR(255), 
                        phone VARCHAR(20), 
                        username VARCHAR(255), 
                        password TEXT,
                        creation_datetime TIMESTAMP
                    );
                '''
            )
            conn.commit()
        except Exception as e:
            conn.close()
            abort(500, f'Error to create table user: {e}')

    # checking if username or email already exists
    user = False
    for field in ['email', 'username']:
        try:
            cursor.execute(f'SELECT {field} FROM userinfos WHERE {field} = %s', (user_infos[field],))
            if cursor.fetchone() is not None:
                user = True
        except Exception as e:
            conn.close()
            abort(500, f'Error checking user: {e}')
        if user == True:
            print(field)
            abort(401, f'{field} already exists')

    # encrypting the password
    hashed_password = bcrypt.generate_password_hash(user_infos['password'])
    user_infos['password'] = hashed_password.decode('utf-8')

    # registering user
    try:
        cursor.execute('''
            INSERT INTO userinfos (full_name, email, phone, username, password, creation_datetime)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_infos['full_name'], user_infos['email'], user_infos['phone'], user_infos['username'], user_infos['password'], datetime.now(),))
        conn.commit()
    except Exception as e:
        conn.close()
        abort(500, f'Error to inseart infos on database: {e}')
        

    # getting user_id
    cursor.execute('''
        SELECT user_id FROM userinfos WHERE username = %s
    ''', (user_infos['username'],))
    user_infos['user_id'] = cursor.fetchone()[0]

    # returning values
    user_infos.pop('password', None)

    user = User(user_infos['user_id'], user_infos['full_name'], user_infos['email'], user_infos['phone'], user_infos['username'])
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    response = jsonify(
        access_token=access_token, 
        refresh_token=refresh_token
    )

    return response, 200

@app.route('/authenticate-user', methods=['POST'])
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

@app.route('/refresh-authentication', methods=['POST'])
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

@app.route('/get-authenticated-user-infos', methods=['GET'])
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