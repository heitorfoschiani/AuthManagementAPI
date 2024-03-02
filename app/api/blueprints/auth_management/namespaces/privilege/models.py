from flask_restx import fields

from app.api.blueprints.auth_management import auth_management_api


privilege_model = auth_management_api.model("Privilege", {
    "privilege": fields.String(description="The user's privilege into the server", required=True),
})