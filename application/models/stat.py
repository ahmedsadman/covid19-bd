from application import db
from datetime import datetime
from application.models import BaseModel


class Stat(BaseModel):
    __tablename__ = "stats"
    id = db.Column(db.Integer, primary_key=True)
    positive_total = db.Column(db.Integer, default=0)
    positive_24 = db.Column(db.Integer, default=0)
    death_total = db.Column(db.Integer, default=0)
    death_24 = db.Column(db.Integer, default=0)
    recovered_total = db.Column(db.Integer, default=0)
    recovered_24 = db.Column(db.Integer, default=0)
    updated_on = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(
        self,
        positive_total=0,
        positive_24=0,
        death_total=0,
        death_24=0,
        recovered_total=0,
        recovered_24=0,
    ):
        self.positive_total = positive_total
        self.positive_24 = positive_24
        self.death_total = death_total
        self.death_24 = death_24
        self.recovered_total = recovered_total
        self.recovered_24 = recovered_24

    def serialize(self):
        return {
            "positive": {"total": self.positive_total, "last24": self.positive_24},
            "death": {"total": self.death_total, "last24": self.death_24},
            "recovered": {"total": self.recovered_total, "last24": self.recovered_24},
            "updated_on": self.updated_on,
        }

    @classmethod
    def get(cls):
        return cls.query.first()
