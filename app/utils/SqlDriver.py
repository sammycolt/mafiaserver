from app.models.db_models import *

class SqlDriver():
    @staticmethod
    def getUsersByIds(ids):
        return db.session.query(User).filter(User.id.in_(ids)).all()
