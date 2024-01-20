from flask import abort, current_app
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, current_user

from app.logs import log_request_headers_information, log_request_body_information
from app.api.namespaces.user import User
from .models import user_model, register_user_model, edit_user_model, authenticate_user_model
from .parse import user_id_parse, username_parse


ns_user = Namespace(
    "user", 
)


@ns_user.route("/")
class UserManagement(Resource):
    @ns_user.doc(
        description="""
            The post method of this end-point registers a new user into the server.
            On success, returns the user's ID and the access tokens.
        """,
        responses={
            201: "User successfully registered", 
            400: "Missing field in json data", 
            409: "Username or email already exists", 
            500: "Internal server error"
        }
    )
    @ns_user.expect(register_user_model)
    @log_request_headers_information
    def post(self):
        js_data = ns_user.payload

        required_fields = ["full_name", "username", "email", "password"]
        for field in required_fields:
            if field not in js_data:
                abort(400, f"{field} is required")

        user = User(
            id=0, 
            full_name=js_data.get("full_name").lower(), 
            username=js_data.get("username").lower(), 
            email=js_data.get("email").lower(), 
            phone=js_data.get("phone")
        )

        if user.username_exists():
            current_app.logger.error(f"User with username '{user.username}'already exists")
            abort(409, f"User with username '{user.username}'already exists")

        if user.email_exists():
            current_app.logger.error(f"User with email '{user.email}' already exists")
            abort(409, f"User with email '{user.email}' already exists")

        bcrypt = current_app.config["flask_bcrypt"]
        hashed_password = bcrypt.generate_password_hash(js_data["password"]).decode("utf-8")
        
        try:
            user.register(hashed_password)
        except Exception as e:
            current_app.logger.error(f"An error occorred when register user: {e}")
            abort(500, "An error occorred when register user")

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        user_access_information = {
            "id": user.id, 
            "access_token": access_token, 
            "refresh_token": refresh_token
        }

        return user_access_information, 201
    
    @ns_user.doc(
        description="""
            The put method of this end-point edit an existing user's information by user_id. 
            Only users with 'administrator' or 'manager' privileges might update information of another user.
        """,
        responses={
            200: "User information updated successfully", 
            403: "Forbidden - User does not have the necessary privileges", 
            404: "User not found", 
            500: "Internal server error"
        },
        security="jsonWebToken"
    )
    @ns_user.marshal_with(user_model)
    @ns_user.expect(edit_user_model)
    @jwt_required()
    @log_request_headers_information
    def put(self):
        js_data = ns_user.payload

        user_id = js_data.get("id")
        if not user_id:
            current_app.logger.error("The user id is required")
            abort(400, "The user id is required")

        user = User.get({
            "user_id": user_id
        })
        if not user:
            current_app.logger.error("User not founded")
            abort(404, "User not founded")

        user_privileges = user.privileges()
        current_user_privileges = current_user.privileges()
        if ("administrator" in user_privileges or "manager" in user_privileges) and "administrator" not in current_user_privileges:
            abort(403, "Insufficient privileges for inactivate an administrator")

        if user.id != current_user.id and ("administrator" not in current_user_privileges and "manager" not in current_user_privileges):
            abort(403, "Insufficient privileges for inactivate a user")

        if "username" in js_data:
            if js_data["username"] == user.username:
                js_data.pop("username")
            else:
                user.username = js_data["username"]
                if user.username_exists():
                    current_app.logger.error(f"User with username '{user.username}' already exists")
                    abort(409, f"User with username '{user.username}'already exists")

        if "email" in js_data:
            if js_data["email"] == user.email:
                js_data.pop("email")
            else:
                user.email = js_data["email"]
                if user.email_exists():
                    current_app.logger.error(f"User with email '{user.email}' already exists")
                    abort(409, f"User with email '{user.email}' already exists")

        if "phone" in js_data:
            if js_data["phone"] == user.phone:
                js_data.pop("phone")
            else:
                user.username = js_data["phone"]

        if "password" in js_data:
            bcrypt = current_app.config["flask_bcrypt"]
            js_data["password"] = bcrypt.generate_password_hash(js_data["password"]).decode("utf-8")
            user_current_password_hash = user.get_password_hash()
            if bcrypt.check_password_hash(user_current_password_hash.encode("utf-8"), js_data["password"]):
                js_data.pop("password")

        try:
            user.update(js_data)
        except Exception as e:
            current_app.logger.error(f"An error occurred when update user information: {e}")
            abort(500, "An error occurred when update user information")

        return user

    @ns_user.doc(
        description="""
            The delete method of this end-point inactivate an user by user_id. 
            Only users with 'administrator' or 'manager' privileges can inactivate another user.
        """,
        responses={
            200: "User successfully inactivated", 
            403: "Forbidden - User does not have the necessary privileges", 
            404: "User not found", 
            409: "User is already inactive", 
            500: "Internal server error"
        },
        security="jsonWebToken"
    )
    @ns_user.expect(user_id_parse)
    @jwt_required()
    @log_request_headers_information
    @log_request_body_information
    def delete(self):
        parse_data = user_id_parse.parse_args()

        user_id = parse_data.get("user_id")
        username = parse_data.get("username")

        if user_id:
            user = User.get({"user_id": user_id})
        elif username:
            user = User.get({"username": username})
        else:
            user = current_user

        if not user:
            current_app.logger.error("User not founded")
            abort(404, "User not founded")

        user_privileges = user.privileges()
        if "inactive" in user_privileges:
            current_app.logger.error("User is already inactive")
            abort(409, "User is already inactive")

        current_user_privileges = current_user.privileges()
        if ("administrator" in user_privileges or "manager" in user_privileges) and "administrator" not in current_user_privileges:
            abort(403, "Insufficient privileges for inactivate an administrator")

        if user.id != current_user.id and ("administrator" not in current_user_privileges and "manager" not in current_user_privileges):
            abort(403, "Insufficient privileges for inactivate a user")

        try:
            user.inactivate()
        except Exception as e:
            current_app.logger.error(f"An error occurred when inactivate user: {e}")
            abort(500, "An error occurred when inactivate user")

        user_privilege_information = {
            "id": user.id,
            "privileges": user.privileges(),
        }

        return user_privilege_information

    @ns_user.doc(
        description="""
            The get method of this end-point returns user information based on the provided access token, user_id, or username. 
            Only 'administrator' or 'manager' users, or the user themself, can access information.
        """,
        responses={
            200: "User information returned successfully",
            400: "Bad request - invalid parameters",
            403: "Forbidden - User does not have the necessary privileges",
            404: "User not founded",
            500: "Internal server error"
        },
        security="jsonWebToken"
    )
    @ns_user.marshal_with(user_model)
    @ns_user.expect(user_id_parse, username_parse)
    @jwt_required()
    @log_request_headers_information
    @log_request_body_information
    def get(self):
        user_id_parse_data = user_id_parse.parse_args()
        username_parse_data = username_parse.parse_args()

        user_id = user_id_parse_data.get("user_id")
        username = username_parse_data.get("username")

        if user_id and username:
            current_app.logger.error("Can only provide either user_id or username, not both")
            abort(400, "Can only provide either user_id or username, not both")
        
        if not user_id and not username:
            user_id = current_user.id 
            user = current_user
        elif user_id:
            user = User.get({
                "user_id": user_id
            })
        elif username:
            user = User.get({
                "username": username
            })

        if not user:
            current_app.logger.error("User not founded")
            abort(404, "User not founded")
        
        user_privileges = user.privileges()
        current_user_privileges = current_user.privileges()
        if "inactive" in user_privileges and ("administrator" not in current_user_privileges and "manager" not in current_user_privileges):
            current_app.logger.error("User not founded")
            abort(404, "User not founded")

        if user.id != current_user.id and ("administrator" not in current_user_privileges and "manager" not in current_user_privileges):
            current_app.logger.error("Insufficient privileges")
            abort(403, "Insufficient privileges")

        return user


