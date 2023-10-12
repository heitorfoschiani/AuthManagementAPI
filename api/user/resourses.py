from flask import abort, current_app
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, current_user
from flask_restx import Namespace, Resource, reqparse

from database.dbconnection import connect_to_postgres
from api.user.objects import User, get_user
from api.user.models import *


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

privilege_parse = reqparse.RequestParser()
privilege_parse.add_argument(
    "privilege", 
    type=str, 
    required=False, 
    help="The privilege to be defined"
)


@ns_user.route("/")
class UserManagement(Resource):
    @ns_user.expect(register_user_model)
    def post(self):
        # The post method of this end-ponis registers a new user into the server

        user = User(
            id = 0, 
            full_name = ns_user.payload["full_name"], 
            email = ns_user.payload["email"], 
            phone = ns_user.payload["phone"], 
            username = ns_user.payload["username"],
        )

        if user.username_exists():
            abort(401, f"{user.username} already exists")
        elif user.email_exists():
            abort(401, f"{user.email} already exists")

        bcrypt = current_app.config["flask_bcrypt"]
        hashed_password = bcrypt.generate_password_hash(ns_user.payload["password"])
        password = hashed_password.decode("utf-8")

        if not user.register(password):
            abort(500, "error when register user")

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        return {
            "id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @ns_user.marshal_with(user_model)
    @ns_user.expect(user_id_parse)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def get(self):
        # The get method of this end-point returns the current user by the acess_token send

        args = user_id_parse.parse_args()

        user_id = args["user_id"]

        if not user_id or user_id == current_user.id:
            return current_user
        
        current_user_privileges = current_user.privileges()
        privileges_allowed = ["administrator", "manager"]
        if not any(item in privileges_allowed for item in current_user_privileges):
            abort(401, "the user does not have permission to access this informations")

        user = get_user(user_id)

        return user
    
    @ns_user.marshal_with(user_model)
    @ns_user.expect(edit_user_model)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def put(self):
        # The put method of this end-point edit an user informations into the server by the user_id informed

        user_id = ns_user.payload["id"]

        current_user_privileges = current_user.privileges()
        privileges_allowed = ["administrator", "manager"]
        if not any(item in privileges_allowed for item in current_user_privileges) and user_id != current_user.id:
            abort(401, "the user does not have permission to set a privilege to another user")

        user = get_user(user_id)
        if not user:
            abort(401, "user not founded")

        update_information = ns_user.payload
        if "email" in update_information:
            if update_information["email"] == user.email:
                update_information.pop("email")

        update_information = ns_user.payload
        if "phone" in update_information:
            if update_information["phone"] == user.phone:
                update_information.pop("phone")

        update_information = ns_user.payload
        if "username" in update_information:
            if update_information["username"] == user.username:
                update_information.pop("username")

        if "password" in update_information:
            bcrypt = current_app.config["flask_bcrypt"]
            update_information["password"] = bcrypt.generate_password_hash(update_information["password"])
            conn = connect_to_postgres()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password FROM userpasswords WHERE status_id = 1 AND user_id = %s",
                (user.id,)
            )
            user_current_password = cursor.fetchone()[0]
            conn.close()
            if bcrypt.check_password_hash(user_current_password.encode("utf-8"), update_information["password"]):
                update_information.pop("password")

        if not user.update(update_information):
            abort(500, "error when update user informations")

        return user

    @ns_user.marshal_with(user_model)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def delete(self):
        # The delete method of this end-point delete an user informationinto the server by the user_id informed

        pass

