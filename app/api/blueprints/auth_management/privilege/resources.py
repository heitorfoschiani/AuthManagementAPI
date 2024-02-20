from flask import abort, current_app
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, current_user

from app.auth import require_privileges
from app.logs import log_request_headers_information, log_request_body_information
from app.api.blueprints.auth_management.user import User
from app.api.blueprints.auth_management.privilege import Privilege
from .models import privilege_model


privilege_namespace = Namespace(
    "privilege", 
)


@privilege_namespace.route("/privileges")
class PrivilegeManagement(Resource):
    @privilege_namespace.doc(
        description="""
            The get method of this end-point returns the privilege types existent into the server and their username owners
        """,
        responses={
            200: "Data returned successfully", 
            403: "Forbidden - User does not have the necessary privileges", 
            500: "Internal server error"
        },
        security="jsonWebToken"
    )
    @jwt_required()
    @require_privileges("administrator", "manager")
    @log_request_headers_information
    @log_request_body_information
    def get(self):
        try:
            dict_user_privileges = Privilege.get_user_privileges()
        except Exception as e:
            current_app.logger.error(f"An error occurred when get userprivilege: {e}")
            abort(500, "An error occurred when get userprivilege")

        return dict_user_privileges


@privilege_namespace.route("/user-privilege/<int:user_id>")
@privilege_namespace.doc(params={"user_id": "The user id into the server."})
class UserPrivilege(Resource):
    @privilege_namespace.doc(
        description="""
            The post method of this end-point set a privilege to the user.
            Only users with 'administrator' or 'manager' privileges can set a privilege to another user.
            Only users with 'administrator' privilege can set a 'administrator' or 'manager' privileges.
            This end-point can't be used for inactivate an user. Use '/user' in delete method instead.
        """,
        responses={
            200: "Privilege assigned to user successfully", 
            403: "Forbidden - User does not have the necessary privileges", 
            404: "Information sent was not founded", 
            405: "Enable to use this end-point for this purpose", 
            409: "User already has this privilege", 
            500: "Internal server error"
        },
        security="jsonWebToken"
    )
    @privilege_namespace.expect(privilege_model)
    @jwt_required()
    @require_privileges("administrator", "manager")
    @log_request_headers_information
    @log_request_body_information
    def post(self, user_id):
        js_data = privilege_namespace.payload

        privilege_name = js_data["privilege"].lower()
        try:
            privilege = Privilege.get_privilege(privilege_name)
        except Exception as e:
            current_app.logger.error(f"An error occorred when get '{privilege_name}' privilege: {e}")
            abort(500, f"An error occorred when get '{privilege_name}' privilege")

        if not privilege:
            current_app.logger.error("Non-existing privilege")
            abort(404, "Non-existing privilege")

        if privilege_name in ["administrator", "manager"]:
            if not "administrator" in current_user.privileges():
                current_app.logger.error("Insufficient privileges to set this privilege to another user")
                abort(403, "Insufficient privileges to set this privilege to another user")

        if privilege_name == "inactive":
            current_app.logger.error("Enable to inactivate an user using this end-point")
            abort(405, "Enable to inactivate an user using this end-point")

        user_information = {
            "user_id": user_id
        }
        user = User.get(user_information)
        if not user:
            current_app.logger.error(f"User not founded")
            abort(404, "User not founded")
        
        if privilege_name in user.privileges():
            current_app.logger.error(f"User already has this privilege")
            abort(409, "User already has this privilege")

        try:
            user.set_privilege(privilege_name)
        except Exception as e:
            current_app.logger.error(f"An error occurred when setting privilege: {e}")
            abort(500, "An error occurred when setting privilege")

        user_privileges = {
            "id": user.id,
            "privileges": user.privileges(),
        }

        return user_privileges
    
    @privilege_namespace.doc(
        description="""
            The delete method of this end-point remove a privilege of an user
            Only users with 'administrator' or 'manager' privileges might remove a privilege of a user.
            Only an administrator can remove a manager privilege.
            Only an administrator can remove the privilege of another.
            This end-point can't be used for inactivate an user. Use '/user' in delete method instead.
        """, 
        responses={
            200: "Privilege removed successfully", 
            403: "Forbidden - User does not have the necessary privileges", 
            404: "Information sent was not founded", 
            405: "Enable to use this end-point for this purpose", 
            500: "Internal server error"
        }, 
        security="jsonWebToken"
    )
    @privilege_namespace.expect(privilege_model)
    @jwt_required()
    @require_privileges("administrator", "manager")
    @log_request_headers_information
    @log_request_body_information
    def delete(self, user_id):
        privilege_name = privilege_namespace.payload.get("privilege").lower()
        privilege = Privilege.get_privilege(privilege_name)
        if not privilege:
            current_app.logger.error(f"Non-existing privilege")
            abort(404, "Non-existing privilege")

        current_user_privileges = current_user.privileges()

        if privilege_name == "inactive":
            current_app.logger.error(f"Enable to inactivate an user using this end-point")
            abort(405, "Enable to inactivate an user using this end-point")

        if privilege_name == "manager":
            if not "administrator" in current_user_privileges:
                current_app.logger.error("Insufficient privileges to remove a manager privilege")
                abort(403, "Insufficient privileges to remove a manager privilege")

        if privilege_name == "administrator":
            if not "administrator" in current_user_privileges:
                current_app.logger.error("Insufficient privileges to remove the privilege of another")
                abort(403, "Insufficient privileges to remove the 'administrator' privilege of another")
            
            if user_id == current_user.id:
                current_app.logger.error("An administrator can not remove the privilege of himself")
                abort(403, "An administrator can not remove the privilege of himself")

        user = User.get({
            "user_id": user_id
        })

        if not user:
            current_app.logger.error(f"User not founded")
            abort(404, "User not founded")
        
        if privilege_name not in user.privileges():
            current_app.logger.error(f"User do not have this privilege")
            abort(404, "User do not have this privilege")

        try:
            user.delete_privilege(privilege_name)
        except Exception as e:
            current_app.logger.error(f"An error occurred when remove privilege: {e}")
            abort(500, "An error occurred when remove privilege")

        user_privileges = {
            "id": user.id,
            "privileges": user.privileges(),
        }

        return user_privileges
                
    @privilege_namespace.doc(
        description="""
            The get method of this end-point returns the privileges of an user.
        """,
        responses={
            200: "Privilege of the user returned successfully", 
            403: "Forbidden - User does not have the necessary privileges", 
            404: "Information sent was not founded", 
            500: "Internal server error"
        },
        security="jsonWebToken"
    )
    @jwt_required()
    @require_privileges("administrator", "manager")
    @log_request_headers_information
    @log_request_body_information
    def get(self, user_id):
        if user_id == current_user.id:
            current_user_privileges = current_user.privileges()
            user_information = {
                "user_id": user_id,
                "privileges": current_user_privileges,
            }
            return user_information
        
        user = User.get({
            "user_id": user_id
        })

        if not user:
            current_app.logger.error("User not founded")
            abort(404, "User not founded")

        user_privileges = {
            "id": user.id,
            "privileges": user.privileges(),
        }

        return user_privileges
    