from flask import current_app as app
from application import db


class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        """save the item to database"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error while saving to database: {e}")

    def delete(self):
        """delete the item from database"""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error while deleting from database: {e}")