@ns_user.route("/authenticate")
class Authenticate(Resource):
    @ns_user.doc(
        description="""
            This end-point authenticates a user with username and password, and returns access and refresh tokens upon successful authentication.
        """,
        responses={
            200: "Authentication successful",
            401: "Incorrect password",
            404: "Non-existing username",
            500: "Internal server error"
        }
    )
    @ns_user.expect(authenticate_user_model)
    @log_request_headers_information
    def post(self):
        js_data = ns_user.payload

        username = js_data.get("username").lower()

        user = User.get({"username": username})
        if not user or "inactive" in user.privileges():
            current_app.logger.error("Non-existing or inactive username.")
            abort(404, "Non-existing or inactive username.")
        
        user_password_hash = user.get_password_hash()
        bcrypt = current_app.config["flask_bcrypt"]
        if not bcrypt.check_password_hash(user_password_hash.encode("utf-8"), ns_user.payload.get("password")):
            current_app.logger.error("Incorrect password")
            abort(401, "Incorrect password")

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        access_user_information = {
            "user_id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        return access_user_information


@ns_user.route("/refresh-authentication")
class RefreshAuthentication(Resource):
    @ns_user.doc(
        description="""
            This end-point generates a new access token for the authenticated user using a valid refresh token.
        """,
        responses={
            200: "New access token generated successfully",
            404: "User not found",
            500: "Internal server error"
        },
        security="jsonWebToken"
    )
    @jwt_required(refresh=True)
    @log_request_headers_information
    def post(self):
        user = User.get({
            "user_id": current_user.id
        })

        if not user:
            current_app.logger.error("User not founded")
            abort(404, "User not founded")

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        access_user_information = {
            "user_id": user.id,
            "access_token": access_token, 
            "refresh_token": refresh_token,
        }

        return access_user_information