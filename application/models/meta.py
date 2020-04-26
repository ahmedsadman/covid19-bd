from datetime import datetime
from application import db
from application.models import BaseModel


class Meta(BaseModel):
    __tablename__ = "meta"
    id = db.Column(db.Integer, primary_key=True)
    syncing_districts = db.Column(db.Boolean, default=False)
    syncing_stats = db.Column(db.Boolean, default=False)
    district_last_sync = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get(cls):
        return cls.query.first()

    @classmethod
    def create_meta(cls):
        meta = cls.get()
        if not meta:
            meta = cls()
            meta.save()

    @classmethod
    def set_district_syncing(cls, state):
        meta = cls.get()
        meta.syncing_districts = state
        meta.save()

    @classmethod
    def set_stats_syncing(cls, state):
        meta = cls.get()
        meta.syncing_stats = state
        meta.save()

    @classmethod
    def is_district_syncing(cls):
        meta = cls.get()
        return meta.syncing_districts

    @classmethod
    def is_stats_syncing(cls):
        meta = cls.get()
        return meta.syncing_stats

    @classmethod
    def set_last_district_sync(cls):
        meta = cls.get()
        meta.district_last_sync = datetime.utcnow()
        meta.save()

    @classmethod
    def get_last_district_sync(cls):
        meta = cls.get()
        return meta.district_last_sync
