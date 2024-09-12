from flask import Flask
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


db = SQLAlchemy()  # , engine_options={"fast_executemany": True})
ma = Marshmallow()
limiter = Limiter(
    get_remote_address,
    default_limits=["20 per second"],
    storage_uri="memory://",
)

api = Api(doc="/api/doc/")


def init_extensions(app: Flask):
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    app.config["SESSION_SQLALCHEMY"] = db

    api.init_app(app)

    return app, db, ma, api
