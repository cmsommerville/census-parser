from flask import Flask
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restx import Api


db = SQLAlchemy()  # , engine_options={"fast_executemany": True})
ma = Marshmallow()
api = Api(doc="/api/doc/")


def init_extensions(app: Flask):
    db.init_app(app)
    ma.init_app(app)
    app.config["SESSION_SQLALCHEMY"] = db

    api.init_app(app)

    return app, db, ma, api
