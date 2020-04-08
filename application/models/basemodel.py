from application import db


class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        """save the item to database"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(e)

    def delete(self):
        """delete the item from database"""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            print(e)
