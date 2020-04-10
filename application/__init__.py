from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS

# globally accessible variables
db = SQLAlchemy()
cors = CORS()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    cors.init_app(app)
    db.init_app(app)
    app.scheduler = BackgroundScheduler()

    with app.app_context():
        from . import routes
        from application.models import Meta

        app.scheduler.start()
        db.create_all()

        # create meta
        Meta.create_meta()

        return app
