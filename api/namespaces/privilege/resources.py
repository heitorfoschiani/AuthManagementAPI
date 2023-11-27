from flask import abort, current_app
from flask_jwt_extended import jwt_required, current_user
from flask_restx import Namespace, Resource

from database.dbconnection import connect_to_postgres
from api.auth import require_privileges
from api.namespaces.privilege.objects import Privilege
from api.namespaces.privilege.models import privilege_model
from api.namespaces.user.objects import User


ns_privilege = Namespace(
    "privilege", 
)

@ns_privilege.route("/privileges")
class PrivilegeManagement(Resource):
    @ns_privilege.doc(security="jsonWebToken")
    @jwt_required()
    @require_privileges("administrator", "manager")
    def get(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        cursor.execute("SELECT privilege FROM userprivileges;")
        server_privileges = cursor.fetchone()

        cursor.execute("""
            SELECT 
                userprivileges.privilege,
                users.id as user_id,
                usernames.username
            FROM useraccess
            INNER JOIN users on users.id = useraccess.user_id
            INNER JOIN usernames ON usernames.user_id = useraccess.user_id
            INNER JOIN userprivileges ON userprivileges.id = useraccess.privilege_id
            INNER JOIN fkstatus ON fkstatus.id = useraccess.status_id
            WHERE
                useraccess.status_id = (SELECT id FROM fkstatus WHERE status = 'valid');
        """)
        user_privileges = cursor.fetchall()
        conn.close()

        dict_user_privileges = {}
        privileges_checked = []
        for row in user_privileges:
            privilege = row[0]
            if privilege not in privileges_checked:
                privileges_checked.append(privilege)
                dict_user_privileges[privilege] = {}

        print(privileges_checked)

@ns_privilege.route("/user-privilege/<int:user_id>")
class UserPrivilege(Resource):
    @ns_privilege.expect(privilege_model)
    @ns_privilege.doc(security="jsonWebToken")
    @jwt_required()
    @require_privileges("administrator", "manager")
    def post(self, user_id):
        # The post method of this end-point set a privilege to the user

        privilege_name = ns_privilege.payload.get("privilege").lower()
        privilege = Privilege.get_privilege(privilege_name)
        if not privilege:
            abort(404, "non-existing privilege")

        if privilege_name == "inactive":
            abort(401, "aneble to inactivate an user using this end-point")

        if privilege_name in ["administrator", "manager"]:
            if not "administrator" in current_user.privileges():
                abort(401, "the user does not have permission to set this privilege to another user")

        user_information = {
            "user_id": user_id
        }
        user = User.get(user_information)
        if not user:
            abort(404, "user not founded")
        
        if privilege_name in user.privileges():
            abort(401, "user already has this privilege")

        if not user.set_privilege(privilege_name):
            abort(500, "error when setting privilege")

        return {
            "id": user.id,
            "privileges": user.privileges(),
        }
    
    @ns_privilege.expect(privilege_model)
    @ns_privilege.doc(security="jsonWebToken")
    @jwt_required()
    @require_privileges("administrator", "manager")
    def delete(self, user_id):
        # The delete method of this end-point remove a privilege of the user

        privilege_name = ns_privilege.payload.get("privilege").lower()
        privilege = Privilege.get_privilege(privilege_name)
        if not privilege:
            abort(404, "non-existing privilege")

        current_user_privileges = current_user.privileges()

        if privilege_name == "basic":
            abort(401, "aneble to inactivate an user using this end-point")

        if privilege_name == "manager":
            if not "administrator" in current_user_privileges:
                abort(401, "only an administrator can remove a manager privilege")

        if privilege_name == "administrator":
            if not "administrator" in current_user_privileges:
                abort(401, "only an administrator can remove the privilege of another")
            
            if user_id == current_user.id:
                abort(401, "an administrator can not remove the privilege of himself")

        user_information = {
            "user_id": user_id
        }
        user = User.get(user_information)
        if not user:
            abort(404, "user not founded")
        
        if privilege_name not in user.privileges():
            abort(401, "user do not have this privilege")

        if not user.delete_privilege(privilege_name):
            abort(500, "error when remove privilege")

        return {
            "id": user.id,
            "privileges": user.privileges(),
        }
                

    @ns_privilege.doc(security="jsonWebToken")
    @jwt_required()
    @require_privileges("administrator", "manager")
    def get(self, user_id):
        # The get method of this end-point return the privilege of the user

        current_user_privileges = current_user.privileges()
        if user_id == current_user.id:
            return {
                "user_id": user_id,
                "privileges": current_user_privileges,
            }
        
        user_information = {
            "user_id": user_id
        }
        user = User.get(user_information)
        if not user:
            abort(404, "user not founded")

        return {
            "id": user.id,
            "privileges": user.privileges(),
        }