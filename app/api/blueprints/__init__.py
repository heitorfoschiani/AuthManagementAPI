from flask import Flask, Blueprint
from flask_restx import Api

from .auth_management.user.resources import user_namespace
from .auth_management.privilege.resources import privilege_namespace


def register_auth_management(app: Flask, api: Api, blueprint: Blueprint):
    app.register_blueprint(blueprint)

    namespaces = [user_namespace, privilege_namespace]
    for namespace in namespaces:
        api.add_namespace(namespace)

    