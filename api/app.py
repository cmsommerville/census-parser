import os
from flask import Flask
from config import CONFIG

from extensions import init_extensions


def create_app():
    ENV = os.environ.get("ENV", "DEV")
    config = CONFIG.get(ENV)
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{app.root_path}/{os.getenv('DATABASE_NAME')}"
    )

    app, db, _, api = init_extensions(app)

    app.config.from_prefixed_env()

    with app.app_context():
        # bind routes
        from routes import NAMESPACES
        from utils import bind_namespaces

        bind_namespaces(api, NAMESPACES, "/api")

        db.metadata.reflect(bind=db.engine)
        db.create_all()

    print("Successfully started app...")
    return app
