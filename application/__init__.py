from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from application.logger import Logger

# globally accessible variables
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    cors.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.before_first_request
    def run_update():
        # try to sync data
        sync_district_data()
        sync_stats()

    with app.app_context():
        from . import routes
        from application.models import Meta
        from application.tasks import sync_district_data, sync_stats

        db.create_all()

        # create meta
        Meta.create_meta()

        return app
