import os


class BaseConfig:
    PROPAGATE_EXCEPTIONS = True
    PERMANENT_SESSION_LIFETIME = 3600
    SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FILE_UPLOAD_EXTENSIONS = [".xlsx", ".xls", ".xlsm", ".csv"]


class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SESSION_COOKIE_SECURE = False


class TestConfig(BaseConfig):
    pass


class ProdConfig(BaseConfig):
    pass


CONFIG = {"DEV": DevConfig(), "TEST": TestConfig(), "PROD": ProdConfig()}
