# Importing libraries
from flask_restx import Api

api = Api(
    version='1.0',
    title='API Authentication Menagement',
    description='A secure Flask API that requires user authentication and manages access',
)