from flask import Flask, Blueprint
from flask_restx import Api

from app.api.blueprints import add_blueprint
from .namespaces.user.resources import user_namespace
from .namespaces.privilege.resources import privilege_namespace
from . import auth_management_api, auth_management_blueprint


def register_auth_management_blueprint(app):
    namespaces = [user_namespace, privilege_namespace]

    add_blueprint(
        app=app, 
        api=auth_management_api, 
        blueprint=auth_management_blueprint, 
        namespaces=namespaces
    )