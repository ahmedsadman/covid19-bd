from datetime import datetime
from application import db
from application.models import BaseModel


class District(BaseModel):
    __tablename__ = "districts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    count = db.Column(db.Integer, default=0)
    updated_on = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, name, count):
        self.name = name
        self.count = count

    def serialize(self):
        return {"id": self.id, "name": self.name, "count": self.count}

    @classmethod
    def get_all(cls):
        return cls.query.all()
