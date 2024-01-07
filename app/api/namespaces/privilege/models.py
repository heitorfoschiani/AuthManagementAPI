from flask_restx import fields

from app.api import api


privilege_model = api.model("Privilege", {
    "privilege": fields.String(description="The user's privilege into the server", required=True),
})