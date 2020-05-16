from application.logger import Logger
from application import db


class BaseModel(db.Model):
    __abstract__ = True
    logger = Logger.create_logger(__name__)

    def save(self):
        """save the item to database"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Error while saving to database: {e}")

    def delete(self):
        """delete the item from database"""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Error while deleting from database: {e}")
