from datetime import datetime
from application import db
from application.models import BaseModel


class Meta(BaseModel):
    __tablename__ = "meta"
    name = db.Column(db.String(30), primary_key=True)
    value = db.Column(db.String(50), nullable=True)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    @classmethod
    def get_meta(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def create_meta(cls):
        meta_list = ["updating", "updated_on"]
        for meta in meta_list:
            found = cls.get_meta(meta)
            if not found:
                new_meta = Meta(meta, "")
                new_meta.save()

    @classmethod
    def set_updating(cls, state):
        meta_update = cls.get_meta("updating")
        meta_update.value = state
        meta_update.save()

    @classmethod
    def is_updating(cls):
        meta = cls.query.filter_by(name="updating").first()
        return meta.value == "True"

    @classmethod
    def set_last_updated(cls):
        meta = cls.query.filter_by(name="updated_on").first()
        meta.value = str(datetime.utcnow())
        meta.save()