@ns_user.route("/authenticate")
class Authenticate(Resource):
    @ns_user.expect(authenticate_user_model)
    def post(self):
        # The post method of this end-point authanticate the user and returns an access token followed by a refresh token

        conn = connect_to_postgres()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 
                    users.id,
                    users.full_name,
                    useremails.email,
                    userphones.phone,
                    usernames.username,
                    userpasswords.password
                FROM users
                LEFT JOIN useremails ON useremails.user_id = users.id
                LEFT JOIN userphones ON userphones.user_id = users.id
                LEFT JOIN usernames ON usernames.user_id = users.id
                LEFT JOIN userpasswords ON userpasswords.user_id = users.id
                WHERE 
                useremails.status_id = 1 AND
                userphones.status_id = 1 AND
                usernames.status_id = 1 AND 
                usernames.username = %s
            """,(ns_user.payload["username"],))
            user_data = cursor.fetchone()
        except Exception as e:
            abort(500, f"error fetching user: {e}")
        finally:
            conn.close()

        if user_data:
            bcrypt = current_app.config["flask_bcrypt"]
            if bcrypt.check_password_hash(user_data[5].encode("utf-8"), ns_user.payload["password"]):
                user = User(
                    id = user_data[0], 
                    full_name = user_data[1], 
                    email = user_data[2], 
                    phone = user_data[3], 
                    username= user_data[4]
                )
                access_token = create_access_token(identity=user)
                refresh_token = create_refresh_token(identity=user)
            else:
                abort(401, "incorrect password")
        else:
            abort(404, "non-existing username")

        return {
            "user_id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    
@ns_user.route("/refresh-authentication")
class RefreshAuthentication(Resource):
    @ns_user.doc(security="jsonWebToken")
    @jwt_required(refresh=True)
    def post(self):
        # The post method of this end-point create an new acess_token for the authenticaded user

        identity = get_jwt_identity()

        user = get_user(identity)

        if not user:
            return {
                "user_id": None,
                "access_token": None,
                "refresh_token": None,
            }, 404

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        return {
            "user_id": user.id,
            "access_token": access_token, 
            "refresh_token": refresh_token,
        }

@ns_user.route("/privilege/<int:user_id>")
class UserPrivilege(Resource):
    @ns_user.expect(privilege_model)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def post(self, user_id):
        # The post method of this end-point set a privilege to the user

        privilege = ns_user.payload["privilege"].lower()
        conn = connect_to_postgres()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT privilege FROM userprivileges WHERE privilege = %s", 
                (privilege,)
            )
            if not cursor.fetchone():
                abort(404, "non-existing privilege")
        finally:
            conn.close()

        current_user_privileges = current_user.privileges()
        privileges_allowed = ["administrator", "manager"]
        if not any(item in privileges_allowed for item in current_user_privileges):
            abort(401, "the user does not have permission to set a privilege to another user")

        if privilege in privileges_allowed:
            if not "administrator" in current_user_privileges:
                abort(401, "the user does not have permission to set this privilege to another user")

        user = get_user(user_id)
        if not user:
            abort(404, "user not founded")
        
        if privilege in user.privileges():
            abort(401, "user already has this privilege")

        if not user.set_privilege(privilege):
            abort(500, "error when setting privilege")

        return {
            "id": user.id,
            "privileges": user.privileges(),
        }
    
    @ns_user.expect(privilege_model)
    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def delete(self, user_id):
        # The delete method of this end-point remove a privilege of the user

        privilege = ns_user.payload["privilege"].lower()
        conn = connect_to_postgres()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT privilege FROM userprivileges WHERE privilege = %s", 
                (privilege,)
            )
            if not cursor.fetchone():
                abort(404, "non-existing privilege")
        finally:
            conn.close()

        current_user_privileges = current_user.privileges()
        privileges_allowed = ["administrator", "manager"]
        if not any(item in privileges_allowed for item in current_user_privileges):
            abort(401, "the user does not have permission to delete a privilege of an user")

        if privilege == "manager":
            if not "administrator" in current_user_privileges:
                abort(401, "only an administrator can remove a manager privilege")

        if privilege == "administrator":
            if not "administrator" in current_user_privileges:
                abort(401, "only an administrator can remove the privilege of another")
            
            if user_id == current_user.id:
                abort(401, "an administrator can not remove the privilege of himself")

        user = get_user(user_id)
        if not user:
            abort(404, "user not founded")
        
        if privilege not in user.privileges():
            abort(401, "user do not have this privilege")

        if not user.delete_privilege(privilege):
            abort(500, "error when remove privilege")

        return {
            "id": user.id,
            "privileges": user.privileges(),
        }
                

    @ns_user.doc(security="jsonWebToken")
    @jwt_required()
    def get(self, user_id):
        # The get method of this end-point return the privilege of the user

        current_user_privileges = current_user.privileges()
        if user_id == current_user.id:
            return {
                "user_id": user_id,
                "privileges": current_user_privileges,
            }
        
        privileges_allowed = ["administrator", "manager"]
        if not any(item in privileges_allowed for item in current_user_privileges):
            abort(401, "the user does not have permission to access this informations")

        user = get_user(user_id)
        if not user:
            abort(404, "user not founded")

        return {
            "id": user.id,
            "privileges": user.privileges(),
        }

