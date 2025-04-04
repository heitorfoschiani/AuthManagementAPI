from flask import Flask, Blueprint
from flask_restx import Api


def add_blueprint(app: Flask, api: Api, blueprint: Blueprint, namespaces: list):
    app.register_blueprint(blueprint)
    
    for namespace in namespaces:
        api.add_namespace(namespace)