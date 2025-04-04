from datetime import timedelta


class Config:
    JWT_SECRET_KEY = "default-secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=6)