import importlib
import sys
import types
import os

import pytest


def load_user_management_module():
    # Create minimal stubs for external dependencies
    flask = types.ModuleType("flask")
    def abort(code, msg=None):
        raise Exception(f"abort {code}: {msg}")
    class Logger:
        def error(self, *args, **kwargs):
            pass
        def info(self, *args, **kwargs):
            pass
    flask.abort = abort
    flask.current_app = types.SimpleNamespace(logger=Logger())
    flask.request = types.SimpleNamespace(headers={}, data=None, get_json=lambda: None)
    sys.modules['flask'] = flask

    flask_restx = types.ModuleType("flask_restx")
    class Namespace:
        def __init__(self, name):
            self.name = name
            self.payload = None
        def route(self, path):
            def decorator(cls):
                return cls
            return decorator
        def doc(self, *a, **k):
            def decorator(f):
                return f
            return decorator
        def expect(self, *a, **k):
            def decorator(f):
                return f
            return decorator
        def marshal_with(self, *a, **k):
            def decorator(f):
                return f
            return decorator
    class Resource:
        pass
    class ReqParser:
        def add_argument(self, *a, **k):
            pass
        def parse_args(self):
            return {}
    flask_restx.Namespace = Namespace
    flask_restx.Resource = Resource
    flask_restx.reqparse = types.SimpleNamespace(RequestParser=lambda: ReqParser())
    flask_restx.fields = types.SimpleNamespace(Integer=lambda *a, **k: None, String=lambda *a, **k: None)
    sys.modules['flask_restx'] = flask_restx

    fjwt = types.ModuleType("flask_jwt_extended")
    def jwt_required(*a, **k):
        def wrapper(fn):
            return fn
        return wrapper
    fjwt.jwt_required = jwt_required
    fjwt.current_user = types.SimpleNamespace(id=1, privileges=lambda: [])
    fjwt.create_access_token = lambda identity=None: 'token'
    fjwt.create_refresh_token = lambda identity=None: 'token'
    sys.modules['flask_jwt_extended'] = fjwt

    decorators_stub = types.ModuleType("app.logs.decorators")
    def identity(f):
        return f
    decorators_stub.log_request_headers_information = identity
    decorators_stub.log_request_body_information = identity
    sys.modules['app.logs.decorators'] = decorators_stub

    auth_stub = types.ModuleType("app.auth")
    auth_stub.authorizations = {}
    sys.modules['app.auth'] = auth_stub

    blueprint_stub = types.ModuleType("app.api.blueprints.auth_management")
    class Api:
        def __init__(self, *a, **k):
            pass
        def model(self, name, fields):
            return {}
    blueprint_stub.auth_management_blueprint = None
    blueprint_stub.Api = Api
    blueprint_stub.auth_management_api = Api()
    sys.modules['app.api.blueprints.auth_management'] = blueprint_stub

    models_stub = types.ModuleType("app.api.blueprints.auth_management.namespaces.user.models")
    models_stub.user_model = {}
    models_stub.register_user_model = {}
    models_stub.edit_user_model = {}
    models_stub.authenticate_user_model = {}
    sys.modules['app.api.blueprints.auth_management.namespaces.user.models'] = models_stub

    parse_stub = types.ModuleType("app.api.blueprints.auth_management.namespaces.user.parse")
    parse_stub.user_id_parse = types.SimpleNamespace(parse_args=lambda: {})
    parse_stub.username_parse = types.SimpleNamespace(parse_args=lambda: {})
    sys.modules['app.api.blueprints.auth_management.namespaces.user.parse'] = parse_stub

    user_stub = types.ModuleType("app.api.blueprints.auth_management.namespaces.user")
    user_stub.__path__ = [os.path.join(os.path.dirname(__file__), '..', 'app', 'api', 'blueprints', 'auth_management', 'namespaces', 'user')]
    class User:
        def __init__(self, id=None, full_name='', username='', email='', phone=None):
            self.id = id
            self.full_name = full_name
            self.username = username
            self.email = email
            self.phone = phone
        def privileges(self):
            return []
        def username_exists(self):
            return False
        def email_exists(self):
            return False
        def update(self, data):
            for k, v in data.items():
                setattr(self, k, v)

    user_instance = User(id=1, full_name='test', username='old_username', email='mail', phone='111')
    def get_user(query):
        return user_instance
    User.get = staticmethod(get_user)
    user_stub.User = User
    sys.modules['app.api.blueprints.auth_management.namespaces.user'] = user_stub

    resources = importlib.import_module('app.api.blueprints.auth_management.namespaces.user.resources')
    return resources, User


@pytest.fixture
def resources_module():
    # ensure fresh import for each test
    modules_to_remove = [m for m in list(sys.modules) if m.startswith('app.api.blueprints.auth_management') or m in {'flask', 'flask_restx', 'flask_jwt_extended'}]
    for m in modules_to_remove:
        sys.modules.pop(m, None)
    resources, User = load_user_management_module()
    return resources, User


def test_put_updates_phone_not_username(resources_module):
    resources, User = resources_module

    # create a user instance that will be returned by User.get
    user = User.get({'user_id': 1})
    # patch current_user in jwt extension
    sys.modules['flask_jwt_extended'].current_user = user

    # set payload with phone update
    resources.user_namespace.payload = {"id": 1, "phone": "999"}

    # call underlying function bypassing decorators
    func = resources.UserManagement.put
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    result = func(resources.UserManagement())

    assert user.phone == "999"
    assert user.username == "old_username"
