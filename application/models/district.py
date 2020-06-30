from datetime import datetime
from sqlalchemy import desc
from application import db
from application.models import BaseModel


class District(BaseModel):
    __tablename__ = "districts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    count = db.Column(db.Integer, default=0)
    prev_count = db.Column(db.Integer, default=0)
    last_update = db.Column(db.DateTime, nullable=True)

    def __init__(self, name, count, last_update):
        self.name = name
        self.count = count
        self.prev_count = count
        self.last_update = last_update

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "count": self.count,
            "prev_count": self.prev_count,
        }

    @classmethod
    def get_all(cls):
        return cls.query.order_by(desc(cls.count)).all()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
