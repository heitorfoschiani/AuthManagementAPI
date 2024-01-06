from flask import abort, current_app
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, current_user
from flask_restx import Namespace, Resource, reqparse
import logging

from database.dbconnection import connect_to_postgres
from api.namespaces.user.objects import User
from api.namespaces.user.models import *


ns_user = Namespace(
    "user", 
)


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


privilege_parse = reqparse.RequestParser()
privilege_parse.add_argument(
    "privilege", 
    type=str, 
    required=False, 
    help="The privilege to be defined"
)


@ns_user.route("/")
class UserManagement(Resource):
    @ns_user.doc(description="The post method of this end-ponis registers a new user into the server")
    @ns_user.expect(register_user_model)
    def post(self):
        js_data = ns_user.payload

        user = User(
            id = 0, 
            full_name = js_data.get("full_name").lower(), 
            username = js_data.get("username").lower(),
            email = js_data.get("email").lower(), 
            phone = js_data.get("phone"), 
        )

        if user.username_exists():
            abort(401, f"{user.username} already exists")
        if user.email_exists():
            abort(401, f"{user.email} already exists")

        bcrypt = current_app.config["flask_bcrypt"]
        hashed_password = bcrypt.generate_password_hash(js_data.get("password"))
        password = hashed_password.decode("utf-8")

        if not user.register(password):
            abort(500, "An error occurred when register user")

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        access_user_information = {
            "id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        return access_user_information

    @ns_user.doc(description="The get method of this end-point returns the current user by the acess_token send or some information about the user")
    @ns_user.marshal_with(user_model)
    @ns_user.expect(user_id_parse, username_parse)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def get(self):
        user_id = user_id_parse.parse_args()["user_id"]
        username = username_parse.parse_args()["username"]

        if user_id and username:
            abort(400, "Can only provide either user_id or username, not both")
        
        if not user_id and not username:
            user_id = current_user.id 
            user = current_user
        elif user_id:
            user = User.get({
                "user_id": user_id
            })
        else:
            user = User.get({
                "username": username
            })

        if not user:
            abort(401, "User not founded")
        
        current_user_privileges = current_user.privileges()
        privileges_allowed = ["administrator", "manager"]
        allowed_privileges_present = any(privilege in privileges_allowed for privilege in current_user_privileges)
        if not allowed_privileges_present and user_id != current_user.id:
            abort(401, "The user does not have permission to access this information")

        privileges_not_allowed = ["inactive"]
        if any(privilege in privileges_not_allowed for privilege in current_user_privileges):
            abort(404, "The user is inactive")

        return user
    
    @ns_user.doc(description="The put method of this end-point edit an user information into the server by the user_id informed")
    @ns_user.marshal_with(user_model)
    @ns_user.expect(edit_user_model)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def put(self):
        user_id = ns_user.payload.get("id")

        current_user_privileges = current_user.privileges()
        privileges_allowed = ["administrator", "manager"]
        privileges_not_allowed = ["inactive"]
        allowed_privileges_present = any(privilege in privileges_allowed for privilege in current_user_privileges)
        not_allowed_privileges_present = any(privilege in privileges_not_allowed for privilege in current_user_privileges)
        if (not allowed_privileges_present and user_id != current_user.id) or not_allowed_privileges_present:
            abort(401, "The user does not have permission to change an information of another user")

        user_information = {
            "user_id": user_id
        }
        user = User.get(user_information)
        if not user:
            abort(401, "user not founded")

        update_information = ns_user.payload

        if "email" in update_information:
            if update_information["email"] == user.email:
                update_information.pop("email")

        if "phone" in update_information:
            if update_information["phone"] == user.phone:
                update_information.pop("phone")

        if "username" in update_information:
            if update_information["username"] == user.username:
                update_information.pop("username")

        if "password" in update_information:
            bcrypt = current_app.config["flask_bcrypt"]
            update_information["password"] = bcrypt.generate_password_hash(update_information["password"])
            update_information["password"] = update_information["password"].decode("utf-8")

            conn = connect_to_postgres()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT password FROM userpasswords 
                WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
            """, (user.id,))
            user_current_password = cursor.fetchone()[0]
            conn.close()
            if bcrypt.check_password_hash(user_current_password.encode("utf-8"), update_information["password"]):
                update_information.pop("password")

        if not user.update(update_information):
            abort(500, "An error occurred when update user information")

        return user

    @ns_user.doc(description="The delete method of this end-point delete an user informationinto the server by the user_id informed")
    @ns_user.expect(user_id_parse)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def delete(self):
        user_id = user_id_parse.parse_args()["user_id"]

        if not user_id:
            user_id = current_user.id
            user = current_user
        else:
            user = User.get({
                "user_id": user_id
            })

        current_user_privileges = current_user.privileges()
        privileges_allowed = ["administrator", "manager"]
        allowed_privileges_present = any(privilege in privileges_allowed for privilege in current_user_privileges)
        if not allowed_privileges_present and user_id != current_user.id:
            abort(401, "The user does not have permission to set a privilege to another user")

        if "inactive" in user.privileges():
            abort(401, "User is already inactive")

        if not user.inactivate():
            abort(500, "An error occurred when inactivate user")

        user_privilege_information = {
            "id": user.id,
            "privileges": user.privileges(),
        }

        return user_privilege_information


@ns_user.route("/authenticate")
class Authenticate(Resource):
    @ns_user.doc(description="The post method of this end-point authanticate the user and returns an access token followed by a refresh token")
    @ns_user.expect(authenticate_user_model)
    def post(self):
        username = ns_user.payload.get("username").lower()

        user = User.get({
            "username": username
        })

        if not user:
            abort(404, "Non-existing active username")

        if 'inactive' in user.privileges():
            abort(404, "Non-existing active username")
        
        user_password_hash = user.get_password_hash()
        bcrypt = current_app.config["flask_bcrypt"]
        if bcrypt.check_password_hash(user_password_hash.encode("utf-8"), ns_user.payload.get("password")):
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
        else:
            abort(401, "Incorrect password")

        access_user_information = {
            "user_id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        return access_user_information


@ns_user.route("/refresh-authentication")
class RefreshAuthentication(Resource):
    @ns_user.doc(description="The post method of this end-point create an new acess_token for the authenticaded user")
    @ns_user.doc(security="jsonWebToken")
    @jwt_required(refresh=True)
    def post(self):
        user = User.get({
            "user_id": current_user.id
        })

        if not user:
            abort(404, "User not founded")

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        access_user_information = {
            "user_id": user.id,
            "access_token": access_token, 
            "refresh_token": refresh_token,
        }

        return access_user_information