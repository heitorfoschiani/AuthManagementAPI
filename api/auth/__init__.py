from flask_jwt_extended import current_user
from flask_restx import abort
from functools import wraps


authorizations = {
    "jsonWebToken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}


def require_privileges(*required_privileges):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_privileges = current_user.privileges()
            
            if not any(privilege in current_user_privileges for privilege in required_privileges):
                abort(401, "Insufficient privileges")

            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator