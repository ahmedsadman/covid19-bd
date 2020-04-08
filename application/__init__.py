from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# globally accessible variables
db = SQLAlchemy()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    with app.app_context():
        from . import routes

        db.create_all()
        return app
