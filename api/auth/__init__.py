from flask_jwt_extended import current_user
from flask_restx import abort, reqparse
from functools import wraps


authorizations = {
    "jsonWebToken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

def require_privileges(allowed_privileges):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Parsing user_id from the request
            parser = reqparse.RequestParser()
            parser.add_argument('user_id', type=int, location='args')
            args = parser.parse_args()
            user_id = args.get('user_id')

            has_privilege = any(privilege in current_user.privileges() for privilege in allowed_privileges)

            # Check if user is trying to access their own information
            if not (has_privilege or (user_id and user_id == current_user.id)):
                abort(401, "Insufficient privileges")

            return f(*args, **kwargs)

        return decorated_function

    return decorator
